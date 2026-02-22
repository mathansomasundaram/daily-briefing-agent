"""
Main orchestrator for Daily Briefing Agent.
Refactored for production-grade quality.
"""

from datetime import datetime, timezone
from typing import Optional, Tuple

from openai import AzureOpenAI

from src.user_config.user_manager import (
    get_active_users,
    get_user_topics,
    get_last_run_timestamp,
    update_last_run_timestamp
)
from src.aggregation.rss_aggregator import RSSAggregator
from src.normalization.normalizer import ArticleNormalizer
from src.deduplication.dedup_manager import DeduplicationManager
from src.ranking.ranker import ImportanceRanker
from src.filtering.content_filter import ContentFilter
from src.llm_formatter.formatter import LLMFormatter
from src.market_calendar import get_active_topics_for_date, get_market_status
from src.token_tracker import TokenTracker
from src.settings import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT_NAME,
    AZURE_OPENAI_MAX_OUTPUT_TOKENS,
    EMAIL_SUBJECT,
    DATA_DIR,
    ARTICLES_PER_CATEGORY,
    MAX_SUMMARY_LENGTH,
    MAX_TOKENS_PER_ARTICLE,
    ensure_directories
)
from email_service import send_email
from utils.logger import setup_logger
from utils.date_utils import parse_timestamp
from src.exceptions import (
    DailyBriefingError,
    ArticleFetchError,
    FormattingError,
    EmailDeliveryError
)

# Setup logger
logger = setup_logger(__name__)

# Ensure directories exist
ensure_directories()

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# Initialize token tracker
token_tracker = TokenTracker(DATA_DIR)


def fetch_articles(topics: list, since_timestamp: str) -> list:
    """
    Fetch and normalize articles for given topics.

    Args:
        topics: List of topic categories
        since_timestamp: Fetch articles since this timestamp

    Returns:
        List of normalized articles

    Raises:
        ArticleFetchError: If article fetching fails critically
    """
    today = datetime.now(timezone.utc).date()
    market_status = get_market_status(today)
    active_topics = get_active_topics_for_date(topics, today)

    # Log market status
    if market_status["is_holiday"]:
        logger.info("Market Status: CLOSED (%s)", market_status['reason'])
        logger.info("Next trading day: %s", market_status['next_trading_day'])
        skipped = [t for t in topics if t not in active_topics]
        if skipped:
            logger.info("Skipping market topics: %s", ', '.join(skipped))
    else:
        logger.info("Market Status: OPEN")

    logger.info("Fetching articles for topics: %s", active_topics)

    # Parse timestamp with fallback
    since_dt = parse_timestamp(since_timestamp)
    if since_dt is None:
        since_dt = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    # Fetch from RSS feeds
    rss_agg = RSSAggregator()
    normalizer = ArticleNormalizer()
    all_articles = []

    for topic in active_topics:
        try:
            logger.info("Fetching RSS articles for: %s", topic)
            rss_articles = rss_agg.fetch_articles(topic, since_dt)
            normalized = normalizer.normalize_batch(
                rss_articles,
                source_type="rss",
                category=topic
            )
            all_articles.extend(normalized)
        except Exception as e:
            logger.error("Error fetching RSS for %s: %s", topic, str(e), exc_info=True)
            # Continue with other topics

    logger.info("Total articles fetched: %d", len(all_articles))
    return all_articles


