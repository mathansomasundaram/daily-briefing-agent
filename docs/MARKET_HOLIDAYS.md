# Market Holiday Management

The Daily Briefing Agent automatically detects Indian market holidays and skips market-related topics when markets are closed.

## How It Works

When the agent runs, it:
1. Checks if today is an Indian market holiday or weekend
2. If markets are closed, automatically skips these topics:
   - `indian_stocks` - Indian Stock Market
   - `fii_dii` - FII & DII Activity
   - `company_results` - Company Results & Announcements
   - `ipos` - Upcoming IPOs
3. Continues fetching other topics (geopolitics, tech, cybersecurity, commodities, etc.)

## Benefits

- **Saves API calls**: No unnecessary RSS fetches for market data
- **Reduces noise**: Users don't receive empty market sections
- **Better efficiency**: Faster execution on holidays
- **Automatic**: No manual intervention needed

## Checking Market Status

### Check Today's Status

```bash
python scripts/check_market_status.py
```

**Output:**
```
==============================================================
  Market Status for February 14, 2026 (Friday)
==============================================================

✅ Indian Stock Markets: OPEN
   Topics to fetch: ALL

==============================================================
  Next 7 Days
==============================================================

❌ 2026-02-15 (Saturday  )
❌ 2026-02-16 (Sunday    )
✅ 2026-02-17 (Monday    )
✅ 2026-02-18 (Tuesday   )
✅ 2026-02-19 (Wednesday )
✅ 2026-02-20 (Thursday  )
✅ 2026-02-21 (Friday    )
```

### Check Specific Date

```bash
python scripts/check_market_status.py --date 2026-08-15
```

**Output:**
```
==============================================================
  Market Status for August 15, 2026 (Saturday)
==============================================================

❌ Indian Stock Markets: CLOSED
   Reason: Independence Day
   Next Trading Day: 2026-08-17

   📋 Topics to SKIP:
      - indian_stocks
      - fii_dii
      - company_results
      - ipos
```

### View Year Calendar

```bash
python scripts/check_market_status.py --year 2026
```

**Output:**
```
==============================================================
  Indian Market Holidays - 2026
==============================================================

January 2026:
  26 - Monday    (Republic Day)

March 2026:
  14 - Saturday  (Mahashivratri)
  25 - Wednesday (Holi)
  ...

==============================================================
  Summary
==============================================================

Total Days in 2026: 365
Weekends: 104
Market Holidays (excluding weekends): 16
Total Non-Trading Days: 120
Trading Days: 245
```

## Updating the Holiday Calendar

The holiday calendar needs to be updated annually. Here's how:

### 1. Get Official Holiday List

Visit the official NSE website:
- https://www.nseindia.com/regulations/trading-holidays
- Download the current year's holiday calendar

### 2. Update the Code

Edit `src/market_calendar/indian_holidays.py`:

```python
# Add new year's holidays
INDIAN_MARKET_HOLIDAYS_2027 = [
    (1, 26),   # Republic Day
    (3, 4),    # Mahashivratri
    (3, 14),   # Holi
    # ... add all holidays
]

# Register in ALL_HOLIDAYS dictionary
ALL_HOLIDAYS = {
    2026: INDIAN_MARKET_HOLIDAYS_2026,
    2027: INDIAN_MARKET_HOLIDAYS_2027,  # Add new year
}
```

### 3. Validate

```bash
python scripts/check_market_status.py --year 2027
```

Verify all holidays are correctly listed.

## Market-Dependent Topics

These topics are automatically skipped when markets are closed:

| Topic Key | Description |
|-----------|-------------|
| `indian_stocks` | Indian Stock Market news |
| `fii_dii` | Foreign/Domestic Institutional Investor data |
| `company_results` | Company earnings and announcements |
| `ipos` | IPO and public offering news |

## Non-Market Topics

These topics are ALWAYS fetched, even on holidays:

| Topic Key | Description |
|-----------|-------------|
| `geopolitics` | Global macro and geopolitical news |
| `tech_ai` | AI & Technology news |
| `tech_cybersecurity` | Cybersecurity & data breaches |
| `us_fed` | US Federal Reserve updates |
| `commodities` | Commodities (Gold & Silver) |

**Why?** These topics are global and continue to have news even when Indian markets are closed.

## Customization

### Skip Different Topics on Holidays

Edit `src/market_calendar/indian_holidays.py`:

```python
MARKET_DEPENDENT_TOPICS = [
    "indian_stocks",
    "fii_dii",
    "company_results",
    "ipos",
    # Add custom topics here
    "your_custom_market_topic"
]
```

### Always Fetch Certain Topics

Remove topics from the `MARKET_DEPENDENT_TOPICS` list if you want them to be fetched even on holidays.

## Logging

When markets are closed, you'll see these log messages:

```
2026-02-15 06:00:00 - main - INFO - 📅 Market Status: CLOSED (Weekend)
2026-02-15 06:00:00 - main - INFO - ⏭️  Next trading day: 2026-02-17
2026-02-15 06:00:00 - main - INFO - ⏸️  Skipping market topics: indian_stocks, fii_dii, company_results, ipos
2026-02-15 06:00:00 - main - INFO - 📰 Fetching articles for topics: geopolitics, tech_ai, tech_cybersecurity, us_fed, commodities
```

## Special Cases

### Market Hours

The holiday detection is based on **date only**, not time. If markets are open but you run the script before market hours, it will still fetch data.

### Partial Holidays

If NSE announces a partial trading day (e.g., Muhurat Trading on Diwali), you can:
1. Keep it in the holiday list (no fetching)
2. OR remove it from the list (normal fetching)

### Late Holiday Announcements

If a holiday is announced last-minute:

```python
# Quick fix: Add to current year's list
INDIAN_MARKET_HOLIDAYS_2026.append((12, 31))  # Emergency holiday
```

Then restart the agent.

## Testing

Test the holiday detection:

```python
from src.market_calendar import is_indian_market_holiday, get_market_status
from datetime import date

# Test Independence Day 2026
aug15 = date(2026, 8, 15)
print(is_indian_market_holiday(aug15))  # True
print(get_market_status(aug15))
# Output: {'date': '2026-08-15', 'is_holiday': True, 'is_trading_day': False, 'reason': 'Independence Day', ...}

# Test normal weekday
aug17 = date(2026, 8, 17)
print(is_indian_market_holiday(aug17))  # False
print(get_market_status(aug17))
# Output: {'date': '2026-08-17', 'is_holiday': False, 'is_trading_day': True, 'reason': None}
```

## FAQ

**Q: What happens if I forget to update the calendar?**
A: The agent will fetch market topics as usual. It won't break, but you'll get empty or stale market data on holidays.

**Q: Can I disable holiday detection?**
A: Yes, set `MARKET_DEPENDENT_TOPICS = []` in `indian_holidays.py` to disable.

**Q: Does this work for other markets (US, Europe)?**
A: Currently only Indian market holidays are supported. You can add similar logic for other markets.

**Q: What about special trading sessions (Muhurat Trading)?**
A: Treat these as regular holidays since they're only 1-2 hours and may not have significant news.

## Maintenance Schedule

**Annually (December):**
1. Visit NSE website for next year's holidays
2. Update `INDIAN_MARKET_HOLIDAYS_XXXX` in `indian_holidays.py`
3. Add to `ALL_HOLIDAYS` dictionary
4. Test with `check_market_status.py --year XXXX`
5. Commit changes

**As Needed:**
- Monitor NSE announcements for emergency holidays
- Update immediately if last-minute holidays are declared
