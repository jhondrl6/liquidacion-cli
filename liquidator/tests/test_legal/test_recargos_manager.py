from datetime import date

import pytest

from liquidator.legal import RecargoError, RecargosManager


def build_manager() -> RecargosManager:
    return RecargosManager({"FECHA_APLICACION_RECARGO_DOMINICAL": "2025-07-01"})


def test_recargo_dominical_transicion_fecha():
    manager = build_manager()
    assert manager.get_recargo_dominical(date(2025, 6, 30)) == pytest.approx(0.75)
    assert manager.get_recargo_dominical(date(2025, 7, 1)) == pytest.approx(0.80)


def test_calcular_valor_recargo_festivo_nocturno():
    manager = build_manager()
    valor = manager.calcular_valor_recargo(
        base=100_000,
        tipo="festivo",
        fecha=date(2025, 8, 1),
        es_nocturno=True,
    )
    # recargo nocturno festivo por defecto 110%
    assert valor == pytest.approx(110_000)


def test_calcular_valor_recargo_base_negativa():
    manager = build_manager()
    with pytest.raises(RecargoError):
        manager.calcular_valor_recargo(
            base=-10,
            tipo="dominical",
            fecha=date(2025, 8, 1),
        )
