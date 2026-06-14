from .currency_utils import (
    format_cop,
    format_currency,
    normalize_amount,
    parse_cop,
    round_currency,
    to_decimal,
)
from .date_utils import (
    add_business_days_date,
    business_days_between_date,
    calculate_days_between,
    calculate_years_of_service,
    days_between_inclusive_date,
    days_in_semester,
    days_in_year,
    get_current_year,
    get_semester,
    get_semester_bounds,
    is_leap_year,
    is_valid_date,
    # --- date-aware helpers (R-OP-06 fix) ---
    parse_date,
)
from .error_handler import (
    ContractError,
    DateError,
    LiquidacionError,
    ParamsError,
    SalaryError,
    ValidationError,
    ValidationOutput,
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
