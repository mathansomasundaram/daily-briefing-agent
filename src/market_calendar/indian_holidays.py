"""
Indian Market Holiday Calendar.
Maintains NSE/BSE trading holidays to skip market data fetching.

Update this file annually with the official NSE holiday list:
https://www.nseindia.com/regulations/trading-holidays
"""

from datetime import datetime, date
from typing import List, Set
import calendar


# NSE/BSE Trading Holidays for 2026
# Source: https://www.nseindia.com/regulations/trading-holidays
INDIAN_MARKET_HOLIDAYS_2026 = [
    # Format: (month, day)
    (1, 26),   # Republic Day
    (3, 14),   # Mahashivratri
    (3, 25),   # Holi
    (4, 2),    # Ram Navami
    (4, 10),   # Mahavir Jayanti
    (4, 14),   # Dr. Ambedkar Jayanti
    (4, 18),   # Good Friday
    (5, 1),    # Maharashtra Day
    (8, 15),   # Independence Day
    (8, 27),   # Ganesh Chaturthi
    (10, 2),   # Gandhi Jayanti
    (10, 22),  # Dussehra
    (10, 31),  # Diwali Laxmi Pujan
    (11, 1),   # Diwali (Balipratipada)
    (11, 5),   # Guru Nanak Jayanti
    (12, 25),  # Christmas
]

# Add holidays for other years as needed
INDIAN_MARKET_HOLIDAYS_2027 = [
    # TODO: Update with 2027 holiday calendar when available
]

# Combine all years
ALL_HOLIDAYS = {
    2026: INDIAN_MARKET_HOLIDAYS_2026,
    2027: INDIAN_MARKET_HOLIDAYS_2027,
}


def is_indian_market_holiday(check_date: date = None) -> bool:
    """
    Check if a given date is an Indian market holiday.

    Args:
        check_date (date): Date to check. Defaults to today.

    Returns:
        bool: True if market is closed, False if market is open
    """
    if check_date is None:
        check_date = date.today()

    # Check if it's a weekend (Saturday=5, Sunday=6)
    if check_date.weekday() in [5, 6]:
        return True

    # Check if it's a holiday
    year = check_date.year
    if year in ALL_HOLIDAYS:
        holidays = ALL_HOLIDAYS[year]
        if (check_date.month, check_date.day) in holidays:
            return True

    return False


def get_market_holidays(year: int = None) -> List[date]:
    """
    Get all market holidays for a given year.

    Args:
        year (int): Year to get holidays for. Defaults to current year.

    Returns:
        List[date]: List of holiday dates
    """
    if year is None:
        year = date.today().year

    if year not in ALL_HOLIDAYS:
        return []

    holidays = []
    for month, day in ALL_HOLIDAYS[year]:
        holidays.append(date(year, month, day))

    # Add all Saturdays and Sundays
    for month in range(1, 13):
        for day in range(1, calendar.monthrange(year, month)[1] + 1):
            d = date(year, month, day)
            if d.weekday() in [5, 6]:  # Saturday or Sunday
                holidays.append(d)

    return sorted(set(holidays))


def get_next_trading_day(from_date: date = None) -> date:
    """
    Get the next trading day after a given date.

    Args:
        from_date (date): Starting date. Defaults to today.

    Returns:
        date: Next trading day
    """
    if from_date is None:
        from_date = date.today()

    check_date = from_date
    while True:
        # Move to next day
        check_date = date.fromordinal(check_date.toordinal() + 1)

        if not is_indian_market_holiday(check_date):
            return check_date


def get_market_status(check_date: date = None) -> dict:
    """
    Get detailed market status for a given date.

    Args:
        check_date (date): Date to check. Defaults to today.

    Returns:
        dict: Market status with details
    """
    if check_date is None:
        check_date = date.today()

    is_holiday = is_indian_market_holiday(check_date)
    is_weekend = check_date.weekday() in [5, 6]

    reason = None
    if is_weekend:
        reason = "Weekend"
    elif is_holiday:
        # Find the holiday name
        year = check_date.year
        if year in ALL_HOLIDAYS:
            holidays = ALL_HOLIDAYS[year]
            if (check_date.month, check_date.day) in holidays:
                # Get holiday index to find name
                holiday_names = [
                    "Republic Day", "Mahashivratri", "Holi", "Ram Navami",
                    "Mahavir Jayanti", "Dr. Ambedkar Jayanti", "Good Friday",
                    "Maharashtra Day", "Independence Day", "Ganesh Chaturthi",
                    "Gandhi Jayanti", "Dussehra", "Diwali Laxmi Pujan",
                    "Diwali (Balipratipada)", "Guru Nanak Jayanti", "Christmas"
                ]
                try:
                    idx = holidays.index((check_date.month, check_date.day))
                    reason = holiday_names[idx] if idx < len(holiday_names) else "Market Holiday"
                except (ValueError, IndexError):
                    reason = "Market Holiday"

    return {
        "date": check_date.strftime("%Y-%m-%d"),
        "is_holiday": is_holiday,
        "is_weekend": is_weekend,
        "is_trading_day": not is_holiday,
        "reason": reason,
        "next_trading_day": get_next_trading_day(check_date).strftime("%Y-%m-%d") if is_holiday else None
    }


# Market-related topics that should be skipped on holidays
MARKET_DEPENDENT_TOPICS = [
    "indian_stocks",
    "fii_dii",
    "company_results",
    "ipos"
]


def get_active_topics_for_date(all_topics: List[str], check_date: date = None) -> List[str]:
    """
    Filter topics based on market status.
    Skip market-related topics if market is closed.

    Args:
        all_topics (List[str]): All configured topics
        check_date (date): Date to check. Defaults to today.

    Returns:
        List[str]: Topics to fetch (market topics excluded if holiday)
    """
    if check_date is None:
        check_date = date.today()

    if is_indian_market_holiday(check_date):
        # Filter out market-dependent topics
        return [topic for topic in all_topics if topic not in MARKET_DEPENDENT_TOPICS]

    return all_topics