def process_user_pipeline(user_id: str) -> Tuple[Optional[str], Optional[dict]]:
    """
    Run the complete pipeline for a single user.

    Args:
        user_id: User identifier

    Returns:
        Tuple of (formatted digest or None, token usage dict or None)
    """
    logger.info("Starting pipeline for user: %s", user_id)

    # Load user configuration
    topics = get_user_topics(user_id)
    last_run = get_last_run_timestamp(user_id)

    if not topics:
        logger.warning("No topics configured for user %s", user_id)
        return None, None

    # Default to 24 hours ago if no last_run
    if not last_run:
        last_run = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        ).isoformat() + 'Z'

    logger.info("User topics: %s, Last run: %s", topics, last_run)

    # Fetch articles
    try:
        articles = fetch_articles(topics, last_run)
    except Exception as e:
        raise ArticleFetchError(f"Failed to fetch articles: {e}") from e

    if not articles:
        logger.warning("No articles fetched")
        return "No new articles available for your topics today.", None

    # Deduplication
    dedup_manager = DeduplicationManager()
    articles = dedup_manager.filter_duplicates(articles)

    if not articles:
        logger.info("All articles were duplicates")
        return "No new articles available (all were previously sent).", None

    # Ranking
    ranker = ImportanceRanker()
    articles_by_category = ranker.rank_by_category(
        articles,
        n_per_category=ARTICLES_PER_CATEGORY
    )

    # Content filtering
    content_filter = ContentFilter()
    filtered_by_category = {}

    for category, category_articles in articles_by_category.items():
        filtered = content_filter.process_all(
            category_articles,
            max_summary_length=MAX_SUMMARY_LENGTH,
            max_tokens=MAX_TOKENS_PER_ARTICLE
        )
        if filtered:
            filtered_by_category[category] = filtered

    if not filtered_by_category:
        logger.warning("No articles after filtering")
        return "No high-quality articles available today.", None

    # LLM Formatting
    try:
        formatter = LLMFormatter(
            client,
            model=AZURE_OPENAI_DEPLOYMENT_NAME,
            max_output_tokens=AZURE_OPENAI_MAX_OUTPUT_TOKENS
        )
        formatted_digest = formatter.format_digest(filtered_by_category)
    except Exception as e:
        raise FormattingError(f"Failed to format digest: {e}") from e

    # Mark articles as sent
    all_urls = [
        article["url"]
        for articles_list in filtered_by_category.values()
        for article in articles_list
    ]
    dedup_manager.mark_as_sent(all_urls)

    logger.info("Pipeline complete. Formatted %d articles", len(all_urls))

    return formatted_digest, formatter.token_usage


def process_user(user: dict) -> bool:
    """
    Process a single user's digest.

    Args:
        user: User configuration dict

    Returns:
        True if successful, False otherwise
    """
    user_id = user["user_id"]
    email = user["email"]

    logger.info("Processing user: %s (%s)", user_id, email)

    try:
        # Run pipeline
        digest_content, token_usage = process_user_pipeline(user_id)

        if not digest_content:
            logger.warning("No digest generated for %s", user_id)
            return False

        # Send email
        logger.info("Sending email to %s", email)
        try:
            send_email(
                subject=EMAIL_SUBJECT,
                body=digest_content,
                receivers=[email]
            )
        except Exception as e:
            raise EmailDeliveryError(f"Failed to send email: {e}") from e

        # Save token usage
        if token_usage:
            token_tracker.save(user_id, token_usage)

        # Update last run timestamp
        update_last_run_timestamp(user_id)
        logger.info("Successfully sent digest to %s", email)
        return True

    except DailyBriefingError as e:
        logger.error("Pipeline error for %s: %s", user_id, str(e), exc_info=True)
        return False
    except Exception as e:
        logger.error("Unexpected error for %s: %s", user_id, str(e), exc_info=True)
        return False


def main():
    """Main execution function."""
    logger.info("=" * 60)
    logger.info("Daily Briefing Agent - Starting")
    logger.info("=" * 60)

    try:
        users = get_active_users()

        if not users:
            logger.warning("No active users found")
            return

        logger.info("Processing %d active user(s)", len(users))

        # Process each user
        success_count = 0
        for user in users:
            if process_user(user):
                success_count += 1

        logger.info("\n" + "=" * 60)
        logger.info(
            "Daily Briefing Agent - Completed (%d/%d successful)",
            success_count,
            len(users)
        )
        logger.info("=" * 60)

    except Exception as e:
        logger.error("Fatal error in main: %s", str(e), exc_info=True)
        raise


if __name__ == "__main__":
    main()
