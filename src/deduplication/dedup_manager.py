"""
Optimized deduplication manager with batch processing.
"""

import json
from typing import List, Dict, Set, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

from utils.logger import setup_logger
from utils.date_utils import parse_timestamp, get_current_timestamp
from src.deduplication.config import (
    ENABLE_CONTENT_DEDUPLICATION,
    SIMILARITY_THRESHOLD,
    EMBEDDING_MODEL
)
from src.exceptions import DeduplicationError

logger = setup_logger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
SENT_ARTICLES_PATH = PROJECT_ROOT / "data" / "sent_articles.json"


class DeduplicationManager:
    """Manages article deduplication using URL tracking and content similarity."""

    def __init__(
        self,
        similarity_threshold: Optional[float] = None,
        enable_content_dedup: Optional[bool] = None
    ):
        """
        Initialize deduplication manager.

        Args:
            similarity_threshold: Cosine similarity threshold (0.0-1.0)
            enable_content_dedup: Whether to enable content-based deduplication
        """
        self.logger = logger
        self.sent_urls = self._load_sent_articles()
        self.similarity_threshold = (
            similarity_threshold if similarity_threshold is not None
            else SIMILARITY_THRESHOLD
        )

        enable_content = (
            enable_content_dedup if enable_content_dedup is not None
            else ENABLE_CONTENT_DEDUPLICATION
        )
        self.enable_content_dedup = enable_content and EMBEDDINGS_AVAILABLE

        self.embedding_model = None
        if self.enable_content_dedup:
            self._initialize_embedding_model()

    def _initialize_embedding_model(self) -> None:
        """Initialize the sentence transformer model."""
        try:
            self.logger.info(
                "Loading sentence-transformers model '%s' for content deduplication...",
                EMBEDDING_MODEL
            )
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
            self.logger.info(
                "Model loaded successfully (threshold: %.2f)",
                self.similarity_threshold
            )
        except Exception as e:
            self.logger.warning(
                "Failed to load embedding model: %s. Content deduplication disabled.",
                str(e)
            )
            self.enable_content_dedup = False

    def _load_sent_articles(self) -> Set[str]:
        """Load previously sent article URLs from JSON file."""
        if not SENT_ARTICLES_PATH.exists() or SENT_ARTICLES_PATH.stat().st_size == 0:
            self.logger.warning(
                "Sent articles file not found or empty: %s",
                SENT_ARTICLES_PATH
            )
            SENT_ARTICLES_PATH.parent.mkdir(parents=True, exist_ok=True)
            return set()

        try:
            with open(SENT_ARTICLES_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            urls = {entry["url"] for entry in data.get("sent_urls", [])}
            self.logger.info("Loaded %d previously sent article URLs", len(urls))
            return urls
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.error("Error loading sent articles: %s", str(e), exc_info=True)
            return set()

    def is_duplicate(self, url: str) -> bool:
        """Check if article URL was already sent."""
        return url in self.sent_urls

    def _get_article_text(self, article: Dict) -> str:
        """Extract combined text from article for embedding."""
        title = article.get('title', '')
        summary = article.get('summary', '')
        return f"{title} {summary}".strip()

    def _find_content_duplicates_batch(
        self,
        articles: List[Dict]
    ) -> List[Tuple[int, int, float]]:
        """
        Find content duplicates using batch embedding computation.

        Args:
            articles: List of articles to check

        Returns:
            List of tuples (article_idx, duplicate_idx, similarity_score)
        """
        if not self.enable_content_dedup or not articles:
            return []

        try:
            # Extract text from all articles
            texts = [self._get_article_text(article) for article in articles]

            # Compute all embeddings in one batch (much faster)
            embeddings = self.embedding_model.encode(texts, show_progress_bar=False)

            # Compute pairwise similarity matrix
            similarity_matrix = cosine_similarity(embeddings)

            # Find duplicate pairs above threshold
            duplicates = []
            for i in range(len(articles)):
                for j in range(i + 1, len(articles)):
                    similarity = similarity_matrix[i][j]
                    if similarity >= self.similarity_threshold:
                        duplicates.append((i, j, float(similarity)))

            return duplicates

        except Exception as e:
            self.logger.warning("Error in batch similarity computation: %s", str(e))
            return []

    def filter_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """
        Filter duplicates using URL matching and content similarity.

        Args:
            articles: List of articles with 'url' field

        Returns:
            Filtered list with duplicates removed
        """
        original_count = len(articles)

        # Step 1: Remove URL duplicates
        seen_urls = set()
        url_filtered = []
        url_duplicates = 0

        for article in articles:
            url = article.get("url", "")
            if not self.is_duplicate(url) and url not in seen_urls:
                url_filtered.append(article)
                seen_urls.add(url)
            else:
                url_duplicates += 1

        # Step 2: Remove content duplicates (batch processing)
        if self.enable_content_dedup and url_filtered:
            duplicate_pairs = self._find_content_duplicates_batch(url_filtered)

            # Build set of indices to remove (keep first occurrence)
            indices_to_remove = set()
            for i, j, similarity in duplicate_pairs:
                indices_to_remove.add(j)  # Remove second occurrence
                self.logger.info(
                    "Similar content detected (%.2f): '%s...' vs '%s...'",
                    similarity,
                    url_filtered[i].get('title', '')[:50],
                    url_filtered[j].get('title', '')[:50]
                )

            # Keep only non-duplicate articles
            content_filtered = [
                article for idx, article in enumerate(url_filtered)
                if idx not in indices_to_remove
            ]
            content_duplicates = len(url_filtered) - len(content_filtered)
        else:
            content_filtered = url_filtered
            content_duplicates = 0

        removed_count = original_count - len(content_filtered)
        if removed_count > 0:
            self.logger.info(
                "Filtered out %d duplicates: %d URL, %d content (%d unique remaining)",
                removed_count,
                url_duplicates,
                content_duplicates,
                len(content_filtered)
            )

        return content_filtered

    def mark_as_sent(self, urls: List[str]) -> None:
        """
        Mark URLs as sent.

        Args:
            urls: List of URLs to mark

        Raises:
            DeduplicationError: If marking fails
        """
        if not urls:
            return

        try:
            data = self._load_data_for_update()
            current_time = get_current_timestamp()

            for url in urls:
                if url not in self.sent_urls:
                    data["sent_urls"].append({
                        "url": url,
                        "sent_at": current_time
                    })
                    self.sent_urls.add(url)

            self._save_data(data)
            self.logger.info("Marked %d articles as sent", len(urls))

        except Exception as e:
            raise DeduplicationError(f"Failed to mark articles as sent: {e}") from e

    def _load_data_for_update(self) -> Dict:
        """Load current data for updating."""
        if SENT_ARTICLES_PATH.exists() and SENT_ARTICLES_PATH.stat().st_size > 0:
            try:
                with open(SENT_ARTICLES_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                self.logger.warning("Corrupted data file, creating new one")

        SENT_ARTICLES_PATH.parent.mkdir(parents=True, exist_ok=True)
        return {"sent_urls": []}

    def _save_data(self, data: Dict) -> None:
        """Save data to file."""
        with open(SENT_ARTICLES_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def cleanup_old_entries(self, days: int = 30) -> int:
        """
        Remove entries older than N days.

        Args:
            days: Remove entries older than this many days

        Returns:
            Number of entries removed

        Raises:
            DeduplicationError: If cleanup fails
        """
        try:
            if not SENT_ARTICLES_PATH.exists() or SENT_ARTICLES_PATH.stat().st_size == 0:
                return 0

            with open(SENT_ARTICLES_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)

            sent_urls = data.get("sent_urls", [])
            original_count = len(sent_urls)

            cutoff_date = datetime.now() - timedelta(days=days)

            filtered_urls = [
                entry for entry in sent_urls
                if (sent_at := parse_timestamp(entry.get("sent_at", "")))
                and sent_at.replace(tzinfo=None) >= cutoff_date
            ]

            data["sent_urls"] = filtered_urls
            self._save_data(data)

            self.sent_urls = {entry["url"] for entry in filtered_urls}
            removed_count = original_count - len(filtered_urls)

            self.logger.info(
                "Cleaned up %d old entries (older than %d days)",
                removed_count,
                days
            )
            return removed_count

        except Exception as e:
            raise DeduplicationError(f"Failed to cleanup old entries: {e}") from e

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about sent articles."""
        return {"total_sent": len(self.sent_urls)}
