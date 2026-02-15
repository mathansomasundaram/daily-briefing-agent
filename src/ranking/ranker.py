"""
Article ranking engine.
Scores and ranks articles by importance.
"""

from typing import List, Dict
from src.ranking.scoring_rules import (
    get_keyword_score,
    get_source_score,
    get_category_score
)
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ImportanceRanker:
    """
    Ranks articles by importance score.
    Combines keyword presence, source reputation, and category priority.
    """

    def __init__(self):
        self.logger = logger

    def score_article(self, article: Dict) -> float:
        """
        Calculate importance score for a single article.

        Scoring formula:
        score = (keyword_score * 0.5) + (source_score * 0.3) + (category_score * 0.2)

        Args:
            article (Dict): Article with title, summary, source, category

        Returns:
            float: Importance score
        """
        # Extract fields
        title = article.get("title", "")
        summary = article.get("summary", "")
        source = article.get("source", "Unknown Source")
        category = article.get("category", "unknown")

        # Combine title and summary for keyword scoring
        text = f"{title} {summary}"

        # Calculate component scores
        keyword_score = get_keyword_score(text)
        source_score = get_source_score(source)
        category_score = get_category_score(category)

        # Weighted combination
        final_score = (keyword_score * 0.5) + (source_score * 0.3) + (category_score * 0.2)

        return round(final_score, 2)

    def rank_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Score and rank all articles by importance.

        Args:
            articles (List[Dict]): List of articles to rank

        Returns:
            List[Dict]: Articles sorted by importance score (highest first)
        """
        if not articles:
            return []

        # Score each article
        for article in articles:
            article["importance_score"] = self.score_article(article)

        # Sort by score (descending)
        ranked = sorted(articles, key=lambda x: x["importance_score"], reverse=True)

        self.logger.info(f"Ranked {len(ranked)} articles. Top score: {ranked[0]['importance_score'] if ranked else 0}")

        return ranked

    def select_top_n(self, articles: List[Dict], n: int = 10) -> List[Dict]:
        """
        Select top N highest-scoring articles.

        Args:
            articles (List[Dict]): List of articles (assumed already ranked)
            n (int): Number of articles to select (default: 10)

        Returns:
            List[Dict]: Top N articles
        """
        return articles[:n]

    def rank_by_category(self, articles: List[Dict], n_per_category: int = 10) -> Dict[str, List[Dict]]:
        """
        Rank articles within each category and select top N per category.

        Args:
            articles (List[Dict]): List of all articles
            n_per_category (int): Number of articles to select per category

        Returns:
            Dict[str, List[Dict]]: Articles grouped by category, each list ranked
        """
        # Group by category
        by_category = {}
        for article in articles:
            category = article.get("category", "unknown")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(article)

        # Rank within each category
        ranked_by_category = {}
        for category, category_articles in by_category.items():
            ranked = self.rank_articles(category_articles)
            top_n = self.select_top_n(ranked, n_per_category)
            ranked_by_category[category] = top_n

            self.logger.info(f"Category '{category}': {len(category_articles)} articles, selected top {len(top_n)}")

        return ranked_by_category
