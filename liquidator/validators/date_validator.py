from __future__ import annotations

from datetime import date
from typing import Dict, List, Tuple

from liquidator.utils import DateError, parse_date, days_between_inclusive


def _extract_dates(input_data: Dict) -> Tuple[date, date]:
    try:
        fi = parse_date(input_data.get("fecha_ingreso"))
        fc = parse_date(input_data.get("fecha_corte"))
    except Exception as exc:
        raise DateError(f"Fechas inválidas: {exc}")
    return fi, fc


def validate_dates(input_data: Dict) -> List[str]:
    """Valida formato y coherencia temporal de fechas. Retorna advertencias."""
    warnings: List[str] = []
    fi, fc = _extract_dates(input_data)

    if fi > fc:
        raise DateError("fecha_ingreso no puede ser posterior a fecha_corte.")

    dias = days_between_inclusive(fi, fc)
    if dias <= 0:
        raise DateError("El periodo debe tener al menos 1 día.")

    # Advertencias por periodos extremadamente largos o cortos
    if dias > 366 + 31:  # período mayor a ~13 meses
        warnings.append("Periodo inusualmente largo; verifique fechas de corte.")

    return warnings
