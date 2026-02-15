"""
Content filtering module.
Filters low-quality articles and optimizes token usage before LLM processing.
"""

from typing import List, Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ContentFilter:
    """
    Filters and optimizes articles for LLM processing.
    Removes low-quality content and reduces token usage.
    """

    def __init__(self):
        self.logger = logger

        # Spam/low-quality indicators
        self.spam_keywords = [
            "click here",
            "buy now",
            "limited time",
            "act now",
            "subscribe",
            "sign up free",
            "exclusive offer"
        ]

        # Irrelevant keywords for market/tech digest (human interest, lifestyle, entertainment)
        self.irrelevant_keywords = [
            "valentine",
            "bouquet",
            "celebrity",
            "wedding",
            "fashion",
            "recipe",
            "diet",
            "horoscope",
            "astrology",
            "sports score",
            "game result",
            "movie review",
            "album review",
            "lottery",
            "trivia"
        ]

    def filter_low_quality(self, articles: List[Dict]) -> List[Dict]:
        """
        Remove low-quality articles based on heuristics.

        Filters out articles with:
        - Very short summaries (< 50 chars)
        - Missing critical fields
        - Spam keywords
        - Empty or placeholder content

        Args:
            articles (List[Dict]): Articles to filter

        Returns:
            List[Dict]: Filtered articles
        """
        filtered = []

        for article in articles:
            # Check required fields
            if not article.get("title") or not article.get("summary"):
                self.logger.debug("Skipping article with missing title/summary")
                continue

            # Check minimum length (reduced from 50 to 20 for RSS feeds with short summaries)
            summary = article.get("summary", "")
            if len(summary) < 20:
                self.logger.debug(f"Skipping short article: {article.get('title', 'Unknown')[:50]}")
                continue

            # Check for spam
            text_lower = f"{article.get('title', '')} {summary}".lower()
            if any(spam in text_lower for spam in self.spam_keywords):
                self.logger.debug(f"Skipping spam article: {article.get('title', 'Unknown')[:50]}")
                continue

            # Check for irrelevant content (human interest, lifestyle, entertainment)
            if any(keyword in text_lower for keyword in self.irrelevant_keywords):
                self.logger.debug(f"Skipping irrelevant article: {article.get('title', 'Unknown')[:50]}")
                continue

            # Passed all checks
            filtered.append(article)

        removed_count = len(articles) - len(filtered)
        if removed_count > 0:
            self.logger.info(f"Filtered out {removed_count} low-quality articles")

        return filtered

    def trim_summaries(self, articles: List[Dict], max_length: int = 300) -> List[Dict]:
        """
        Trim long summaries to reduce token usage.

        Args:
            articles (List[Dict]): Articles to process
            max_length (int): Maximum summary length in characters (default: 300)

        Returns:
            List[Dict]: Articles with trimmed summaries
        """
        trimmed_count = 0

        for article in articles:
            summary = article.get("summary", "")

            if len(summary) > max_length:
                # Trim and add ellipsis
                article["summary"] = summary[:max_length].rsplit(' ', 1)[0] + "..."
                trimmed_count += 1

        if trimmed_count > 0:
            self.logger.info(f"Trimmed {trimmed_count} article summaries to max {max_length} chars")

        return articles

    def limit_tokens(self, articles: List[Dict], max_tokens: int = 2000) -> List[Dict]:
        """
        Limit total articles to fit within token budget.
        Uses rough estimate: 1 token ≈ 4 characters.

        Args:
            articles (List[Dict]): Articles (assumed already ranked)
            max_tokens (int): Maximum token count (default: 2000)

        Returns:
            List[Dict]: Truncated article list if needed
        """
        CHARS_PER_TOKEN = 4
        max_chars = max_tokens * CHARS_PER_TOKEN

        total_chars = 0
        limited_articles = []

        for article in articles:
            # Estimate character count for this article
            text = f"{article.get('title', '')} {article.get('summary', '')}"
            article_chars = len(text)

            if total_chars + article_chars <= max_chars:
                limited_articles.append(article)
                total_chars += article_chars
            else:
                # Budget exceeded, stop adding articles
                break

        removed_count = len(articles) - len(limited_articles)
        if removed_count > 0:
            self.logger.info(
                f"Limited articles to {len(limited_articles)} to fit token budget "
                f"(~{total_chars // CHARS_PER_TOKEN} tokens)"
            )

        return limited_articles

    def process_all(
        self,
        articles: List[Dict],
        max_summary_length: int = 300,
        max_tokens: int = 2000
    ) -> List[Dict]:
        """
        Apply all filtering steps in sequence.

        Args:
            articles (List[Dict]): Raw articles
            max_summary_length (int): Max summary length
            max_tokens (int): Max token budget

        Returns:
            List[Dict]: Filtered and optimized articles
        """
        self.logger.info(f"Processing {len(articles)} articles through content filter")

        # Step 1: Remove low quality
        filtered = self.filter_low_quality(articles)

        # Step 2: Trim summaries
        trimmed = self.trim_summaries(filtered, max_summary_length)

        # Step 3: Limit tokens
        limited = self.limit_tokens(trimmed, max_tokens)

        self.logger.info(f"Content filter output: {len(limited)} articles")

        return limited
