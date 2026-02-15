# Topic Configuration Template

Copy and modify this template when adding a new topic to `src/aggregation/sources_config.py`.

## Template

```python
# ============================================================================
# NEW TOPIC: [Your Topic Name]
# ============================================================================

# 1. RSS_SOURCES
# Add your RSS feed URLs here
RSS_SOURCES = {
    # ... existing topics ...

    "your_topic_key": [
        "https://example-news.com/rss/your-topic.xml",
        "https://another-source.com/feeds/topic.rss",
        "https://third-source.org/rss"
    ]
}

# 2. URL_TO_SOURCE
# Map domain names to display names for attribution
URL_TO_SOURCE = {
    # ... existing sources ...

    "example-news.com": "Example News",
    "another-source.com": "Another Source",
    "third-source.org": "Third Source"
}

# 3. CATEGORY_DISPLAY_NAMES
# Add display name with emoji (emoji first!)
CATEGORY_DISPLAY_NAMES = {
    # ... existing categories ...

    "your_topic_key": "🎯 Your Topic Display Name"
}

# 4. SOURCE_REPUTATION
# Add reputation scores (1.0 = unknown, 3.0 = premium)
SOURCE_REPUTATION = {
    # ... existing sources ...

    "Example News": 2.2,
    "Another Source": 2.5,
    "Third Source": 2.0
}

# 5. (Optional) YAHOO_FINANCE_TICKERS
# Only if you need market data for this topic
YAHOO_FINANCE_TICKERS = {
    # ... existing tickers ...

    "your_topic_key": [
        "TICKER1.NS",
        "TICKER2.BO"
    ]
}
```

## Quick Reference

### Common Emojis by Topic

| Topic Category | Emoji | Example |
|---------------|-------|---------|
| Business/Finance | 💼 📊 💰 | "💼 Business News" |
| Technology | 💻 📱 🖥️ | "💻 Technology Updates" |
| Healthcare | 💊 🏥 ⚕️ | "💊 Healthcare News" |
| Sports | ⚽ 🏀 🏈 | "⚽ Sports Updates" |
| Entertainment | 🎬 🎭 🎵 | "🎬 Entertainment News" |
| Environment | 🌱 ♻️ 🌍 | "🌱 Environmental News" |
| Real Estate | 🏠 🏘️ 🏗️ | "🏠 Real Estate Market" |
| Automotive | 🚗 🏎️ 🚙 | "🚗 Automotive Industry" |
| Education | 🎓 📚 📖 | "🎓 Education Updates" |
| Food & Dining | 🍽️ 🍕 🍔 | "🍽️ Food & Dining" |
| Travel | ✈️ 🌍 🗺️ | "✈️ Travel News" |
| Crypto | ₿ 💎 🪙 | "₿ Cryptocurrency" |
| Gaming | 🎮 🕹️ 🎯 | "🎮 Gaming News" |
| Fashion | 👗 👠 💄 | "👗 Fashion & Style" |
| Politics | 🏛️ 🗳️ 📜 | "🏛️ Political News" |

### Reputation Score Guidelines

```
3.0  = Reuters, Bloomberg, WSJ, Financial Times, Federal Reserve
2.5  = BBC, NYT, Economic Times, Mint, established newspapers
2.0  = TechCrunch, Medium-tier publications, industry blogs
1.5  = Emerging sources, niche publications
1.0  = Unknown or unverified sources
```

### RSS Feed Finding Tips

1. **Add /rss to website URL**:
   - `example.com` → `example.com/rss`

2. **Add /feed**:
   - `example.com` → `example.com/feed`

3. **Look for RSS icon**: 📡 (usually in footer)

4. **Check /rss.xml or /feed.xml**:
   - `example.com/rss.xml`
   - `example.com/feed.xml`

5. **Category-specific feeds**:
   - `example.com/category/tech/rss`
   - `example.com/sports/feed`

6. **Use RSS Feed Finder tools**:
   - https://www.rssfeedfinder.com/
   - https://feedsearch.dev/

## Example: Cryptocurrency Topic

Here's a complete working example:

```python
# 1. RSS_SOURCES
"crypto": [
    "https://cointelegraph.com/rss",
    "https://coindesk.com/arc/outboundfeeds/rss/",
    "https://decrypt.co/feed",
    "https://cryptonews.com/news/feed/"
]

# 2. URL_TO_SOURCE
"cointelegraph.com": "Cointelegraph",
"coindesk.com": "CoinDesk",
"decrypt.co": "Decrypt",
"cryptonews.com": "CryptoNews"

# 3. CATEGORY_DISPLAY_NAMES
"crypto": "₿ Cryptocurrency & Blockchain"

# 4. SOURCE_REPUTATION
"Cointelegraph": 2.0,
"CoinDesk": 2.3,
"Decrypt": 1.9,
"CryptoNews": 1.8
```

## Validation Checklist

After adding your topic configuration:

```bash
# 1. Validate configuration
python scripts/validate_config.py

# 2. Test RSS feed fetching
python -c "
from src.aggregation.rss_aggregator import RSSAggregator
from datetime import datetime, timezone
agg = RSSAggregator()
articles = agg.fetch_articles('your_topic_key', datetime.now(timezone.utc))
print(f'✅ Fetched {len(articles)} articles')
"

# 3. Run full pipeline
python main.py
```

## Common Mistakes

1. ❌ **Wrong domain in URL_TO_SOURCE**
   - Feed URL: `https://subdomain.example.com/rss`
   - Wrong: `"example.com": "Example"`
   - Correct: `"subdomain.example.com": "Example"`

2. ❌ **Emoji in wrong position**
   - Wrong: `"Tech News 💻"`
   - Correct: `"💻 Tech News"`

3. ❌ **Topic key mismatch**
   - RSS_SOURCES: `"tech_news"`
   - CATEGORY_DISPLAY_NAMES: `"tech-news"` ❌
   - Use same key everywhere! ✅

4. ❌ **Missing comma after list**
   ```python
   "topic1": [
       "feed1.rss"
   ]  # Missing comma here!
   "topic2": [  # This will cause error
   ```

5. ❌ **Not validating after adding**
   - Always run `python scripts/validate_config.py`

## Need Help?

- See [ADDING_NEW_TOPICS.md](ADDING_NEW_TOPICS.md) for full guide
- Check existing topics in `sources_config.py` for examples
- Run validation script to find configuration issues
