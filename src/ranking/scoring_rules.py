"""
Scoring rules for article ranking.
Defines keyword weights, source reputation, and category scores.
"""

# Keyword weights for importance scoring
# Higher weight = more important
KEYWORD_WEIGHTS = {
    # Breaking/Urgent news
    "breaking": 3.0,
    "urgent": 2.5,
    "alert": 2.5,
    "critical": 2.5,

    # Financial/Market keywords
    "fed": 2.0,
    "federal reserve": 2.5,
    "reserve bank": 2.0,
    "rbi": 2.0,
    "interest rate": 2.0,
    "inflation": 1.8,
    "recession": 2.2,
    "market crash": 3.0,
    "bull market": 1.5,
    "bear market": 1.8,

    # Indian market specific
    "nifty": 1.5,
    "sensex": 1.5,
    "fii": 2.0,
    "dii": 2.0,
    "ipo": 2.5,
    "listing": 2.0,
    "earnings": 1.8,
    "results": 1.5,
    "quarterly": 1.5,

    # Commodities
    "gold": 1.5,
    "silver": 1.5,
    "crude oil": 1.8,
    "commodity": 1.3,

    # Technology/AI
    "ai": 1.5,
    "artificial intelligence": 1.8,
    "machine learning": 1.5,
    "chatgpt": 1.8,
    "openai": 1.5,
    "google": 1.3,
    "microsoft": 1.3,
    "apple": 1.3,
    "nvidia": 1.5,

    # Cybersecurity
    "data breach": 2.5,
    "hack": 2.2,
    "ransomware": 2.3,
    "cyberattack": 2.5,
    "vulnerability": 2.0,
    "zero-day": 2.5,
    "malware": 2.0,
    "phishing": 1.8,

    # Geopolitics
    "war": 2.5,
    "conflict": 2.0,
    "sanctions": 2.0,
    "treaty": 1.8,
    "election": 1.8,
    "china": 1.5,
    "russia": 1.8,
    "ukraine": 1.8,
    "middle east": 1.8,
    "india": 1.3,

    # Crisis/Emergency
    "crisis": 2.3,
    "emergency": 2.3,
    "disaster": 2.0,
    "pandemic": 2.5
}

# Negative keywords - reduce score for irrelevant content
# These are entertainment, lifestyle, human interest stories
NEGATIVE_KEYWORDS = {
    "valentine": -2.0,
    "bouquet": -2.0,
    "celebrity": -1.5,
    "wedding": -1.5,
    "fashion": -1.5,
    "recipe": -2.0,
    "horoscope": -2.0,
    "lottery": -1.5,
    "sports score": -1.0,
    "movie": -1.0,
    "entertainment": -1.0,
    "trivia": -1.5
}

# Source reputation scores
# Higher score = more trusted/authoritative
SOURCE_REPUTATION = {
    # Top tier financial
    "Reuters": 3.0,
    "Bloomberg": 3.0,
    "Financial Times": 3.0,
    "The Wall Street Journal": 3.0,

    # Government/Official
    "Federal Reserve": 3.0,
    "Reserve Bank of India": 3.0,
    "RBI": 3.0,

    # Indian Financial
    "Economic Times": 2.5,
    "Business Standard": 2.3,
    "Moneycontrol": 2.2,
    "Livemint": 2.2,

    # Technology
    "TechCrunch": 2.0,
    "The Verge": 1.8,
    "Wired": 2.0,
    "Ars Technica": 2.0,

    # Cybersecurity
    "The Hacker News": 2.2,
    "BleepingComputer": 2.0,
    "Security Week": 2.0,
    "Krebs on Security": 2.5,

    # General News
    "BBC": 2.5,
    "CNN": 2.0,
    "Al Jazeera": 2.0,
    "The New York Times": 2.5,

    # Default
    "Unknown Source": 1.0
}

# Category base scores
# Prioritize certain categories
CATEGORY_SCORES = {
    "us_fed": 2.0,           # High priority - impacts markets
    "fii_dii": 2.0,          # High priority - direct market impact
    "indian_stocks": 1.8,    # High-medium priority
    "geopolitics": 1.5,      # Medium priority
    "tech_cybersecurity": 2.0,  # High priority - security
    "tech_ai": 1.5,          # Medium priority
    "commodities": 1.5,      # Medium priority
    "ipos": 1.8,             # High-medium priority
    "company_results": 1.7,  # High-medium priority
    "unknown": 1.0           # Default
}


def get_keyword_score(text: str) -> float:
    """
    Calculate keyword-based score for text (title + summary).
    Positive keywords increase score, negative keywords decrease it.

    Args:
        text (str): Combined text to score

    Returns:
        float: Keyword score (can be negative for irrelevant content)
    """
    if not text:
        return 0.0

    text_lower = text.lower()
    score = 0.0

    # Add positive keyword weights
    for keyword, weight in KEYWORD_WEIGHTS.items():
        if keyword.lower() in text_lower:
            score += weight

    # Subtract negative keyword weights (for irrelevant content)
    for keyword, penalty in NEGATIVE_KEYWORDS.items():
        if keyword.lower() in text_lower:
            score += penalty  # penalty is already negative

    return score


def get_source_score(source: str) -> float:
    """
    Get reputation score for a source.

    Args:
        source (str): Source name

    Returns:
        float: Reputation score
    """
    # Try exact match
    if source in SOURCE_REPUTATION:
        return SOURCE_REPUTATION[source]

    # Try partial match
    source_lower = source.lower()
    for known_source, score in SOURCE_REPUTATION.items():
        if known_source.lower() in source_lower or source_lower in known_source.lower():
            return score

    # Default
    return SOURCE_REPUTATION["Unknown Source"]


def get_category_score(category: str) -> float:
    """
    Get priority score for a category.

    Args:
        category (str): Category name

    Returns:
        float: Category priority score
    """
    return CATEGORY_SCORES.get(category, CATEGORY_SCORES["unknown"])
