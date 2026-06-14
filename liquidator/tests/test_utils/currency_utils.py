from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal


def round_currency(value: float | int, ndigits: int = 0) -> int | float:
    q = Decimal(10) ** -ndigits
    rounded = Decimal(str(value)).quantize(q, rounding=ROUND_HALF_UP)
    return int(rounded) if ndigits == 0 else float(rounded)


def format_cop(value: int | float) -> str:
    return f"$ {int(round_currency(value, 0)):,}".replace(",", ".")
