#!/usr/bin/env python3
"""
Market Status Checker.
Check if Indian markets are open today and view the holiday calendar.

Usage:
    python scripts/check_market_status.py
    python scripts/check_market_status.py --date 2026-08-15
    python scripts/check_market_status.py --year 2026
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, date

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.market_calendar import (
    is_indian_market_holiday,
    get_market_status,
    get_market_holidays,
    get_next_trading_day,
    MARKET_DEPENDENT_TOPICS
)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def check_specific_date(check_date: date):
    """Check market status for a specific date."""
    print_section(f"Market Status for {check_date.strftime('%B %d, %Y (%A)')}")

    status = get_market_status(check_date)

    if status["is_trading_day"]:
        print("✅ Indian Stock Markets: OPEN")
        print(f"   Topics to fetch: ALL")
    else:
        print(f"❌ Indian Stock Markets: CLOSED")
        print(f"   Reason: {status['reason']}")
        print(f"   Next Trading Day: {status['next_trading_day']}")
        print(f"\n   📋 Topics to SKIP:")
        for topic in MARKET_DEPENDENT_TOPICS:
            print(f"      - {topic}")


def show_year_calendar(year: int):
    """Show all holidays for a year."""
    print_section(f"Indian Market Holidays - {year}")

    holidays = get_market_holidays(year)

    if not holidays:
        print(f"⚠️  No holiday calendar available for {year}")
        print("   Please update src/market_calendar/indian_holidays.py")
        return

    # Group by month
    from collections import defaultdict
    by_month = defaultdict(list)

    for holiday in holidays:
        by_month[holiday.month].append(holiday)

    # Print by month
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    trading_days = 0
    total_days = 365 + (1 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 0)

    for month in range(1, 13):
        if month in by_month:
            print(f"\n{month_names[month-1]} {year}:")
            for holiday in sorted(by_month[month]):
                day_name = holiday.strftime("%A")
                if holiday.weekday() in [5, 6]:  # Weekend
                    print(f"  {holiday.day:2d} - {day_name:9s} (Weekend)")
                else:
                    print(f"  {holiday.day:2d} - {day_name:9s}")

    holidays_count = len([h for h in holidays if h.weekday() not in [5, 6]])
    weekends = len([h for h in holidays if h.weekday() in [5, 6]])
    trading_days = total_days - len(holidays)

    print_section("Summary")
    print(f"Total Days in {year}: {total_days}")
    print(f"Weekends: {weekends}")
    print(f"Market Holidays (excluding weekends): {holidays_count}")
    print(f"Total Non-Trading Days: {len(holidays)}")
    print(f"Trading Days: {trading_days}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Check Indian market status and view holiday calendar"
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Check specific date (format: YYYY-MM-DD)"
    )
    parser.add_argument(
        "--year",
        type=int,
        help="Show full year calendar"
    )

    args = parser.parse_args()

    if args.date:
        # Check specific date
        try:
            check_date = datetime.strptime(args.date, "%Y-%m-%d").date()
            check_specific_date(check_date)
        except ValueError:
            print("❌ Invalid date format. Use YYYY-MM-DD (e.g., 2026-08-15)")
            return 1

    elif args.year:
        # Show year calendar
        show_year_calendar(args.year)

    else:
        # Default: check today
        today = date.today()
        check_specific_date(today)

        # Show next 7 days
        print_section("Next 7 Days")
        from datetime import timedelta

        for i in range(1, 8):
            future_date = today + timedelta(days=i)
            is_holiday = is_indian_market_holiday(future_date)
            day_name = future_date.strftime("%A")
            status_icon = "❌" if is_holiday else "✅"

            print(f"{status_icon} {future_date.strftime('%Y-%m-%d')} ({day_name:9s})")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
