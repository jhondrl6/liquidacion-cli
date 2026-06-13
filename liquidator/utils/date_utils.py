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


# ---------------------------------------------------------------------------
# Date-object helpers (used by tests and date arithmetic).
# Unlike the str-based helpers above, these accept/return ``datetime.date``.
# ---------------------------------------------------------------------------


def is_valid_date(value: str) -> bool:
    """Return ``True`` if ``value`` is a valid ``YYYY-MM-DD`` date string.

    No exception is raised on bad input; the caller is expected to handle the
    boolean directly (mirrors the contract the test suite assumes).
    """
    if not isinstance(value, str):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def is_leap_year(year: int) -> bool:
    """Return ``True`` for a Gregorian leap year."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_year(year: int) -> int:
    """Return 366 for a leap year, 365 otherwise."""
    return 366 if is_leap_year(year) else 365


def get_semester(d: date) -> int:
    """Return ``1`` for H1 (Jan–Jun) or ``2`` for H2 (Jul–Dec)."""
    return 1 if d.month <= 6 else 2


def get_semester_bounds(d: date) -> tuple[date, date]:
    """Return ``(start, end)`` of the academic/calendar semester that contains ``d``.

    H1 spans Jan 1 – Jun 30 (inclusive). H2 spans Jul 1 – Dec 31 (inclusive).
    """
    if d.month <= 6:
        return (date(d.year, 1, 1), date(d.year, 6, 30))
    return (date(d.year, 7, 1), date(d.year, 12, 31))


def days_in_semester(d: date) -> int:
    """Return the number of days in the semester that contains ``d``."""
    start, end = get_semester_bounds(d)
    return (end - start).days + 1


# ---------------------------------------------------------------------------
# Date-object helpers — used by tests/test_utils/test_date_currency_utils.py
# These accept/return ``datetime.date`` (NOT strings), matching the test
# contract that the old aliases in ``__init__.py`` failed to provide.
# ---------------------------------------------------------------------------


def parse_date(value: str) -> date:
    """Parse a ``YYYY-MM-DD`` string into a ``datetime.date``."""
    return datetime.strptime(value, "%Y-%m-%d").date()


def days_between_inclusive_date(start: date, end: date) -> int:
    """Return the inclusive day count between two ``date`` objects.

    ``days_between_inclusive_date(date(2025,1,1), date(2025,1,31)) → 31``
    """
    if end < start:
        raise ValueError("End date must be after start date")
    return (end - start).days + 1


def business_days_between_date(
    start: date, end: date, holidays: set[date] | None = None
) -> int:
    """Count business days (Mon–Fri, excl. holidays) between *start* and *end*.

    Both bounds are inclusive.
    """
    holidays = holidays or set()
    if end < start:
        return 0
    current = start
    count = 0
    while current <= end:
        if current.weekday() < 5 and current not in holidays:
            count += 1
        current += timedelta(days=1)
    return count


def add_business_days_date(
    start: date, days: int, holidays: set[date] | None = None
) -> date:
    """Return the date *days* business days after *start*, skipping weekends
    and any dates in *holidays*."""
    holidays = holidays or set()
    current = start
    added = 0
    while added < days:
        current += timedelta(days=1)
        if current.weekday() < 5 and current not in holidays:
            added += 1
    return current
