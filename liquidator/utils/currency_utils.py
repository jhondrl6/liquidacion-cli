from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation


def to_decimal(value: float | int | str | Decimal) -> Decimal:
    """Normaliza un valor numérico a ``Decimal`` evitando errores binarios."""

    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"Valor monetario inválido: {value!r}") from exc


def round_currency(value: float | int, ndigits: int = 0) -> float:
    """Redondea un valor monetario siguiendo la estrategia estándar bancaria."""

    quantize_str = "1" if ndigits == 0 else f"1.{'0' * ndigits}"
    decimal_value = to_decimal(value).quantize(
        Decimal(quantize_str), rounding=ROUND_HALF_UP
    )
    return float(decimal_value)


def normalize_amount(value: float | int | str | Decimal, ndigits: int = 0) -> Decimal:
    """Devuelve un ``Decimal`` redondeado al número de decimales indicado."""

    quantize_str = "1" if ndigits == 0 else f"1.{'0' * ndigits}"
    return to_decimal(value).quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)


def format_cop(
    value: float | int | Decimal,
    *,
    symbol: bool = True,
    decimals: int = 0,
    use_nbsp: bool = False,
) -> str:
    """Formatea un valor como moneda colombiana.

    Args:
        value: monto a formatear.
        symbol: si ``True`` antepone ``$``.
        decimals: número de decimales visibles.
        use_nbsp: intercambia el espacio por ``\u00a0`` para evitar saltos de línea.
    """

    amount = normalize_amount(value, ndigits=decimals)
    pattern = f"{{:,.{decimals}f}}"
    raw = pattern.format(amount)
    integer_part, _, fractional_part = raw.partition(".")
    integer_part = integer_part.replace(",", ".")
    if decimals > 0:
        formatted = f"{integer_part},{fractional_part}"
    else:
        formatted = integer_part

    if symbol:
        space = "\u00a0" if use_nbsp else " "
        return f"${space}{formatted}"
    return formatted


def parse_cop(value: str) -> Decimal:
    """Convierte una cadena con formato COP a ``Decimal``.

    Ejemplo: ``"$ 1.234.567,89"`` → ``Decimal('1234567.89')``
    """

    if not isinstance(value, str):
        raise TypeError("parse_cop solo acepta cadenas")
    cleaned = (
        value.replace("$", "")
        .replace("\u00a0", " ")
        .replace(".", "")
        .replace(" ", "")
        .replace(",", ".")
    )
    return to_decimal(cleaned)


def format_currency(value: float | int) -> str:
    """
    Formatea un valor como moneda colombiana (alias de format_cop).
    """
    return format_cop(value)
