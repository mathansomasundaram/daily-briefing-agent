"""
RSS feed aggregator.
Fetches articles from RSS feeds using feedparser.
"""

import feedparser
import ssl
import certifi
from typing import List, Dict
from datetime import datetime, timezone
from tenacity import retry, stop_after_attempt, wait_exponential

from src.aggregation.base_aggregator import BaseAggregator
from src.aggregation.sources_config import get_rss_sources, get_source_name_from_url
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Create SSL context with certifi certificates
ssl_context = ssl.create_default_context(cafile=certifi.where())


class RSSAggregator(BaseAggregator):
    """
    Aggregator for RSS news feeds.
    Fetches articles from multiple RSS sources for a given category.
    """

    def __init__(self):
        super().__init__(name="RSSAggregator")
        self.logger = logger

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _fetch_feed(self, url: str) -> feedparser.FeedParserDict:
        """
        Fetch a single RSS feed with retry logic.

        Args:
            url (str): RSS feed URL

        Returns:
            feedparser.FeedParserDict: Parsed feed

        Raises:
            Exception: If feed fetch fails after retries
        """
        self.logger.info(f"Fetching RSS feed: {url}")

        # Use custom SSL context to avoid certificate errors
        import urllib.request

        try:
            # Create request with SSL context
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                feed_data = response.read()

            # Parse the feed data
            feed = feedparser.parse(feed_data)
        except Exception as e:
            self.logger.error(f"Error fetching feed {url}: {e}")
            # Fallback to basic parse (may still fail)
            feed = feedparser.parse(url)

        if feed.get("bozo", False):
            # Feed has errors
            bozo_exception = feed.get('bozo_exception', 'Unknown error')
            self.logger.warning(f"RSS feed parsing issues: {url} - {bozo_exception}")

        return feed

    def fetch_articles(self, category: str, since: datetime) -> List[Dict]:
        """
        Fetch articles from RSS feeds for a given category.

        Args:
            category (str): Topic category (e.g., "geopolitics", "tech_ai")
            since (datetime): Fetch articles published after this time

        Returns:
            List[Dict]: List of raw RSS entries
        """
        self.logger.info(f"Fetching RSS articles for category: {category}, since: {since}")

        # Get RSS feed URLs for this category
        feed_urls = get_rss_sources(category)

        if not feed_urls:
            self.logger.warning(f"No RSS sources configured for category: {category}")
            return []

        all_articles = []


        for url in feed_urls:
            try:
                feed = self._fetch_feed(url)

                feed_source = get_source_name_from_url(url)

                if not feed_source:
                    try:
                        if hasattr(feed, 'feed'):
                            feed_dict = feed.feed
                            if isinstance(feed_dict, dict):
                                feed_source = (
                                    feed_dict.get('title', '') or
                                    feed_dict.get('publisher', '') or
                                    None
                                )
                            elif hasattr(feed_dict, 'title'):
                                feed_source = getattr(feed_dict, 'title', None) or getattr(feed_dict, 'publisher', None)
                    except Exception as e:
                        self.logger.debug(f"Could not extract source from feed: {e}")
                        feed_source = None

                # Extract entries from feed
                entries = feed.get("entries", [])
                if entries is None:
                    entries = []

                self.logger.info(f"Fetched {len(entries)} entries from {url}")

                # Add source information to each entry
                for entry in entries:
                    if feed_source and not entry.get('source'):
                        entry['_feed_source'] = feed_source  

                # Filter by published date
                filtered_entries = self._filter_by_date(list(entries), since)
                self.logger.info(f"Filtered to {len(filtered_entries)} articles after {since}")

                all_articles.extend(filtered_entries)

            except Exception as e:
                self.logger.error(f"Failed to fetch RSS feed {url}: {e}", exc_info=True)
                # Continue with other feeds

        self.logger.info(f"Total RSS articles fetched for {category}: {len(all_articles)}")
        return all_articles

    def _filter_by_date(self, entries: List[Dict], since: datetime) -> List[Dict]:
        """
        Filter RSS entries by published date.

        Args:
            entries (List[Dict]): Raw RSS entries
            since (datetime): Minimum published date

        Returns:
            List[Dict]: Filtered entries
        """
        filtered = []

        for entry in entries:
            # Try to parse published date
            published_dt = None

            if "published_parsed" in entry and entry["published_parsed"]:
                try:
                    published_dt = datetime(*entry["published_parsed"][:6], tzinfo=timezone.utc)
                except Exception as e:
                    self.logger.warning(f"Error parsing RSS date: {e}")

            # If no date or date is newer than 'since', include it
            if published_dt is None or published_dt >= since:
                filtered.append(entry)

        return filtered

    def fetch_all_categories(self, categories: List[str], since: datetime) -> Dict[str, List[Dict]]:
        """
        Fetch articles for multiple categories.

        Args:
            categories (List[str]): List of category names
            since (datetime): Fetch articles published after this time

        Returns:
            Dict[str, List[Dict]]: Articles grouped by category
        """
        results = {}

        for category in categories:
            articles = self.fetch_articles(category, since)
            results[category] = articles

        return results
