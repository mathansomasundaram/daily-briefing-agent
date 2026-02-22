"""
Deduplication manager.
Tracks sent articles to prevent duplicates.
Includes both URL-based and content similarity-based deduplication.
"""

import json
from typing import List, Dict, Set
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    import faiss
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


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
SENT_ARTICLES_PATH = PROJECT_ROOT / "data" / "sent_articles.json"


class DeduplicationManager:
    """
    Manages article deduplication by tracking previously sent URLs
    and detecting content similarity using embeddings.
    """

    def __init__(self, similarity_threshold: float = None, enable_content_dedup: bool = None):
        """
        Initialize the deduplication manager.

        Args:
            similarity_threshold (float): Cosine similarity threshold (0.0-1.0) for considering articles as duplicates
            enable_content_dedup (bool): Whether to enable content-based deduplication
        """
        self.logger = logger
        self.sent_urls = self._load_sent_articles()
        self.similarity_threshold = similarity_threshold if similarity_threshold is not None else SIMILARITY_THRESHOLD

        # Use config value if not explicitly provided
        if enable_content_dedup is None:
            enable_content_dedup = ENABLE_CONTENT_DEDUPLICATION

        self.enable_content_dedup = enable_content_dedup and EMBEDDINGS_AVAILABLE

        # Initialize embedding model if available
        if self.enable_content_dedup:
            try:
                self.logger.info(f"Loading sentence-transformers model '{EMBEDDING_MODEL}' for content deduplication...")
                self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
                self.logger.info(f"Sentence-transformers model loaded successfully (similarity threshold: {self.similarity_threshold})")
            except Exception as e:
                self.logger.warning(f"Failed to load embedding model: {e}. Content deduplication disabled.")
                self.enable_content_dedup = False
        else:
            self.embedding_model = None
            if not EMBEDDINGS_AVAILABLE:
                self.logger.warning("sentence-transformers or faiss not installed. Content deduplication disabled.")

    def _load_sent_articles(self) -> Set[str]:
        """
        Load sent article URLs from JSON file.

        Returns:
            Set[str]: Set of previously sent URLs
        """
        if not SENT_ARTICLES_PATH.exists() or SENT_ARTICLES_PATH.stat().st_size == 0:
            self.logger.warning(f"Sent articles file not found or empty: {SENT_ARTICLES_PATH}")
            # Create parent directory if it doesn't exist
            SENT_ARTICLES_PATH.parent.mkdir(parents=True, exist_ok=True)
            return set()

        try:
            with open(SENT_ARTICLES_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)

            urls = {entry["url"] for entry in data.get("sent_urls", [])}
            self.logger.info(f"Loaded {len(urls)} previously sent article URLs")
            return urls

        except Exception as e:
            self.logger.error(f"Error loading sent articles: {e}", exc_info=True)
            return set()

    def is_duplicate(self, url: str) -> bool:
        """
        Check if an article URL was already sent.

        Args:
            url (str): Article URL to check

        Returns:
            bool: True if URL was already sent, False otherwise
        """
        return url in self.sent_urls

    def _compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts using embeddings.

        Args:
            text1 (str): First text
            text2 (str): Second text

        Returns:
            float: Cosine similarity (0.0-1.0)
        """
        if not self.enable_content_dedup or not self.embedding_model:
            return 0.0

        try:
            # Generate embeddings
            embeddings = self.embedding_model.encode([text1, text2])

            # Compute cosine similarity
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )

            return float(similarity)
        except Exception as e:
            self.logger.warning(f"Error computing similarity: {e}")
            return 0.0

    def _is_content_similar(self, article: Dict, existing_articles: List[Dict]) -> bool:
        """
        Check if article content is similar to any existing articles.

        Args:
            article (Dict): Article to check
            existing_articles (List[Dict]): List of articles to compare against

        Returns:
            bool: True if similar content found, False otherwise
        """
        if not self.enable_content_dedup or not existing_articles:
            return False

        # Combine title and summary for better matching
        article_text = f"{article.get('title', '')} {article.get('summary', '')}"

        for existing in existing_articles:
            existing_text = f"{existing.get('title', '')} {existing.get('summary', '')}"

            similarity = self._compute_similarity(article_text, existing_text)

            if similarity >= self.similarity_threshold:
                self.logger.info(
                    f"Similar content detected (similarity: {similarity:.2f}): "
                    f"'{article.get('title', '')[:50]}...' vs '{existing.get('title', '')[:50]}...'"
                )
                return True

        return False

    def filter_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """
        Filter out articles that were already sent OR that are duplicates within the current batch.
        Uses both URL-based and content similarity-based deduplication.

        Args:
            articles (List[Dict]): List of articles with 'url' field

        Returns:
            List[Dict]: Filtered articles (duplicates removed)
        """
        original_count = len(articles)
        seen_urls = set()
        filtered = []
        url_duplicates = 0
        content_duplicates = 0

        for article in articles:
            url = article.get("url", "")

            # Skip if URL already sent or already seen in this batch
            if self.is_duplicate(url) or url in seen_urls:
                url_duplicates += 1
                continue

            # Check content similarity with already filtered articles
            if self.enable_content_dedup and self._is_content_similar(article, filtered):
                content_duplicates += 1
                continue

            # Article is unique, add it
            filtered.append(article)
            seen_urls.add(url)

        removed_count = original_count - len(filtered)
        if removed_count > 0:
            self.logger.info(
                f"Filtered out {removed_count} duplicate articles: "
                f"{url_duplicates} URL duplicates, {content_duplicates} content duplicates "
                f"({len(filtered)} unique articles remaining)"
            )

        return filtered

    def mark_as_sent(self, urls: List[str]) -> bool:
        """
        Mark URLs as sent by adding them to the tracking file.

        Args:
            urls (List[str]): List of URLs to mark as sent

        Returns:
            bool: True if successful, False otherwise
        """
        if not urls:
            return True

        try:
            # Load current data
            if SENT_ARTICLES_PATH.exists() and SENT_ARTICLES_PATH.stat().st_size > 0:
                with open(SENT_ARTICLES_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                # Create parent directory if it doesn't exist
                SENT_ARTICLES_PATH.parent.mkdir(parents=True, exist_ok=True)
                data = {"sent_urls": []}

            # Add new URLs with timestamp
            current_time = get_current_timestamp()
            for url in urls:
                if url not in self.sent_urls:
                    data["sent_urls"].append({
                        "url": url,
                        "sent_at": current_time
                    })
                    self.sent_urls.add(url)

            # Save back to file
            with open(SENT_ARTICLES_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Marked {len(urls)} articles as sent")
            return True

        except Exception as e:
            self.logger.error(f"Error marking articles as sent: {e}", exc_info=True)
            return False

    def cleanup_old_entries(self, days: int = 30) -> int:
        """
        Remove entries older than N days to prevent file bloat.

        Args:
            days (int): Remove entries older than this many days (default: 30)

        Returns:
            int: Number of entries removed
        """
        try:
            if not SENT_ARTICLES_PATH.exists() or SENT_ARTICLES_PATH.stat().st_size == 0:
                return 0

            with open(SENT_ARTICLES_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)

            sent_urls = data.get("sent_urls", [])
            original_count = len(sent_urls)

            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=days)

            # Filter out old entries
            filtered_urls = []
            for entry in sent_urls:
                sent_at = parse_timestamp(entry.get("sent_at", ""))
                if sent_at and sent_at.replace(tzinfo=None) >= cutoff_date:
                    filtered_urls.append(entry)

            # Update data
            data["sent_urls"] = filtered_urls

            # Save back
            with open(SENT_ARTICLES_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Reload in memory
            self.sent_urls = {entry["url"] for entry in filtered_urls}

            removed_count = original_count - len(filtered_urls)
            self.logger.info(f"Cleaned up {removed_count} old entries (older than {days} days)")

            return removed_count

        except Exception as e:
            self.logger.error(f"Error cleaning up old entries: {e}", exc_info=True)
            return 0

    def get_stats(self) -> Dict:
        """
        Get statistics about sent articles.

        Returns:
            Dict: Statistics (total_sent, etc.)
        """
        return {
            "total_sent": len(self.sent_urls)
        }
