"""
Main orchestrator for Daily Briefing Agent.
Coordinates the entire pipeline from news aggregation to email delivery.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from datetime import datetime, timezone
from typing import Optional
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Import all modules
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
from email_service import send_email
from utils.logger import setup_logger
from utils.date_utils import parse_timestamp
from config import EMAIL_SUBJECT
import json

# Load environment variables
load_dotenv()

# Setup logger
logger = setup_logger(__name__)

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", ""),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "")
)

# Token usage file path
TOKEN_USAGE_FILE = project_root / "data" / "token_usage.json"


def save_token_usage(user_id: str, token_data: dict):
    """
    Save token usage to JSON file.

    Args:
        user_id (str): User identifier
        token_data (dict): Token usage data
    """
    # Load existing data
    if TOKEN_USAGE_FILE.exists() and TOKEN_USAGE_FILE.stat().st_size > 0:
        try:
            with open(TOKEN_USAGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            logger.warning("Token usage file corrupted, creating new one")
            data = {"runs": []}
    else:
        data = {"runs": []}
        TOKEN_USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Add current run
    run_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "input_tokens": token_data.get("input_tokens", 0),
        "output_tokens": token_data.get("output_tokens", 0),
        "total_tokens": token_data.get("total_tokens", 0)
    }
    data["runs"].append(run_data)

    # Save to file
    with open(TOKEN_USAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"💾 Token usage saved: {run_data['total_tokens']} total tokens")


def fetch_and_normalize_articles(
    topics: list,
    since_timestamp: str
) -> list:
    """
    Fetch articles from all sources and normalize them.
    Automatically skips market-related topics if Indian markets are closed.

    Args:
        topics (list): List of topic categories
        since_timestamp (str): Fetch articles since this timestamp

    Returns:
        list: Normalized articles
    """
    # Check market status and filter topics accordingly
    today = datetime.now(timezone.utc).date()
    market_status = get_market_status(today)
    active_topics = get_active_topics_for_date(topics, today)

    # Log market status
    if market_status["is_holiday"]:
        logger.info(f"📅 Market Status: CLOSED ({market_status['reason']})")
        logger.info(f"⏭️  Next trading day: {market_status['next_trading_day']}")

        skipped_topics = [t for t in topics if t not in active_topics]
        if skipped_topics:
            logger.info(f"⏸️  Skipping market topics: {', '.join(skipped_topics)}")
    else:
        logger.info(f"📈 Market Status: OPEN")

    logger.info(f"📰 Fetching articles for topics: {active_topics}")

    # Parse timestamp
    since_dt = parse_timestamp(since_timestamp)
    if since_dt is None:
        # Default to 24 hours ago
        since_dt = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    # Initialize aggregators
    rss_agg = RSSAggregator()
    normalizer = ArticleNormalizer()

    all_articles = []

    # Fetch from RSS feeds (only for active topics)
    for topic in active_topics:
        try:
            logger.info(f"Fetching RSS articles for: {topic}")
            rss_articles = rss_agg.fetch_articles(topic, since_dt)

            # Normalize
            normalized_rss = normalizer.normalize_batch(rss_articles, source_type="rss", category=topic)
            all_articles.extend(normalized_rss)

        except Exception as e:
            logger.error(f"Error fetching RSS for {topic}: {e}", exc_info=True)

    logger.info(f"Total articles fetched and normalized: {len(all_articles)}")
    return all_articles


def process_pipeline(user_id: str) -> tuple[Optional[str], Optional[dict]]:
    """
    Run the complete pipeline for a single user.

    Args:
        user_id (str): User identifier

    Returns:
        tuple: (Formatted digest ready for email or None, Token usage dict or None)
    """
    logger.info(f"Starting pipeline for user: {user_id}")

    # 1. Load user configuration
    topics = get_user_topics(user_id)
    last_run = get_last_run_timestamp(user_id)

    if not topics:
        logger.warning(f"No topics configured for user {user_id}")
        return None, None

    # Default to 24 hours ago if no last_run
    if not last_run:
        last_run = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'

    logger.info(f"User topics: {topics}, Last run: {last_run}")

    # 2. Fetch and normalize articles
    articles = fetch_and_normalize_articles(topics, last_run)

    if not articles:
        logger.warning("No articles fetched")
        return "No new articles available for your topics today.", None

    # 3. Deduplication
    dedup_manager = DeduplicationManager()
    articles = dedup_manager.filter_duplicates(articles)

    if not articles:
        logger.info("All articles were duplicates")
        return "No new articles available (all were previously sent).", None

    # 4. Ranking (reduced from 10 to 5 per category to fit all categories in LLM output)
    ranker = ImportanceRanker()
    articles_by_category = ranker.rank_by_category(articles, n_per_category=5)

    # 5. Content filtering
    content_filter = ContentFilter()
    filtered_by_category = {}

    for category, category_articles in articles_by_category.items():
        filtered = content_filter.process_all(
            category_articles,
            max_summary_length=200,  # Reduced from 300 to fit more categories
            max_tokens=1500  # Reduced from 2000 to allow all categories
        )
        if filtered:
            filtered_by_category[category] = filtered

    if not filtered_by_category:
        logger.warning("No articles after filtering")
        return "No high-quality articles available today.", None

    # 6. LLM Formatting (increased token limit to fit all 9 categories)
    # Use Azure deployment name from environment variable
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
    formatter = LLMFormatter(client, model=deployment_name, max_output_tokens=4000)
    formatted_digest = formatter.format_digest(filtered_by_category)

    # 7. Mark articles as sent
    all_urls = []
    for articles_list in filtered_by_category.values():
        all_urls.extend([a["url"] for a in articles_list])

    dedup_manager.mark_as_sent(all_urls)

    logger.info(f"Pipeline complete. Formatted {len(all_urls)} articles")

    # Return formatted digest and token usage
    return formatted_digest, formatter.token_usage


def main():
    """
    Main execution function.
    Processes all active users and sends daily digests.
    """
    try:
        logger.info("=" * 60)
        logger.info("Daily Briefing Agent - Starting")
        logger.info("=" * 60)

        # Get all active users
        users = get_active_users()

        if not users:
            logger.warning("No active users found")
            return

        logger.info(f"Processing {len(users)} active user(s)")

        # Process each user
        for user in users:
            user_id = user["user_id"]
            email = user["email"]

            logger.info(f"\nProcessing user: {user_id} ({email})")

            try:
                # Run pipeline
                digest_content, token_usage = process_pipeline(user_id)

                if digest_content:
                    # Send email
                    logger.info(f"Sending email to {email}")
                    send_email(
                        subject=EMAIL_SUBJECT,
                        body=digest_content,
                        receivers=[email]
                    )

                    # Save token usage to file
                    if token_usage:
                        save_token_usage(user_id, token_usage)

                    # Update last run timestamp
                    update_last_run_timestamp(user_id)
                    logger.info(f"Successfully sent digest to {email}")

                else:
                    logger.warning(f"No digest generated for {user_id}")

            except Exception as e:
                logger.error(f"Error processing user {user_id}: {e}", exc_info=True)
                # Continue with next user

        logger.info("\n" + "=" * 60)
        logger.info("Daily Briefing Agent - Completed")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Fatal error in main: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
