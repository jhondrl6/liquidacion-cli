"""
Tests unitarios para IndemnizacionCalculator.calculate_indemnizacion_preaviso
(Tarea 2.B-cuater, Fase 2, S30 — Art. 46 CST)

Fórmula: indemnización = (SBL / 30) × dias_faltantes
dias_faltantes = max(0, 30 - dias_preaviso_efectivos)

Reparos cerrados:
  (a) Art. 46 CST verificado verbatim en SUIN (2026-06-14).
  (b) Indemnización preaviso = renglón SEPARADO de Art. 64.
  (c) Preaviso contractual (pacto > 30d) NO se implementa en v2.0.
"""

import pytest
from decimal import Decimal
from liquidator.calculators.indemnizacion_calculator import IndemnizacionCalculator


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def params_2026():
    """Params mínimos para IndemnizacionCalculator (2026)."""
    return {
        "SMMLV": 1750905,
        "TOPE_INDEMNIZACION_SMMLV": 20,
        "LIMITE_AUXILIO": 2847000,
        "REDONDEO": 0,
    }


@pytest.fixture
def calc(params_2026):
    return IndemnizacionCalculator(params_2026)


# ---------------------------------------------------------------------------
# Clase 1: TestRegresionCanonica — happy path y regresión
# ---------------------------------------------------------------------------

class TestRegresionCanonica:
    """Happy-path tests: cálculo correcto de la fórmula Art. 46 CST."""

    def test_preaviso_cero_dias(self, calc):
        """Sin preaviso (0 días) → faltan 30 días."""
        r = calc.calculate_indemnizacion_preaviso(sbl=2_200_000, dias_preaviso_efectivos=0)
        assert r["aplica"] is True
        assert r["dias_faltantes"] == 30
        assert r["valor"] == 2_200_000  # (2_200_000 / 30) * 30 = 2_200_000
        assert r["norma"] == "Art. 46 CST"

    def test_preaviso_10_dias(self, calc):
        """10 días de preaviso → faltan 20 días."""
        r = calc.calculate_indemnizacion_preaviso(sbl=2_200_000, dias_preaviso_efectivos=10)
        assert r["dias_faltantes"] == 20
        # (2_200_000 / 30) * 20 = 1_466_666.67 → ROUND_HALF_UP = 1_466_667
        assert r["valor"] == 1_466_667

    def test_preaviso_30_dias_exacto(self, calc):
        """30 días de preaviso → suficiente, no aplica."""
        r = calc.calculate_indemnizacion_preaviso(sbl=2_200_000, dias_preaviso_efectivos=30)
        assert r["aplica"] is False
        assert r["valor"] == 0
        assert r["dias_faltantes"] == 0

    def test_preaviso_mayor_30_dias(self, calc):
        """35 días de preaviso → suficiente, no aplica."""
        r = calc.calculate_indemnizacion_preaviso(sbl=2_200_000, dias_preaviso_efectivos=35)
        assert r["aplica"] is False
        assert r["valor"] == 0


# ---------------------------------------------------------------------------
# Clase 2: TestPreavisoReglasExito — distintos escenarios válidos
# ---------------------------------------------------------------------------

class TestPreavisoReglasExito:
    """Casos válidos con diferentes SBL y días de preaviso."""

    def test_smmlv_2026(self, calc):
        """SBL = SMMLV 2026, 15 días de preaviso."""
        r = calc.calculate_indemnizacion_preaviso(sbl=1_750_905, dias_preaviso_efectivos=15)
        assert r["dias_faltantes"] == 15
        # (1_750_905 / 30) * 15 = 875_452.5 → ROUND_HALF_UP = 875_453
        assert r["valor"] == 875_453
        assert r["aplica"] is True

    def test_1_dia_preaviso(self, calc):
        """1 día de preaviso → faltan 29 días."""
        r = calc.calculate_indemnizacion_preaviso(sbl=3_000_000, dias_preaviso_efectivos=1)
        assert r["dias_faltantes"] == 29
        # (3_000_000 / 30) * 29 = 2_900_000
        assert r["valor"] == 2_900_000

    def test_29_dias_preaviso(self, calc):
        """29 días de preaviso → falta 1 día."""
        r = calc.calculate_indemnizacion_preaviso(sbl=2_200_000, dias_preaviso_efectivos=29)
        assert r["dias_faltantes"] == 1
        # (2_200_000 / 30) * 1 = 73_333.33 → ROUND_HALF_UP = 73_333
        assert r["valor"] == 73_333

    def test_sbl_alto(self, calc):
        """SBL alto (10M), 20 días de preaviso."""
        r = calc.calculate_indemnizacion_preaviso(sbl=10_000_000, dias_preaviso_efectivos=20)
        assert r["dias_faltantes"] == 10
        # (10_000_000 / 30) * 10 = 3_333_333.33 → ROUND_HALF_UP = 3_333_333
        assert r["valor"] == 3_333_333


