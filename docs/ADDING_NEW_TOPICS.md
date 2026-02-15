# Adding New Topics to Daily Briefing Agent

This guide explains how to add new topics/categories to your daily briefing digest.

## Quick Start

To add a new topic, you need to update **one file**: `src/aggregation/sources_config.py`

## Step-by-Step Guide

### 1. Choose a Topic Key

Pick a short, lowercase identifier for your topic (e.g., `crypto`, `real_estate`, `startup_news`)

### 2. Add RSS Feed Sources

In `RSS_SOURCES` dictionary, add your topic with RSS feed URLs:

```python
RSS_SOURCES = {
    # ... existing topics ...

    "your_topic": [
        "https://example.com/rss/feed1.xml",
        "https://example.com/rss/feed2.xml",
        "https://another-source.com/feed.rss"
    ]
}
```

**Finding RSS Feeds:**
- Most news sites have RSS feeds (look for RSS icon or `/rss` in URL)
- Try appending `/rss`, `/feed`, or `/rss.xml` to site URLs
- Use tools like [RSS Feed Finder](https://www.rssfeedfinder.com/)

### 3. Add Source Domains

In `URL_TO_SOURCE` dictionary, add domain-to-name mappings for attribution:

```python
URL_TO_SOURCE = {
    # ... existing sources ...

    "example.com": "Example News",
    "another-source.com": "Another Source"
}
```

**Important:** Use the domain name as it appears in the RSS feed URL.

### 4. Add Display Name with Emoji

In `CATEGORY_DISPLAY_NAMES` dictionary, add a display name with emoji:

```python
CATEGORY_DISPLAY_NAMES = {
    # ... existing categories ...

    "your_topic": "🎯 Your Topic Display Name"
}
```

**Emoji Guidelines:**
- Choose a relevant emoji that represents your topic
- Put emoji at the start of the display name
- Keep the name concise (2-4 words)

**Popular Emojis:**
- 📱 Mobile/Apps
- 🏠 Real Estate
- ⚽ Sports
- 🎬 Entertainment
- 💊 Healthcare
- 🚗 Automotive
- 🌱 Environment/Climate
- 💼 Business
- 🎓 Education
- ₿ Cryptocurrency

### 5. Add Source Reputation Scores

In `SOURCE_REPUTATION` dictionary, add reputation scores (1.0-3.0) for your sources:

```python
SOURCE_REPUTATION = {
    # ... existing sources ...

    "Example News": 2.2,
    "Another Source": 2.5
}
```

**Reputation Score Guidelines:**
- **3.0**: Premium sources (Reuters, Bloomberg, WSJ, FT)
- **2.5**: Established publications (BBC, NYT, Economic Times)
- **2.0-2.3**: Good quality sources (TechCrunch, Mint, local newspapers)
- **1.5-1.9**: Emerging/niche sources
- **1.0**: Unknown sources

### 6. (Optional) Add to User Configuration

If you want users to subscribe to your new topic, update `src/user_config/users.json`:

```json
{
  "users": [
    {
      "user_id": "user1",
      "email": "user@example.com",
      "active": true,
      "topics": [
        "geopolitics",
        "tech_ai",
        "your_topic"  // Add your new topic here
      ]
    }
  ]
}
```

## Complete Example: Adding Cryptocurrency Topic

Here's a complete example of adding a "crypto" topic:

```python
# 1. Add to RSS_SOURCES
"crypto": [
    "https://cointelegraph.com/rss",
    "https://coindesk.com/arc/outboundfeeds/rss/",
    "https://decrypt.co/feed"
]

# 2. Add to URL_TO_SOURCE
"cointelegraph.com": "Cointelegraph",
"coindesk.com": "CoinDesk",
"decrypt.co": "Decrypt"

# 3. Add to CATEGORY_DISPLAY_NAMES
"crypto": "₿ Cryptocurrency & Blockchain"

# 4. Add to SOURCE_REPUTATION
"Cointelegraph": 2.0,
"CoinDesk": 2.3,
"Decrypt": 1.9
```

## Validation

After adding a new topic, validate your configuration:

```python
from src.aggregation.sources_config import validate_topic_config, validate_all_topics

# Validate single topic
result = validate_topic_config("your_topic")
print(result)

# Validate all topics
all_results = validate_all_topics()
print(all_results)
```

## Testing Your New Topic

1. **Test RSS Feed Fetching:**
   ```bash
   python -c "from src.aggregation.rss_aggregator import RSSAggregator; from datetime import datetime, timezone; agg = RSSAggregator(); articles = agg.fetch_articles('your_topic', datetime.now(timezone.utc)); print(f'Fetched {len(articles)} articles')"
   ```

2. **Run Full Pipeline:**
   ```bash
   python main.py
   ```

3. **Check Logs:**
   Look for your topic in the logs to ensure articles are being fetched and processed.

## Troubleshooting

### No Articles Found

- **Check RSS Feed URL**: Visit the URL in your browser to verify it works
- **Check Date Filtering**: Ensure articles are recent (within last 24 hours)
- **Check Feed Format**: Some feeds may not be standard RSS/Atom

### Source Attribution Missing

- **Check URL_TO_SOURCE**: Ensure the domain matches exactly
- **Check Feed URLs**: Extract domain from actual feed URLs in RSS

### Topic Not Appearing in Digest

- **Check User Config**: Ensure topic is in user's topic list
- **Check Article Count**: Verify articles are being fetched (check logs)
- **Check Deduplication**: Articles might be duplicates from previous runs

## Best Practices

1. **Start Small**: Add 2-3 reliable RSS feeds first
2. **Test Thoroughly**: Run the pipeline and check output quality
3. **Monitor Quality**: Check the digest for a few days to ensure good content
4. **Adjust Reputation**: Fine-tune source reputation scores based on content quality
5. **Batch Size**: If you have >5 categories, content will be processed in batches automatically

## Architecture Notes

The system is designed to be scalable:

- **Automatic Emoji Detection**: Formatter automatically detects emojis from your display names
- **Batch Processing**: Categories are processed in batches of 5 to prevent LLM hallucination
- **Dynamic Configuration**: All topic config is centralized in one file
- **Validation Functions**: Built-in validation ensures configuration is complete

## Need Help?

If you encounter issues:
1. Check logs in console output
2. Validate your configuration using validation functions
3. Test RSS feeds individually
4. Review this guide for missing steps

## Summary Checklist

Before deploying a new topic:

- [ ] Added to `RSS_SOURCES`
- [ ] Added sources to `URL_TO_SOURCE`
- [ ] Added to `CATEGORY_DISPLAY_NAMES` with emoji
- [ ] Added source reputation scores to `SOURCE_REPUTATION`
- [ ] Added to user's topic list (if applicable)
- [ ] Validated configuration
- [ ] Tested RSS feed fetching
- [ ] Tested full pipeline
- [ ] Checked output quality in digest
