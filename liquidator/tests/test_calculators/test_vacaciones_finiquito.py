"""Tests para vacaciones compensadas en finiquito (Tarea 2.B-ter).

Fórmula: (SBL / 30) × dias_pendientes (Art. 189-190 CST).
Redondeo: ROUND_HALF_UP, resultado entero en COP.
"""

import inspect
from decimal import Decimal

import pytest

from liquidator.calculators.prestaciones_calculator import PrestacionesCalculator


@pytest.fixture
def params():
    """Parámetros mínimos para instanciar el calculador."""
    return {
        "DIAS_BASE": 360.0,
        "TASA_INT_CESANTIAS": 0.12,
        "REDONDEO": 0,
        "SMMLV": 1750905,
    }


@pytest.fixture
def calc(params):
    return PrestacionesCalculator(params)


class TestVacacionesCompensadasFiniquito:
    """Tests unitarios para la fórmula Art. 189-190 CST."""

    def test_vacaciones_7_5_dias_sbl_2_200_000(self, calc):
        """Caso real del addendum: 7.5 días, SBL 2.200.000 → $550.000."""
        r = calc.calculate_vacaciones_compensadas_finiquito(
            sbl=Decimal("2200000"), dias_pendientes=Decimal("7.5")
        )
        assert r["valor"] == 550000
        assert r["dias"] == 7.5
        assert r["obligatorio_en_finiquito"] is True
        assert "Art. 189" in r["evidencia_legal"]

    def test_vacaciones_cero_dias_retorna_cero(self, calc):
        """dias_pendientes=0 → valor = 0."""
        r = calc.calculate_vacaciones_compensadas_finiquito(
            sbl=Decimal("2200000"), dias_pendientes=Decimal("0")
        )
        assert r["valor"] == 0
        assert r["dias"] == 0.0

    def test_vacaciones_dia_entero_sbl_1_750_905(self, calc):
        """Sanity check: 1 día con SMMLV 2026 → 58.364 (1.750.905/30 ≈ 58.363.5)."""
        r = calc.calculate_vacaciones_compensadas_finiquito(
            sbl=Decimal("1750905"), dias_pendientes=Decimal("1")
        )
        # 1.750.905 / 30 = 58.363,5 → ROUND_HALF_UP = 58.364
        assert r["valor"] == 58364

    def test_vacaciones_15_dias_sbl_2_000_000(self, calc):
        """15 días con SBL 2.000.000 → 1.000.000 (exacto)."""
        r = calc.calculate_vacaciones_compensadas_finiquito(
            sbl=Decimal("2000000"), dias_pendientes=Decimal("15")
        )
        assert r["valor"] == 1000000  # (2.000.000/30)*15 = 66.666,67*15 = 1.000.000

    def test_vacaciones_fraccion_dia_sbl_1_500_000(self, calc):
        """3.3 días con SBL 1.500.000 → 165.000 exacto."""
        r = calc.calculate_vacaciones_compensadas_finiquito(
            sbl=Decimal("1500000"), dias_pendientes=Decimal("3.3")
        )
        # (1.500.000/30) × 3.3 = 50.000 × 3.3 = 165.000
        assert r["valor"] == 165000

    def test_vacaciones_redondeo_half_up_a_favor_trabajador(self, calc):
        """Redondeo HALF_UP: 0.5 pesos → 1 peso a favor del trabajador."""
        # SBL = 30.001 → valor diario = 1.000,0333... × 0.5 = 500,0167 → 500
        r = calc.calculate_vacaciones_compensadas_finiquito(
            sbl=Decimal("30001"), dias_pendientes=Decimal("0.5")
        )
        # 30.001/30 = 1.000,033... × 0.5 = 500,0167 → ROUND_HALF_UP = 500
        assert r["valor"] == 500

    def test_vacaciones_no_incluye_auxilio_transporte(self, calc):
        """El SBL para vacaciones excluye recargos/HHE (Art. 185).
        Verificamos que la firma del método solo acepta sbl y dias_pendientes
        como parámetros — sin auxilio_transporte ni recargo.
        """
        sig = inspect.signature(
            PrestacionesCalculator.calculate_vacaciones_compensadas_finiquito
        )
        params = list(sig.parameters.keys())
        assert "sbl" in params
        assert "dias_pendientes" in params
        assert "auxilio_transporte" not in params
        assert "recargo" not in params
        assert "horas_extras" not in params

    def test_formula_explicita_en_resultado(self, calc):
        """El resultado debe documentar la fórmula utilizada."""
        r = calc.calculate_vacaciones_compensadas_finiquito(
            sbl=Decimal("1000000"), dias_pendientes=Decimal("3")
        )
        assert r["formula"] == "SBL / 30 × días_pendientes"
        assert r["concepto"] == "Vacaciones compensadas (finiquito)"

    def test_params_usados_reflejan_input(self, calc):
        """params_usados debe contener los valores exactos recibidos."""
        r = calc.calculate_vacaciones_compensadas_finiquito(
            sbl=Decimal("2500000"), dias_pendientes=Decimal("6.25")
        )
        assert r["params_usados"]["SBL"] == 2500000
        assert r["params_usados"]["dias_pendientes"] == 6.25
