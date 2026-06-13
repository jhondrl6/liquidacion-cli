from datetime import datetime, date, timedelta
from .cache import global_cache


def get_current_year():
    return datetime.now().year


def calculate_days_between(start_date: str, end_date: str) -> int:
    """
    Calculate the number of days between two dates (inclusive).

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Number of days between dates (included both dates)
    """
    cache_key = global_cache.generate_key('calculate_days_between', start_date, end_date)
    cached_result = global_cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    if end < start:
        raise ValueError("End date must be after start date")

    result = (end - start).days + 1  # Include both dates
    global_cache.set(cache_key, result)
    return result


def calculate_years_of_service(start_date: str, end_date: str) -> float:
    """
    Calculate years of service between two dates.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Years of service as a float (including fractions)
    """
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    if end < start:
        raise ValueError("End date must be after start date")

    years = end.year - start.year
    remaining_days = (end - datetime(end.year, start.month, start.day).date()).days
    return years + (remaining_days / 365.25)


def add_business_days(start_date: str, days: int) -> str:
    """
    Add business days to a date, skipping weekends.

    Args:
        start_date: Start date in YYYY-MM-DD format
        days: Number of business days to add

    Returns:
        New date in YYYY-MM-DD format
    """
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    current_date = start
    business_days_added = 0

    while business_days_added < days:
        current_date += timedelta(days=1)
        # Skip weekends (Saturday=5, Sunday=6)
        if current_date.weekday() < 5:
            business_days_added += 1

    return current_date.strftime("%Y-%m-%d")
