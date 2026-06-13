from datetime import date
from decimal import Decimal

from liquidator.utils import (
    add_business_days,
    business_days_between,
    days_between_inclusive,
    days_in_semester,
    days_in_year,
    format_cop,
    get_semester,
    get_semester_bounds,
    is_leap_year,
    is_valid_date,
    normalize_amount,
    parse_cop,
    parse_date,
    round_currency,
    to_decimal,
)


def test_parse_and_validate_date():
    assert is_valid_date("2025-01-01")
    parsed = parse_date("2025-12-31")
    assert parsed == date(2025, 12, 31)


def test_days_between_inclusive():
    a = date(2025, 1, 1)
    b = date(2025, 1, 31)
    assert days_between_inclusive(a, b) == 31


def test_semester_helpers():
    s1, e1 = get_semester_bounds(date(2025, 3, 5))
    assert s1 == date(2025, 1, 1)
    assert e1 == date(2025, 6, 30)

    s2, e2 = get_semester_bounds(date(2025, 9, 1))
    assert s2 == date(2025, 7, 1)
    assert e2 == date(2025, 12, 31)

    assert get_semester(date(2025, 2, 1)) == 1
    assert get_semester(date(2025, 7, 1)) == 2
    assert days_in_semester(date(2025, 8, 15)) == 184


def test_leap_year_helpers():
    assert is_leap_year(2024)
    assert not is_leap_year(2025)
    assert days_in_year(2024) == 366
    assert days_in_year(2025) == 365


def test_business_day_calculations():
    start = date(2025, 7, 4)
    end = date(2025, 7, 10)
    holidays = {date(2025, 7, 7)}
    assert business_days_between(start, end, holidays=holidays) == 4

    result = add_business_days(start, 3, holidays=holidays)
    assert result == date(2025, 7, 10)


def test_currency_helpers():
    assert round_currency(1234.567, 2) == 1234.57
    assert to_decimal(1234) == Decimal("1234")
    assert normalize_amount("1234.5", ndigits=1) == Decimal("1234.5")


def test_format_and_parse_cop():
    formatted = format_cop(1234567.5, decimals=2)
    assert formatted == "$ 1.234.567,50"
    parsed = parse_cop(formatted)
    assert parsed == Decimal("1234567.50")
