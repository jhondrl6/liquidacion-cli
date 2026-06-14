from typing import Any


class ValidationError(Exception):
    pass


class ContractError(ValidationError):
    pass


class DateError(ValidationError):
    pass


class SalaryError(ValidationError):
    pass


class LiquidacionError(Exception):
    """Base exception for liquidation errors"""

    pass


class ParamsError(LiquidacionError):
    """Exception for parameters-related errors"""

    pass


class ValidationOutput:
    """Standard output format for validation results"""

    def __init__(self, is_valid: bool, errors: list[Any] | None = None, warnings: list[Any] | None = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
