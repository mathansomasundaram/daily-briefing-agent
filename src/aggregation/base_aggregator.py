"""
Base aggregator abstract class.
Defines the interface for all news aggregators.
"""

from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime


class BaseAggregator(ABC):
    """
    Abstract base class for all news aggregators.
    Each aggregator must implement the fetch_articles method.
    """

    def __init__(self, name: str = "BaseAggregator"):
        """
        Initialize the base aggregator.

        Args:
            name (str): Aggregator name for logging
        """
        self.name = name

    @abstractmethod
    def fetch_articles(self, category: str, since: datetime) -> List[Dict]:
        """
        Fetch articles for a given category since a specific timestamp.

        Args:
            category (str): Topic category (e.g., "geopolitics", "tech_ai")
            since (datetime): Fetch articles published after this time

        Returns:
            List[Dict]: List of raw articles (format depends on source)

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement fetch_articles")

    def get_name(self) -> str:
        """Get the aggregator name."""
        return self.name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
