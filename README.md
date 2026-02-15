# Daily Briefing Agent

An intelligent news aggregation system that delivers personalized daily digests covering markets, technology, and global news.

## Features

- 📰 **Multi-Source RSS Aggregation**: Fetches news from 20+ reliable sources
- 🤖 **AI-Powered Formatting**: Uses Azure OpenAI to format articles into clean, readable digests
- 📧 **Email Delivery**: Automated email delivery to configured users
- 🔄 **Smart Deduplication**: Prevents duplicate articles across runs
- ⚡ **Batch Processing**: Handles large numbers of categories efficiently
- 📊 **Token Usage Logging**: Tracks LLM usage for cost monitoring

## Current Topics

- 🌍 Geopolitical & Global Macro News
- 💰 Commodities (Gold & Silver)
- 📈 Indian Stock Market
- 💼 India FII & DII Activity
- 🤖 AI & Technology
- 🔒 Cybersecurity & Data Breaches
- 🏦 US Federal Reserve
- 🚀 Upcoming IPOs
- 🏢 Company Results & Announcements

## Quick Start

### Prerequisites

- Python 3.11+
- Azure OpenAI API access
- SMTP server for email delivery

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables in `.env`:
   ```
   AZURE_OPENAI_API_KEY=your_key_here
   AZURE_OPENAI_ENDPOINT=your_endpoint_here
   AZURE_OPENAI_API_VERSION=2024-02-01
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini

   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   ```

### Running

```bash
python main.py
```

## Adding New Topics

Want to add cryptocurrency, sports, or other topics? It's easy!

👉 **See [docs/ADDING_NEW_TOPICS.md](docs/ADDING_NEW_TOPICS.md) for detailed instructions.**

Quick summary:
1. Add RSS feeds to `src/aggregation/sources_config.py`
2. Add source attribution and display names
3. Add reputation scores
4. Validate configuration: `python scripts/validate_config.py`
5. Run the pipeline: `python main.py`

## Architecture

```
main.py
  ├── User Management (src/user_config/)
  ├── RSS Aggregation (src/aggregation/)
  ├── Article Normalization (src/normalization/)
  ├── Deduplication (src/deduplication/)
  ├── Importance Ranking (src/ranking/)
  ├── Content Filtering (src/filtering/)
  ├── LLM Formatting (src/llm_formatter/)
  └── Email Delivery (email_service.py)
```

### Scalability Features

- **Batch Processing**: Categories are processed in batches of 5 to prevent LLM hallucination
- **Dynamic Configuration**: All topics configured in one central file
- **Automatic Emoji Detection**: No hardcoding needed when adding new topics
- **Validation Tools**: Built-in validation ensures configuration completeness

## Configuration Files

- `src/user_config/users.json` - User subscriptions and topics
- `src/aggregation/sources_config.py` - RSS feeds, sources, and topic configuration
- `data/sent_articles.json` - Deduplication tracking (auto-generated)

## Scripts

- `python main.py` - Run the daily briefing pipeline
- `python scripts/validate_config.py` - Validate topic configuration

## Customization

### Change Batch Size

Edit `main.py` line 175:

```python
formatter = LLMFormatter(client, model=deployment_name, max_output_tokens=4000, batch_size=5)
```

Change `batch_size=5` to your preferred value (e.g., `batch_size=3` for 3 categories per batch).

### Adjust Articles Per Category

Edit `main.py` line 153:

```python
articles_by_category = ranker.rank_by_category(articles, n_per_category=5)
```

Change `n_per_category=5` to show more or fewer articles per topic.

### Change Email Subject

Edit `config.py`:

```python
EMAIL_SUBJECT = f"📊 Daily AI Market & Tech Digest - {TODAY}"
```

## Logs

The system logs all operations to console with timestamps. Key log messages include:

- Article fetching progress
- Token usage for LLM calls
- Deduplication statistics
- Email delivery status

## Troubleshooting

### No Articles Found

- Check RSS feed URLs are still valid
- Verify date filtering (articles must be from last 24 hours)
- Check logs for HTTP errors

### Duplicate Categories

- Run deduplication cleanup: the system automatically handles this
- Check that RSS feeds aren't shared between categories

### High Token Usage

- Reduce `n_per_category` in main.py
- Reduce `max_summary_length` in content filter
- Consider using smaller batch sizes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Test thoroughly
5. Submit a pull request

## License

[Your License Here]

## Support

For issues or questions:
1. Check [docs/ADDING_NEW_TOPICS.md](docs/ADDING_NEW_TOPICS.md)
2. Review logs for error messages
3. Open an issue on GitHub
