"""
Custom exceptions for Daily Briefing Agent.
"""


class DailyBriefingError(Exception):
    """Base exception for all Daily Briefing Agent errors."""
    pass


class ConfigurationError(DailyBriefingError):
    """Raised when configuration is invalid or missing."""
    pass


class ArticleFetchError(DailyBriefingError):
    """Raised when article fetching fails."""
    pass


class DeduplicationError(DailyBriefingError):
    """Raised when deduplication process fails."""
    pass


class FormattingError(DailyBriefingError):
    """Raised when LLM formatting fails."""
    pass


class EmailDeliveryError(DailyBriefingError):
    """Raised when email delivery fails."""
    pass


class TokenTrackingError(DailyBriefingError):
    """Raised when token usage tracking fails."""
    pass
