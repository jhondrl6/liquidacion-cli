from datetime import date, timedelta

import pytest

from liquidator.legal import (
    PagoFueraDePlazoError,
    PlazosManager,
)


def test_calculate_fecha_limite_cesantias_periodica():
    manager = PlazosManager()
    fecha_corte = date(2025, 11, 15)
    limite = manager.calculate_fecha_limite("cesantias", fecha_corte)
    assert limite == date(2026, 2, 14)


def test_validar_pago_inmediato_vacaciones():
    manager = PlazosManager()
    fecha_retiro = date(2025, 11, 15)
    with pytest.raises(PagoFueraDePlazoError):
        manager.validar_fecha_pago(
            "vacaciones",
            fecha_referencia=fecha_retiro,
            fecha_pago=fecha_retiro + timedelta(days=1),
        )


def test_aplica_a_modo_case_insensitive():
    manager = PlazosManager()
    assert manager.aplica_a_modo("cesantias", "periodica")
    assert not manager.aplica_a_modo("vacaciones", "periodica")
