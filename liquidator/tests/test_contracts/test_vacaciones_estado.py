"""Tests de VacacionesEstado (Tarea 1.C-ter — addendum finiquito/vacaciones).

Cubre: creación mínima, validación de consistencia, fracciones de día,
valores negativos, integración con LiquidacionInput.
"""

import pytest
from decimal import Decimal
from pydantic import ValidationError

from liquidator.contracts.input_model import VacacionesEstado, PeriodoDisfrute


class TestVacacionesEstadoMinimo:
    """Creación mínima de VacacionesEstado."""

    def test_minimo_pendientes_7_5(self):
        """Caso real: 7.5 días pendientes (fracción legal en CST)."""
        v = VacacionesEstado(dias_pendientes=Decimal("7.5"))
        assert v.dias_pendientes == Decimal("7.5")
        assert v.dias_disfrutados == Decimal(0)
        assert v.dias_causados_proporcionales is None
        assert v.fechas_disfrute is None

    def test_minimo_cero_pendientes(self):
        """Todas las vacaciones disfrutadas: 0 pendientes."""
        v = VacacionesEstado(dias_pendientes=Decimal("0"))
        assert v.dias_pendientes == Decimal("0")
        assert v.dias_disfrutados == Decimal(0)


class TestVacacionesEstadoConsistencia:
    """Validación de consistencia entre causados/disfrutados/pendientes."""

    def test_pasa_con_causados_ok(self):
        """dias_pendientes <= dias_causados - dias_disfrutados."""
        v = VacacionesEstado(
            dias_causados_proporcionales=Decimal("10"),
            dias_disfrutados=Decimal("2"),
            dias_pendientes=Decimal("8"),
        )
        assert v.dias_pendientes == Decimal("8")

    def test_pasa_causados_exacto(self):
        """Límite exacto: causados=15, disfrutados=0, pendientes=15."""
        v = VacacionesEstado(
            dias_causados_proporcionales=Decimal("15"),
            dias_disfrutados=Decimal("0"),
            dias_pendientes=Decimal("15"),
        )
        assert v.dias_pendientes == Decimal("15")

    def test_pasa_causados_discretos(self):
        """Sin dias_causados: no se ejecuta el validador."""
        v = VacacionesEstado(
            dias_disfrutados=Decimal("5"),
            dias_pendientes=Decimal("100"),
        )
        assert v.dias_pendientes == Decimal("100")

    def test_rechaza_pendientes_excedidos(self):
        """10 > 5 - 2 = 3 → ValidationError."""
        with pytest.raises(ValidationError, match="excede el máximo"):
            VacacionesEstado(
                dias_causados_proporcionales=Decimal("5"),
                dias_disfrutados=Decimal("2"),
                dias_pendientes=Decimal("10"),
            )

    def test_rechaza_pendientes_excedidos_por_un_decimal(self):
        """Exceso por fracción: 8.1 > 10 - 2 = 8 → rechaza."""
        with pytest.raises(ValidationError, match="excede el máximo"):
            VacacionesEstado(
                dias_causados_proporcionales=Decimal("10"),
                dias_disfrutados=Decimal("2"),
                dias_pendientes=Decimal("8.1"),
            )

    def test_pasa_causados_none_no_valida(self):
        """causados=None desactiva la validación de consistencia."""
        v = VacacionesEstado(
            dias_disfrutados=Decimal("0"),
            dias_pendientes=Decimal("999"),
        )
        assert v.dias_pendientes == Decimal("999")


class TestVacacionesEstadoFracciones:
    """Fracciones de día de vacaciones (legales en CST)."""

    def test_acepta_medio_dia(self):
        v = VacacionesEstado(dias_pendientes=Decimal("0.5"))
        assert v.dias_pendientes == Decimal("0.5")

    def test_acepta_fraccion_compleja(self):
        v = VacacionesEstado(dias_pendientes=Decimal("3.25"))
        assert v.dias_pendientes == Decimal("3.25")

    def test_acepta_disfrutados_fraccion(self):
        v = VacacionesEstado(
            dias_causados_proporcionales=Decimal("15"),
            dias_disfrutados=Decimal("7.5"),
            dias_pendientes=Decimal("7.5"),
        )
        assert v.dias_pendientes == Decimal("7.5")


class TestVacacionesEstadoNegativos:
    """Rechazo de valores negativos."""

    def test_pendientes_negativo_falla(self):
        with pytest.raises(ValidationError):
            VacacionesEstado(dias_pendientes=Decimal("-1"))

    def test_pendientes_negativo_fraccion_falla(self):
        with pytest.raises(ValidationError):
            VacacionesEstado(dias_pendientes=Decimal("-0.01"))


class TestPeriodoDisfrute:
    """Modelo PeriodoDisfrute."""

    def test_creacion_minima(self):
        from datetime import date

        p = PeriodoDisfrute(desde=date(2025, 1, 15), hasta=date(2025, 2, 1))
        assert p.desde == date(2025, 1, 15)
        assert p.hasta == date(2025, 2, 1)


class TestVacacionesEstadoConFechas:
    """VacacionesEstado con historial de fechas_disfrute."""

    def test_con_fechas_disfrute(self):
        from datetime import date

        v = VacacionesEstado(
            dias_pendientes=Decimal("5"),
            fechas_disfrute=[
                PeriodoDisfrute(desde=date(2025, 6, 1), hasta=date(2025, 6, 15)),
                PeriodoDisfrute(desde=date(2025, 12, 20), hasta=date(2025, 12, 31)),
            ],
        )
        assert len(v.fechas_disfrute) == 2
        assert v.fechas_disfrute[0].desde == date(2025, 6, 1)
        assert v.fechas_disfrute[1].hasta == date(2025, 12, 31)
