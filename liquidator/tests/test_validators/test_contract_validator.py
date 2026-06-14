import pytest

from liquidator.utils import ContractError
from liquidator.validators import validate_contract


def test_validate_contract_ok():
    warnings = validate_contract({"tipo_contrato": "indefinido"})
    assert warnings == []


def test_validate_contract_reject_prestacion():
    with pytest.raises(ContractError):
        validate_contract({"tipo_contrato": "prestación_servicios"})