# ---------------------------------------------------------------------------
# Clase 3: TestPreavisoReglasFallo — validación defensiva
# ---------------------------------------------------------------------------

class TestPreavisoReglasFallo:
    """Casos que deben levantar ValueError."""

    def test_sbl_cero(self, calc):
        with pytest.raises(ValueError, match="positivo"):
            calc.calculate_indemnizacion_preaviso(sbl=0, dias_preaviso_efectivos=10)

    def test_sbl_negativo(self, calc):
        with pytest.raises(ValueError, match="positivo"):
            calc.calculate_indemnizacion_preaviso(sbl=-100, dias_preaviso_efectivos=10)

    def test_dias_negativos(self, calc):
        with pytest.raises(ValueError, match="negativo"):
            calc.calculate_indemnizacion_preaviso(sbl=2_200_000, dias_preaviso_efectivos=-5)


# ---------------------------------------------------------------------------
# Clase 4: TestPreavisoConsistencia — fórmula y campos del dict
# ---------------------------------------------------------------------------

class TestPreavisoConsistencia:
    """Verificar consistencia de la fórmula y campos del resultado."""

    def test_formula_texto(self, calc):
        """El campo formula contiene la fórmula legible."""
        r = calc.calculate_indemnizacion_preaviso(sbl=2_200_000, dias_preaviso_efectivos=0)
        assert "2,200,000" in r["formula"]
        assert "30" in r["formula"]

    def test_evidencia_legal_presente(self, calc):
        """Campo evidencia_legal presente cuando aplica."""
        r = calc.calculate_indemnizacion_preaviso(sbl=2_200_000, dias_preaviso_efectivos=0)
        assert "evidencia_legal" in r
        assert "Art. 46" in r["evidencia_legal"]

    def test_evidencia_legal_ausente_si_no_aplica(self, calc):
        """Campo evidencia_legal NO presente si preaviso suficiente."""
        r = calc.calculate_indemnizacion_preaviso(sbl=2_200_000, dias_preaviso_efectivos=30)
        assert "evidencia_legal" not in r

    def test_redondeo_half_up(self, calc):
        """Verificar ROUND_HALF_UP: SBL 2_200_001 con 1 día faltante."""
        # (2_200_001 / 30) * 1 = 73_333.3667 → ROUND_HALF_UP = 73_333
        r = calc.calculate_indemnizacion_preaviso(sbl=2_200_001, dias_preaviso_efectivos=29)
        assert r["valor"] == 73_333

    def test_sbl_utilizado_es_entero(self, calc):
        r = calc.calculate_indemnizacion_preaviso(sbl=2_200_000, dias_preaviso_efectivos=0)
        assert isinstance(r["sbl_utilizado"], int)
        assert r["sbl_utilizado"] == 2_200_000


# ---------------------------------------------------------------------------
# Clase 5: TestReparosAddendumCerrados — reparos bloqueantes verificados
# ---------------------------------------------------------------------------

class TestReparosAddendumCerrados:
    """Verificar que los reparos del addendum preaviso están cerrados."""

    def test_no_referencias_art_64_en_calculo_preaviso(self, calc):
        """Reparo (b): preaviso NO se acumula con Art. 64.
        El método NO debe mencionar Art. 64 como fuente del cálculo."""
        r = calc.calculate_indemnizacion_preaviso(sbl=2_200_000, dias_preaviso_efectivos=10)
        assert "Art. 64" not in r.get("norma", "")
        assert "Art. 46" in r.get("norma", "")

    def test_art_46_en_norma(self, calc):
        """Reparo (a): Art. 46 CST presente como norma de referencia."""
        r = calc.calculate_indemnizacion_preaviso(sbl=2_200_000, dias_preaviso_efectivos=0)
        assert "Art. 46 CST" in r["norma"]
