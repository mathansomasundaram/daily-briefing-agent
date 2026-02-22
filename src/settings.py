"""
Centralized application settings.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Azure OpenAI settings
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
AZURE_OPENAI_MAX_OUTPUT_TOKENS = 4000

# Email settings
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "")
EMAIL_SUBJECT = "📰 Daily Market & Tech Briefing"

# Pipeline settings
ARTICLES_PER_CATEGORY = 5
MAX_SUMMARY_LENGTH = 200
MAX_TOKENS_PER_ARTICLE = 1500
LLM_BATCH_SIZE = 5  # Process N categories at a time

# Deduplication settings
ENABLE_CONTENT_DEDUPLICATION = True
SIMILARITY_THRESHOLD = 0.85
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
DEDUP_CLEANUP_DAYS = 30

# Data file paths
SENT_ARTICLES_FILE = DATA_DIR / "sent_articles.json"
TOKEN_USAGE_FILE = DATA_DIR / "token_usage.json"
USER_CONFIG_FILE = DATA_DIR / "user_config.json"


def validate_settings() -> bool:
    """
    Validate critical settings are present.

    Returns:
        True if all critical settings valid, False otherwise
    """
    errors = []

    if not AZURE_OPENAI_API_KEY:
        errors.append("AZURE_OPENAI_API_KEY not set")

    if not AZURE_OPENAI_ENDPOINT:
        errors.append("AZURE_OPENAI_ENDPOINT not set")

    if not EMAIL_ADDRESS:
        errors.append("EMAIL_ADDRESS not set")

    if not EMAIL_APP_PASSWORD:
        errors.append("EMAIL_APP_PASSWORD not set")

    if errors:
        for error in errors:
            print(f"Configuration error: {error}")
        return False

    return True


def ensure_directories() -> None:
    """Create necessary directories if they don't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
