import pytest

from liquidator.validators import validate_input
from liquidator.utils import ValidationError


def test_validate_input_ok():
    params = {"SMMLV": 1423500, "LIMITE_AUXILIO": 2847000}
    data = {
        "modo": "PERIODICA",
        "fecha_ingreso": "2025-01-01",
        "fecha_corte": "2025-01-31",
        "salario_mensual": 2000000,
        "tipo_contrato": "indefinido",
    }
    warnings, notes = validate_input(data, params)
    assert isinstance(warnings, list)
    assert isinstance(notes, list)


def test_validate_input_missing_fields():
    params = {"SMMLV": 1423500, "LIMITE_AUXILIO": 2847000}
    data = {"modo": "PERIODICA"}
    with pytest.raises(ValidationError):
        validate_input(data, params)
