"""
Article normalization module.
Converts articles from various sources into a unified schema.
"""

from typing import Dict, List, Optional
from datetime import datetime
from utils.date_utils import parse_timestamp, get_current_timestamp
from utils.logger import setup_logger

logger = setup_logger(__name__)


# Unified Article Schema
ARTICLE_SCHEMA = {
    "title": str,           # Article headline
    "summary": str,         # 2-3 sentence summary
    "source": str,          # Source name (Reuters, TechCrunch, etc.)
    "published_at": str,    # ISO format datetime
    "category": str,        # Topic category
    "url": str,             # Original article URL
    "importance_score": 0   # Initially 0, populated by ranker
}


class ArticleNormalizer:
    """
    Normalizes articles from various sources into a unified schema.
    """

    def __init__(self):
        self.logger = logger

    def normalize_rss_article(self, raw_article: Dict, category: str = "unknown") -> Optional[Dict]:
        """
        Convert RSS feed entry to unified article schema.

        Args:
            raw_article (Dict): Raw RSS entry from feedparser
            category (str): Topic category for this article

        Returns:
            Optional[Dict]: Normalized article or None if required fields missing
        """
        try:
            # Extract title
            title = raw_article.get("title", "").strip()
            if not title:
                self.logger.warning("RSS article missing title, skipping")
                return None

            # Extract summary (try different fields)
            summary = (
                raw_article.get("summary", "") or
                raw_article.get("description", "") or
                raw_article.get("content", [{}])[0].get("value", "") if raw_article.get("content") else ""
            ).strip()

            # Extract source (try different fields)
            # Priority: _feed_source (added by RSS aggregator) > source.title > publisher > Unknown
            source = (
                raw_article.get("_feed_source", "") or  # Custom field from RSS aggregator
                (raw_article.get("source", {}).get("title", "") if isinstance(raw_article.get("source"), dict) else "") or
                raw_article.get("publisher", "") or
                "Unknown Source"
            )

            # Extract URL
            url = raw_article.get("link", "")
            if not url:
                self.logger.warning(f"RSS article '{title}' missing URL, skipping")
                return None

            # Extract published date
            published_at = None
            if "published_parsed" in raw_article and raw_article["published_parsed"]:
                try:
                    dt = datetime(*raw_article["published_parsed"][:6])
                    published_at = dt.isoformat() + 'Z'
                except Exception as e:
                    self.logger.warning(f"Error parsing RSS published date: {e}")

            if not published_at:
                published_at = get_current_timestamp()

            # Build normalized article
            normalized = {
                "title": title,
                "summary": summary if summary else title,  # Fallback to title if no summary
                "source": source,
                "published_at": published_at,
                "category": category,
                "url": url,
                "importance_score": 0
            }

            return normalized

        except Exception as e:
            self.logger.error(f"Error normalizing RSS article: {e}", exc_info=True)
            return None

    def normalize_market_data(self, raw_data: Dict, category: str = "market_data") -> Optional[Dict]:
        """
        Convert market data to unified article schema.
        Note: This method is kept for future use if market data sources are added.

        Args:
            raw_data (Dict): Raw market data from external sources
            category (str): Topic category

        Returns:
            Optional[Dict]: Normalized article or None if error
        """
        try:
            # Extract fields
            title = raw_data.get("title", "Market Update")
            summary = raw_data.get("summary", "")
            source = raw_data.get("source", "Market Data Provider")
            url = raw_data.get("url", "")
            published_at = raw_data.get("published_at", get_current_timestamp())

            # Build normalized article
            normalized = {
                "title": title,
                "summary": summary,
                "source": source,
                "published_at": published_at,
                "category": category,
                "url": url,
                "importance_score": 0
            }

            return normalized

        except Exception as e:
            self.logger.error(f"Error normalizing market data: {e}", exc_info=True)
            return None

    def normalize_batch(
        self,
        articles: List[Dict],
        source_type: str = "rss",
        category: str = "unknown"
    ) -> List[Dict]:
        """
        Normalize a batch of articles.

        Args:
            articles (List[Dict]): List of raw articles
            source_type (str): Type of source ("rss", "market_data", etc.)
            category (str): Topic category

        Returns:
            List[Dict]: List of normalized articles
        """
        normalized_articles = []

        for raw_article in articles:
            if source_type == "rss":
                normalized = self.normalize_rss_article(raw_article, category)
            elif source_type == "market_data":
                normalized = self.normalize_market_data(raw_article, category)
            else:
                self.logger.warning(f"Unknown source type: {source_type}")
                continue

            if normalized:
                normalized_articles.append(normalized)

        self.logger.info(
            f"Normalized {len(normalized_articles)} articles from {len(articles)} raw {source_type} entries"
        )

        return normalized_articles

    def validate_article(self, article: Dict) -> bool:
        """
        Validate that an article conforms to the unified schema.

        Args:
            article (Dict): Article to validate

        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ["title", "summary", "source", "published_at", "category", "url"]

        for field in required_fields:
            if field not in article or not article[field]:
                self.logger.warning(f"Article missing required field: {field}")
                return False

        return True
