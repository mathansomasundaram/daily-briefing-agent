"""
News sources configuration.
Maps topic categories to RSS feed URLs and other data sources.

HOW TO ADD A NEW TOPIC:
=======================
1. Add RSS feeds to RSS_SOURCES dictionary
2. Add source domain to URL_TO_SOURCE for proper attribution
3. Add display name with emoji to CATEGORY_DISPLAY_NAMES
4. Add source reputation scores to SOURCE_REPUTATION (1.0-3.0)
5. Validate using validate_topic_config() function

EXAMPLE:
--------
To add "crypto" topic:

1. RSS_SOURCES:
   "crypto": [
       "https://cointelegraph.com/rss",
       "https://coindesk.com/arc/outboundfeeds/rss/"
   ]

2. URL_TO_SOURCE:
   "cointelegraph.com": "Cointelegraph",
   "coindesk.com": "CoinDesk"

3. CATEGORY_DISPLAY_NAMES:
   "crypto": "₿ Cryptocurrency & Blockchain"

4. SOURCE_REPUTATION:
   "Cointelegraph": 2.0,
   "CoinDesk": 2.2
"""

# URL to Source Name mapping (for better source attribution)
URL_TO_SOURCE = {
    "rss.nytimes.com": "The New York Times",
    "feeds.bbci.co.uk": "BBC",
    "aljazeera.com": "Al Jazeera",
    "techcrunch.com": "TechCrunch",
    "theverge.com": "The Verge",
    "wired.com": "Wired",
    "arstechnica.com": "Ars Technica",
    "feedburner.com/TheHackersNews": "The Hacker News",
    "bleepingcomputer.com": "BleepingComputer",
    "feedburner.com/Securityweek": "Security Week",
    "economictimes.indiatimes.com": "Economic Times",
    "moneycontrol.com": "Moneycontrol",
    "federalreserve.gov": "Federal Reserve",
    "reuters.com": "Reuters",
    "investing.com": "Investing.com",
    "kitco.com": "Kitco",
    "livemint.com": "Mint",
    "indiatoday.in": "India Today",
    "timesofindia.indiatimes.com": "Times of India",
    "thehindubusinessline.com": "Business Line",
    "thehindu.com": "The Hindu",
    "newindianexpress.com": "New Indian Express",
    "washingtonpost.com": "The Washington Post",
}

def get_source_name_from_url(url: str) -> str:
    """
    Extract a proper source name from feed URL.

    Args:
        url (str): Feed URL

    Returns:
        str: Proper source name or empty string if not found
    """
    for key, name in URL_TO_SOURCE.items():
        if key in url:
            return name
    return ""

# RSS Feed URLs mapped to topic categories
RSS_SOURCES = {
    "geopolitics": [
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://www.reuters.com/rssfeed/worldNews",
        "https://feeds.washingtonpost.com/rss/world"
    ],
    "tech_ai": [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://www.wired.com/feed/category/business/ai/latest/rss",
        "https://feeds.arstechnica.com/arstechnica/technology-lab"
    ],
    "tech_cybersecurity": [
        "https://feeds.feedburner.com/TheHackersNews",
        "https://www.bleepingcomputer.com/feed/",
        "https://feeds.feedburner.com/Securityweek"
    ],
    "indian_stocks": [
        "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
        "https://www.moneycontrol.com/rss/latestnews.xml",
        "https://www.moneycontrol.com/rss/marketreports.xml",
        "https://indianexpress.com/section/business/market/feed/",
        "https://www.livemint.com/rss/markets",
        "https://www.livemint.com/rss/money",
        "https://timesofindia.indiatimes.com/rssfeeds/1898055.cms",  
        "https://www.indiatoday.in/rss/1206578",  
        "https://www.thehindubusinessline.com/markets/stock-markets/?service=rss"
    ],
    "us_fed": [
        "https://www.federalreserve.gov/feeds/press_all.xml",
        "https://www.reuters.com/finance/rss"
    ],
    "commodities": [
        "https://www.investing.com/rss/commodities.rss",
        "https://www.reuters.com/markets/commodities/rss",
        "https://www.kitco.com/rss/KitcoArticles.xml" 
    ],
    "company_results": [
        "https://economictimes.indiatimes.com/markets/stocks/earnings/rssfeeds/11294550.cms"
    ],
    "ipos": [
        "https://economictimes.indiatimes.com/markets/ipos/fpos/rssfeeds/67812886.cms",
        "https://economictimes.indiatimes.com/markets/ipo/rssfeeds/61225961.cms"
    ],
    "fii_dii": [
        "https://www.moneycontrol.com/rss/marketoutlook.xml",
        "https://economictimes.indiatimes.com/markets/stocks/news/rssfeeds/2146449.cms",
        "https://www.livemint.com/rss/money"
    ],
    "state_news_tn": [
        "https://www.thehindu.com/news/national/tamil-nadu/feeder/default.rss",
        "https://www.newindianexpress.com/states/tamil-nadu/?widgetName=rssfeed&widgetId=429436&getXmlFeed=true"
    ],
    "india_economy" : [
        "https://www.thehindu.com/business/Economy/feeder/default.rss"
    ]
}

