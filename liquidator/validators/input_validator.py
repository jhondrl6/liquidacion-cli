from __future__ import annotations

from typing import Dict, List, Tuple

from liquidator.validators.contract_validator import validate_contract
from liquidator.validators.date_validator import validate_dates
from liquidator.validators.salary_validator import validate_salary_components
from liquidator.utils import ValidationError


REQUIRED_FIELDS = [
    "modo",
    "fecha_ingreso",
    "fecha_corte",
    "salario_mensual",
    "tipo_contrato",
]


def _validate_required(input_data: Dict) -> None:
    missing = [f for f in REQUIRED_FIELDS if f not in input_data]
    if missing:
        raise ValidationError(
            f"Campos requeridos ausentes: {', '.join(missing)}"
        )


def validate_input(input_data: Dict, params: Dict) -> Tuple[List[str], List[str]]:
    """Validador compuesto de entrada.

    Retorna (warnings, notes) donde warnings son potencialmente 
    bloqueantes según política, y notes son observaciones informativas.
    """
    warnings: List[str] = []
    notes: List[str] = []

    _validate_required(input_data)

    modo = str(input_data.get("modo", "")).strip().upper()
    if modo not in {"PERIÓDICA", "PERIODICA", "FINIQUITO"}:
        raise ValidationError("modo debe ser 'PERIÓDICA'/'PERIODICA' o 'FINIQUITO'.")

    # Normalización simple de modo
    if modo == "PERIODICA":
        input_data["modo"] = "PERIÓDICA"

    # Validaciones específicas
    warnings += validate_contract(input_data)
    warnings += validate_dates(input_data)
    warnings += validate_salary_components(input_data, params)

    return warnings, notes
