"""
User configuration management module.
Handles loading and updating user preferences from user_config.json.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
USER_CONFIG_PATH = PROJECT_ROOT / "data" / "user_config.json"


def load_user_config() -> Dict:
    """
    Load user configuration from JSON file.

    Returns:
        Dict: Complete user configuration with all users

    Raises:
        FileNotFoundError: If user_config.json doesn't exist
        json.JSONDecodeError: If JSON is malformed
    """
    if not USER_CONFIG_PATH.exists():
        raise FileNotFoundError(f"User config file not found: {USER_CONFIG_PATH}")

    with open(USER_CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)

    return config


def get_active_users() -> List[Dict]:
    """
    Get all active users from configuration.

    Returns:
        List[Dict]: List of active user configurations
    """
    config = load_user_config()
    return [user for user in config.get("users", []) if user.get("active", True)]


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """
    Get specific user configuration by user_id.

    Args:
        user_id (str): User identifier

    Returns:
        Optional[Dict]: User configuration or None if not found
    """
    config = load_user_config()
    for user in config.get("users", []):
        if user.get("user_id") == user_id:
            return user
    return None


def get_user_topics(user_id: str) -> List[str]:
    """
    Get list of topics a user is subscribed to.

    Args:
        user_id (str): User identifier

    Returns:
        List[str]: List of topic identifiers
    """
    user = get_user_by_id(user_id)
    if user:
        return user.get("topics", [])
    return []


def get_user_email(user_id: str) -> Optional[str]:
    """
    Get user's email address.

    Args:
        user_id (str): User identifier

    Returns:
        Optional[str]: Email address or None
    """
    user = get_user_by_id(user_id)
    if user:
        return user.get("email")
    return None


def get_last_run_timestamp(user_id: str) -> Optional[str]:
    """
    Get the last run timestamp for a user.

    Args:
        user_id (str): User identifier

    Returns:
        Optional[str]: ISO format timestamp or None
    """
    user = get_user_by_id(user_id)
    if user:
        return user.get("last_run_timestamp")
    return None


def update_last_run_timestamp(user_id: str, timestamp: Optional[str] = None) -> bool:
    """
    Update the last run timestamp for a user.

    Args:
        user_id (str): User identifier
        timestamp (Optional[str]): ISO format timestamp, defaults to current UTC time

    Returns:
        bool: True if successful, False otherwise
    """
    if timestamp is None:
        timestamp = datetime.utcnow().isoformat() + 'Z'

    config = load_user_config()

    # Find and update the user
    user_found = False
    for user in config.get("users", []):
        if user.get("user_id") == user_id:
            user["last_run_timestamp"] = timestamp
            user_found = True
            break

    if not user_found:
        return False

    # Write back to file
    with open(USER_CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    return True


def save_user_config(config: Dict) -> bool:
    """
    Save complete user configuration to JSON file.

    Args:
        config (Dict): Complete configuration dictionary

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(USER_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving user config: {e}")
        return False
