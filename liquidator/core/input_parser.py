import json
from typing import Any


def parse_input_file(file_path: str) -> dict[str, Any]:
    """
    Parse input data from a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Parsed input data as dictionary
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {file_path}") from None
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in input file {file_path}: {e}") from e


class InputParser:
    """Parser for liquidation input data."""

    def __init__(self):
        pass

    def parse(self, input_data: dict[str, Any] | str) -> dict[str, Any]:
        """
        Parse input data from dictionary or file path.

        Args:
            input_data: Either dictionary with data or path to JSON file

        Returns:
            Parsed input data
        """
        if isinstance(input_data, str):
            # Assume it's a file path
            return parse_input_file(input_data)
        elif isinstance(input_data, dict):
            return input_data
        else:
            raise ValueError(
                "Input data must be either a dictionary or a file path string"
            )

    def validate_structure(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate and normalize input data structure.

        Args:
            input_data: Raw input data

        Returns:
            Normalized input data
        """
        # Set default values
        normalized = {
            "modo": input_data.get("modo", "PERIODICA"),
            "fecha_ingreso": input_data.get("fecha_ingreso"),
            "fecha_corte": input_data.get("fecha_corte"),
            "salario_mensual": input_data.get("salario_mensual", 0),
            "salarios_historicos": input_data.get("salarios_historicos", []),
            "comisiones_promedio_mensual": input_data.get(
                "comisiones_promedio_mensual", 0
            ),
            "horas_extras_promedio_mensual": input_data.get(
                "horas_extras_promedio_mensual", 0
            ),
            "bonificaciones_promedio_mensual": input_data.get(
                "bonificaciones_promedio_mensual", 0
            ),
            "reside_en_lugar_trabajo": input_data.get("reside_en_lugar_trabajo", False),
            "auxilio_conectividad": input_data.get("auxilio_conectividad", 0),
            "dias_vacaciones_pendientes": input_data.get(
                "dias_vacaciones_pendientes", 0
            ),
            "dias_vacaciones_para_compensar_dinero": input_data.get(
                "dias_vacaciones_para_compensar_dinero", 0
            ),
            "tipo_contrato": input_data.get("tipo_contrato", "indefinido"),
            "nombre": input_data.get("nombre", ""),
            "documento": input_data.get("documento", ""),
            "enforce_compliance": input_data.get("enforce_compliance", True),
            "compliance_policy": input_data.get("compliance_policy", "standard"),
            "human_override": input_data.get("human_override", False),
            "operator_id": input_data.get("operator_id", ""),
            "override_reason": input_data.get("override_reason", ""),
        }

        return normalized
