from .date_utils import (
    get_current_year,
    calculate_days_between,
    calculate_years_of_service,
    is_valid_date,
    days_in_semester,
    days_in_year,
    is_leap_year,
    get_semester,
    get_semester_bounds,
    # --- date-aware helpers (R-OP-06 fix) ---
    parse_date,
    days_between_inclusive_date,
    business_days_between_date,
    add_business_days_date,
)
from .currency_utils import (
    round_currency,
    format_currency,
    format_cop,
    normalize_amount,
    parse_cop,
    to_decimal,
)
from .error_handler import (
    LiquidacionError,
    ContractError,
    ParamsError,
    ValidationOutput,
    DateError,
    SalaryError,
    ValidationError,
)

# ------------------------------------------------------------------
# Aliases for backward compatibility — point to the date-aware
# implementations that the test suite expects (R-OP-06 fix).
# ------------------------------------------------------------------
add_business_days = add_business_days_date
days_between_inclusive = days_between_inclusive_date
business_days_between = business_days_between_date

__all__ = [
    "get_current_year",
    "calculate_days_between",
    "calculate_years_of_service",
    "is_valid_date",
    "days_in_semester",
    "days_in_year",
    "is_leap_year",
    "get_semester",
    "get_semester_bounds",
    "parse_date",
    "days_between_inclusive_date",
    "business_days_between_date",
    "add_business_days_date",
    # Aliases (date-aware, replace old str-based ones)
    "add_business_days",
    "days_between_inclusive",
    "business_days_between",
    # Currency
    "round_currency",
    "format_currency",
    "format_cop",
    "normalize_amount",
    "parse_cop",
    "to_decimal",
    # Errors
    "LiquidacionError",
    "ContractError",
    "ParamsError",
    "ValidationOutput",
    "DateError",
    "SalaryError",
    "ValidationError",
]