# Category display names for email formatting
CATEGORY_DISPLAY_NAMES = {
    "geopolitics": "🌍 Geopolitical & Global Macro News",
    "tech_ai": "🤖 AI & Technology",
    "tech_cybersecurity": "🔒 Cybersecurity & Data Breaches",
    "indian_stocks": "📈 Indian Stock Market",
    "us_fed": "🏦 US Federal Reserve",
    "commodities": "💰 Commodities (Gold & Silver)",
    "fii_dii": "💼 FII & DII Activity",
    "ipos": "🚀 Upcoming IPOs",
    "company_results": "🏢 Company Results & Announcements",
    "india_economy": "📊 Indian Economy",
    "state_news_tn": "📍 Tamil Nadu & Coimbatore News"
}

# Source reputation scores (used by ranking engine)
SOURCE_REPUTATION = {
    "Reuters": 3.0,
    "Bloomberg": 3.0,
    "Financial Times": 3.0,
    "The Wall Street Journal": 3.0,
    "Economic Times": 2.9,
    "Moneycontrol": 3.0,
    "Mint": 2.5,
    "Times of India": 2.2,
    "India Today": 2.2,
    "Business Line": 2.4,
    "Federal Reserve": 3.0,
    "TechCrunch": 2.0,
    "The Verge": 1.8,
    "Wired": 2.0,
    "BBC": 2.5,
    "Al Jazeera": 2.0,
    "The Hacker News": 2.2,
    "BleepingComputer": 2.0,
    "Investing.com": 2.2,
    "Kitco": 2.1,
    "The Hindu": 2.6,
    "New Indian Express": 2.3,
    "The New York Times": 2.8,
    "The Washington Post": 2.9,
    "Ars Technica": 2.1,
    "Security Week": 2.0,
    "Unknown Source": 1.0
}

def get_rss_sources(category: str) -> list:
    """
    Get RSS feed URLs for a given category.

    Args:
        category (str): Topic category

    Returns:
        list: List of RSS feed URLs
    """
    return RSS_SOURCES.get(category, [])


def get_category_display_name(category: str) -> str:
    """
    Get display name for a category.

    Args:
        category (str): Topic category key

    Returns:
        str: Display name with emoji
    """
    return CATEGORY_DISPLAY_NAMES.get(category, category.replace("_", " ").title())


def get_all_categories() -> list:
    """
    Get list of all available categories.

    Returns:
        list: List of category keys
    """
    return list(RSS_SOURCES.keys())


def get_all_category_emojis() -> list:
    """
    Extract all emojis from category display names.
    Used for dynamic emoji detection in formatter.

    Returns:
        list: List of emojis used in category headings
    """
    emojis = []
    for display_name in CATEGORY_DISPLAY_NAMES.values():
        for char in display_name:
            if ord(char) > 127: 
                emojis.append(char)
                break
    return emojis


def validate_topic_config(topic: str) -> dict:
    """
    Validate that a topic has all required configuration.

    Args:
        topic (str): Topic key to validate

    Returns:
        dict: Validation result with 'valid' (bool) and 'missing' (list) keys
    """
    missing = []

    # Check RSS sources
    if topic not in RSS_SOURCES:
        missing.append(f"RSS_SOURCES['{topic}']")

    # Check display name
    if topic not in CATEGORY_DISPLAY_NAMES:
        missing.append(f"CATEGORY_DISPLAY_NAMES['{topic}']")

    if topic in RSS_SOURCES:
        for feed_url in RSS_SOURCES[topic]:
            source_name = get_source_name_from_url(feed_url)
            if source_name and source_name not in SOURCE_REPUTATION:
                missing.append(f"SOURCE_REPUTATION['{source_name}'] (from {feed_url})")

    return {
        "valid": len(missing) == 0,
        "missing": missing,
        "topic": topic
    }


def validate_all_topics() -> dict:
    """
    Validate all configured topics.

    Returns:
        dict: Summary of validation results
    """
    all_topics = get_all_categories()
    results = {
        "total": len(all_topics),
        "valid": 0,
        "invalid": 0,
        "details": {}
    }

    for topic in all_topics:
        validation = validate_topic_config(topic)
        results["details"][topic] = validation

        if validation["valid"]:
            results["valid"] += 1
        else:
            results["invalid"] += 1

    return results
