# Daily Briefing Agent

An intelligent news aggregation system that delivers personalized daily digests covering markets, technology, and global news.

## Features

- 📰 **Multi-Source RSS Aggregation**: Fetches news from 20+ reliable sources
- 🤖 **AI-Powered Formatting**: Uses Azure OpenAI to format articles into clean, readable digests
- 📧 **Email Delivery**: Automated email delivery to configured users
- 🔄 **Smart Deduplication**:
  - URL-based deduplication to prevent re-sending same articles
  - **NEW**: Content similarity detection using embeddings to remove duplicate stories from different sources
- ⚡ **Batch Processing**: Handles large numbers of categories efficiently
- 📊 **Token Usage Logging**: Tracks LLM usage for cost monitoring
- 📅 **Market Holiday Detection**: Automatically skips market-related topics when Indian markets are closed

## Current Topics

- 🌍 Geopolitical & Global Macro News
- 💰 Commodities (Gold & Silver)
- 📈 Indian Stock Market
- 💼 FII & DII Activity
- 📊 Indian Economy
- 🤖 AI & Technology
- 🔒 Cybersecurity & Data Breaches
- 🏦 US Federal Reserve
- 🚀 Upcoming IPOs
- 🏢 Company Results & Announcements
- 📍 Tamil Nadu & Coimbatore News (State News)

