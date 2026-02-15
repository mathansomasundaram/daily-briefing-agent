"""
Deduplication manager.
Tracks sent articles to prevent duplicates.
"""

import json
from typing import List, Dict, Set
from pathlib import Path
from datetime import datetime, timedelta

from utils.logger import setup_logger
from utils.date_utils import parse_timestamp, get_current_timestamp

logger = setup_logger(__name__)


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
SENT_ARTICLES_PATH = PROJECT_ROOT / "data" / "sent_articles.json"


class DeduplicationManager:
    """
    Manages article deduplication by tracking previously sent URLs.
    """

    def __init__(self):
        self.logger = logger
        self.sent_urls = self._load_sent_articles()

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

    def filter_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """
        Filter out articles that were already sent OR that are duplicates within the current batch.

        Args:
            articles (List[Dict]): List of articles with 'url' field

        Returns:
            List[Dict]: Filtered articles (duplicates removed)
        """
        original_count = len(articles)
        seen_urls = set()
        filtered = []

        for article in articles:
            url = article.get("url", "")
            # Skip if already sent or already seen in this batch
            if not self.is_duplicate(url) and url not in seen_urls:
                filtered.append(article)
                seen_urls.add(url)

        removed_count = original_count - len(filtered)
        if removed_count > 0:
            self.logger.info(
                f"Filtered out {removed_count} duplicate articles "
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
