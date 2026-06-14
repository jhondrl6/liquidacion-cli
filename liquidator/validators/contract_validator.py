from __future__ import annotations

from liquidator.utils import ContractError

VALID_CONTRACTS = {"indefinido", "fijo"}
REJECTED_CONTRACTS = {"prestación_servicios", "prestacion_servicios", "servicios"}


def validate_contract(input_data: dict) -> list[str]:
    """Valida el tipo de contrato. Lanza ContractError si es prestación de servicios.

    Retorna lista de advertencias (puede estar vacía).
    """
    warnings: list[str] = []
    tipo_val = input_data.get("tipo_contrato", "")
    tipo = str(tipo_val).strip().lower() if tipo_val is not None else ""
    if not tipo:
        raise ContractError("tipo_contrato es requerido.")

    if tipo in REJECTED_CONTRACTS:
        raise ContractError(
            "Contrato de prestación de servicios no aplica a prestaciones legales."
        )

    if tipo not in VALID_CONTRACTS:
        warnings.append(
            f"tipo_contrato '{tipo}' no reconocido. Se esperan: {', '.join(sorted(VALID_CONTRACTS))}."
        )

    return warnings
