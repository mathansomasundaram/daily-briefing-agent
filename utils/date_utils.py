"""
Date and time utility functions.
Handles timestamp parsing, formatting, and freshness checks.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
from dateutil import parser as dateutil_parser


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """
    Parse a timestamp string into a datetime object.
    Handles multiple formats including ISO format.

    Args:
        timestamp_str (str): Timestamp string to parse

    Returns:
        Optional[datetime]: Parsed datetime object (timezone-aware) or None if parsing fails
    """
    if not timestamp_str:
        return None

    try:
        dt = dateutil_parser.parse(timestamp_str)
        # Ensure timezone-aware
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError) as e:
        print(f"Error parsing timestamp '{timestamp_str}': {e}")
        return None


def get_current_timestamp() -> str:
    """
    Get current UTC timestamp in ISO format.

    Returns:
        str: Current timestamp (e.g., "2026-02-14T11:00:00Z")
    """
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def format_timestamp(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object into a string.

    Args:
        dt (datetime): Datetime object to format
        format_str (str): Format string (default: "%Y-%m-%d %H:%M:%S")

    Returns:
        str: Formatted timestamp string
    """
    return dt.strftime(format_str)


def is_within_last_n_hours(timestamp_str: str, hours: int = 24) -> bool:
    """
    Check if a timestamp is within the last N hours.

    Args:
        timestamp_str (str): Timestamp string to check
        hours (int): Number of hours to check (default: 24)

    Returns:
        bool: True if timestamp is within last N hours, False otherwise
    """
    dt = parse_timestamp(timestamp_str)
    if dt is None:
        return False

    now = datetime.now(timezone.utc)
    threshold = now - timedelta(hours=hours)

    return dt >= threshold


def is_newer_than(timestamp_str: str, reference_timestamp_str: str) -> bool:
    """
    Check if a timestamp is newer than a reference timestamp.

    Args:
        timestamp_str (str): Timestamp to check
        reference_timestamp_str (str): Reference timestamp

    Returns:
        bool: True if timestamp is newer, False otherwise
    """
    dt = parse_timestamp(timestamp_str)
    ref_dt = parse_timestamp(reference_timestamp_str)

    if dt is None or ref_dt is None:
        return False

    return dt > ref_dt


def get_time_ago_str(timestamp_str: str) -> str:
    """
    Get a human-readable "time ago" string from a timestamp.

    Args:
        timestamp_str (str): Timestamp string

    Returns:
        str: Human-readable time difference (e.g., "2 hours ago", "1 day ago")
    """
    dt = parse_timestamp(timestamp_str)
    if dt is None:
        return "unknown time ago"

    now = datetime.now(timezone.utc)
    diff = now - dt

    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "just now"
