import pytest

from liquidator.utils import DateError
from liquidator.validators import validate_dates


def test_validate_dates_ok():
    warnings = validate_dates(
        {
            "fecha_ingreso": "2025-01-01",
            "fecha_corte": "2025-01-31",
        }
    )
    assert isinstance(warnings, list)


def test_validate_dates_invalid_order():
    with pytest.raises(DateError):
        validate_dates(
            {
                "fecha_ingreso": "2025-02-01",
                "fecha_corte": "2025-01-31",
            }
        )
