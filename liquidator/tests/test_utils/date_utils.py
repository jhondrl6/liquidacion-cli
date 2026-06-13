from __future__ import annotations

from datetime import date, datetime



def parse_date(value: str) -> date:
    """Parsea una fecha ISO (YYYY-MM-DD) a date; lanza ValueError si es inválida."""
    return datetime.strptime(value, "%Y-%m-%d").date()


def is_valid_date(value: str) -> bool:
    try:
        parse_date(value)
        return True
    except Exception:
        return False


def days_between_inclusive(start: date, end: date) -> int:
    """Días entre fechas incluyendo ambos extremos (>= 1 si start <= end)."""
    return (end - start).days + 1


def get_semester_bounds(d: date) -> Tuple[date, date]:
    """Retorna (inicio_semestre, fin_semestre) para la fecha dada."""
    if d.month <= 6:
        start = date(d.year, 1, 1)
        end = date(d.year, 6, 30)
    else:
        start = date(d.year, 7, 1)
        end = date(d.year, 12, 31)
    return start, end
