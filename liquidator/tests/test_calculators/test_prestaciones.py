"""
Tests Unitarios - Calculador de Prestaciones Sociales
=====================================================

Tests exhaustivos para validar todos los cálculos de prestaciones
contra casos conocidos, casos de borde y normativa legal.

Author: Sistema de Liquidación de Nómina
Version: 1.0.0
"""

import pytest
from datetime import date
from decimal import Decimal
import sys
import os

# Agregar path del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from liquidator.calculators.prestaciones_calculator import PrestacionesCalculator


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def params_default():
    """Parámetros por defecto para 2025."""
    return {
        "SMMLV": 1423500,
        "AUXILIO_TRANS": 200000,
        "DIAS_BASE": 360.0,
        "TASA_INT_CESANTIAS": 0.12,
        "REDONDEO": 0,
    }


@pytest.fixture
def calculator(params_default):
    """Instancia del calculador con parámetros por defecto."""
    return PrestacionesCalculator(params_default)


# ============================================================================
# TESTS: calculate_dias_servicio
# ============================================================================


class TestCalculateDiasServicio:
    """Tests para el cálculo de días de servicio."""

    def test_año_completo(self, calculator):
        """Test año completo (365 días)."""
        dias = calculator.calculate_dias_servicio("2024-11-16", "2025-11-15")
        assert dias == 365

    def test_año_bisiesto(self, calculator):
        """Test año bisiesto (366 días)."""
        dias = calculator.calculate_dias_servicio("2024-01-01", "2024-12-31")
        assert dias == 366

    def test_semestre_completo(self, calculator):
        """Test semestre completo."""
        dias = calculator.calculate_dias_servicio("2025-01-01", "2025-06-30")
        assert dias == 181

    def test_un_dia(self, calculator):
        """Test un solo día."""
        dias = calculator.calculate_dias_servicio("2025-01-01", "2025-01-01")
        assert dias == 1

    def test_sin_incluir_dia_corte(self, calculator):
        """Test sin incluir día de corte."""
        dias = calculator.calculate_dias_servicio(
            "2025-01-01", "2025-01-10", incluir_dia_corte=False
        )
        assert dias == 9  # 10 - 1 = 9 días

    def test_fecha_invalida(self, calculator):
        """Test fecha con formato inválido."""
        with pytest.raises(ValueError, match="Formato de fecha inválido"):
            calculator.calculate_dias_servicio("2025/01/01", "2025-12-31")

    def test_fecha_corte_anterior(self, calculator):
        """Test fecha de corte anterior a ingreso."""
        with pytest.raises(ValueError, match="anterior a fecha de ingreso"):
            calculator.calculate_dias_servicio("2025-12-31", "2025-01-01")


# ============================================================================
# TESTS: calculate_cesantias
# ============================================================================


class TestCalculateCesantias:
    """Tests para el cálculo de cesantías."""

    def test_año_completo_caso_finca(self, calculator):
        """Test caso finca rural - año completo."""
        result = calculator.calculate_cesantias(
            sbl_general=2200000,
            dias_servicio=360,
            fecha_ingreso="2024-11-16",
            fecha_corte="2025-11-15",
        )

        assert result["valor"] == 2200000
        assert result["dias_liquidados"] == 360
        assert result["norma"] == "Art. 249-250 CST"
        assert "2026-02-14" in result["plazo_pago_legal"]

    def test_medio_año(self, calculator):
        """Test medio año (180 días)."""
        result = calculator.calculate_cesantias(
            sbl_general=1500000,
            dias_servicio=180,
            fecha_ingreso="2025-01-01",
            fecha_corte="2025-06-30",
        )

        # (1.500.000 × 180) / 360 = 750.000
        assert result["valor"] == 750000
        assert result["dias_liquidados"] == 180

    def test_periodo_parcial(self, calculator):
        """Test período parcial (90 días)."""
        result = calculator.calculate_cesantias(
            sbl_general=2000000,
            dias_servicio=90,
            fecha_ingreso="2025-01-01",
            fecha_corte="2025-03-31",
        )

        # (2.000.000 × 90) / 360 = 500.000
        assert result["valor"] == 500000

    def test_un_dia(self, calculator):
        """Test un solo día trabajado."""
        result = calculator.calculate_cesantias(
            sbl_general=1500000,
            dias_servicio=1,
            fecha_ingreso="2025-01-01",
            fecha_corte="2025-01-01",
        )

        # (1.500.000 × 1) / 360 = 4.166,67 ≈ 4.167
        assert result["valor"] in [4166, 4167]  # Tolerancia por redondeo

    def test_sbl_negativo(self, calculator):
        """Test SBL negativo (debe fallar)."""
        with pytest.raises(ValueError, match="debe ser positivo"):
            calculator.calculate_cesantias(
                sbl_general=-2000000,
                dias_servicio=360,
                fecha_ingreso="2024-11-16",
                fecha_corte="2025-11-15",
            )

    def test_dias_negativos(self, calculator):
        """Test días negativos (debe fallar)."""
        with pytest.raises(ValueError, match="no pueden ser negativos"):
            calculator.calculate_cesantias(
                sbl_general=2000000,
                dias_servicio=-10,
                fecha_ingreso="2024-11-16",
                fecha_corte="2025-11-15",
            )

    def test_cesantias_con_decimales(self, calculator):
        """Test cesantías que resultan en decimales."""
        result = calculator.calculate_cesantias(
            sbl_general=1423500,  # SMMLV 2025
            dias_servicio=100,
            fecha_ingreso="2025-01-01",
            fecha_corte="2025-04-10",
        )

        # (1.423.500 × 100) / 360 = 395.416,67 ≈ 395.417
        expected = int(
            Decimal("395416.67").quantize(Decimal("1"), rounding="ROUND_HALF_UP")
        )
        assert abs(result["valor"] - expected) <= 1

    def test_plazo_pago_legal_año_siguiente(self, calculator):
        """Test que plazo de pago sea 14-Feb del año siguiente."""
        result = calculator.calculate_cesantias(
            sbl_general=2000000,
            dias_servicio=360,
            fecha_ingreso="2024-01-01",
            fecha_corte="2024-12-31",
        )

        assert result["plazo_pago_legal"] == "2025-02-14"

    def test_metadata_presente(self, calculator):
        """Test que metadata esté completa."""
        result = calculator.calculate_cesantias(
            sbl_general=2000000,
            dias_servicio=360,
            fecha_ingreso="2024-11-16",
            fecha_corte="2025-11-15",
        )

        assert "metadata" in result
        assert "fecha_ingreso" in result["metadata"]
        assert "fecha_corte" in result["metadata"]
        assert "base_dias" in result["metadata"]
        assert result["metadata"]["base_dias"] == 360.0


# ============================================================================
# TESTS: calculate_intereses_cesantias
# ============================================================================


class TestCalculateInteresesCesantias:
    """Tests para el cálculo de intereses sobre cesantías."""

    def test_año_completo_caso_finca(self, calculator):
        """Test caso finca rural - año completo."""
        result = calculator.calculate_intereses_cesantias(
            cesantias=2200000,
            dias_servicio=360,
            fecha_ingreso="2024-11-16",
            fecha_corte="2025-11-15",
        )

        # (2.200.000 × 360 × 0.12) / 360 = 264.000
        assert result["valor"] == 264000
        assert result["tasa_aplicada"] == 0.12
        assert result["norma"] == "Ley 50/1990 Art. 99"

    def test_medio_año(self, calculator):
        """Test medio año."""
        cesantias = 750000
        result = calculator.calculate_intereses_cesantias(
            cesantias=cesantias,
            dias_servicio=180,
            fecha_ingreso="2025-01-01",
            fecha_corte="2025-06-30",
        )

        # (750.000 × 180 × 0.12) / 360 = 45.000
        assert result["valor"] == 45000
        assert result["cesantias_base"] == cesantias

    def test_tasa_12_porciento(self, calculator):
        """Test que la tasa sea exactamente 12%."""
        result = calculator.calculate_intereses_cesantias(
            cesantias=1000000,
            dias_servicio=360,
            fecha_ingreso="2025-01-01",
            fecha_corte="2025-12-31",
        )

        # Con 360 días, intereses deben ser exactamente 12% de cesantías
        assert result["valor"] == 120000
        assert result["tasa_aplicada"] == 0.12

    def test_un_dia(self, calculator):
        """Test un solo día."""
        result = calculator.calculate_intereses_cesantias(
            cesantias=1000000,
            dias_servicio=1,
            fecha_ingreso="2025-01-01",
            fecha_corte="2025-01-01",
        )

        # (1.000.000 × 1 × 0.12) / 360 = 333,33 ≈ 333
        assert result["valor"] in [333, 334]

    def test_cesantias_cero(self, calculator):
        """Test con cesantías en cero."""
        result = calculator.calculate_intereses_cesantias(
            cesantias=0,
            dias_servicio=360,
            fecha_ingreso="2025-01-01",
            fecha_corte="2025-12-31",
        )

        assert result["valor"] == 0

    def test_cesantias_negativas(self, calculator):
        """Test cesantías negativas (debe fallar)."""
        with pytest.raises(ValueError, match="no pueden ser negativas"):
            calculator.calculate_intereses_cesantias(
                cesantias=-1000000,
                dias_servicio=360,
                fecha_ingreso="2025-01-01",
                fecha_corte="2025-12-31",
            )

    def test_plazo_pago_31_enero(self, calculator):
        """Test que plazo de pago sea 31-Ene del año siguiente."""
        result = calculator.calculate_intereses_cesantias(
            cesantias=2000000,
            dias_servicio=360,
            fecha_ingreso="2024-01-01",
            fecha_corte="2024-12-31",
        )

        assert result["plazo_pago_legal"] == "2025-01-31"

    def test_formula_documentada(self, calculator):
        """Test que la fórmula esté documentada en el resultado."""
        result = calculator.calculate_intereses_cesantias(
            cesantias=2000000,
            dias_servicio=180,
            fecha_ingreso="2025-01-01",
            fecha_corte="2025-06-30",
        )

        assert "formula" in result
        assert "2,000,000" in result["formula"]
        assert "180" in result["formula"]
        assert "0.12" in result["formula"]


# ============================================================================
# TESTS: calculate_dias_prima
# ============================================================================


class TestCalculateDiasPrima:
    """Tests para el cálculo de días de prima."""

    def test_primer_semestre_completo(self, calculator):
        """Test primer semestre completo."""
        dias, semestre = calculator.calculate_dias_prima("2025-01-01", "2025-06-30")

        assert dias == 181  # 1-Ene a 30-Jun = 181 días
        assert semestre == "primer_semestre"

    def test_segundo_semestre_completo(self, calculator):
        """Test segundo semestre completo."""
        dias, semestre = calculator.calculate_dias_prima("2025-07-01", "2025-12-31")

        assert dias == 184  # 1-Jul a 31-Dic = 184 días
        assert semestre == "segundo_semestre"

    def test_ingreso_mitad_primer_semestre(self, calculator):
        """Test ingreso a mitad del primer semestre."""
        dias, semestre = calculator.calculate_dias_prima("2025-03-15", "2025-06-30")

        # 15-Mar a 30-Jun = 108 días
        assert dias == 108
        assert semestre == "primer_semestre"

    def test_caso_finca_rural(self, calculator):
        """Test caso finca rural (ingreso 16-Nov-2024, corte 15-Nov-2025)."""
        # Este caso cruza dos semestres, debe tomar el del corte (segundo)
        dias, semestre = calculator.calculate_dias_prima("2024-11-16", "2025-11-15")

        # Corte en 15-Nov-2025 = segundo semestre
        # Desde 1-Jul-2025 hasta 15-Nov-2025 = 138 días
        assert semestre == "segundo_semestre"
        assert dias == 138

    def test_ingreso_despues_inicio_semestre(self, calculator):
        """Test ingreso después del inicio del semestre."""
        dias, semestre = calculator.calculate_dias_prima("2025-08-15", "2025-12-31")

        # 15-Ago a 31-Dic = 139 días
        assert dias == 139
        assert semestre == "segundo_semestre"

    def test_corte_mitad_semestre(self, calculator):
        """Test corte a mitad de semestre."""
        dias, semestre = calculator.calculate_dias_prima("2025-01-01", "2025-03-31")

        # 1-Ene a 31-Mar = 90 días (primer semestre)
        assert dias == 90
        assert semestre == "primer_semestre"

    def test_ingreso_y_corte_mismo_semestre(self, calculator):
        """Test ingreso y corte dentro del mismo semestre."""
        dias, semestre = calculator.calculate_dias_prima("2025-02-15", "2025-04-15")

        # 15-Feb a 15-Abr = 60 días
        assert dias == 60
        assert semestre == "primer_semestre"

    def test_ingreso_antes_del_semestre(self, calculator):
        """Test cuando ingreso es antes del inicio del semestre de corte."""
        dias, semestre = calculator.calculate_dias_prima("2024-01-01", "2025-06-30")

        # Todo el primer semestre de 2025
        assert dias == 181
        assert semestre == "primer_semestre"

    def test_un_dia_primer_semestre(self, calculator):
        """Test un solo día en primer semestre."""
        dias, semestre = calculator.calculate_dias_prima("2025-06-30", "2025-06-30")

        assert dias == 1
        assert semestre == "primer_semestre"

    def test_un_dia_segundo_semestre(self, calculator):
        """Test un solo día en segundo semestre."""
        dias, semestre = calculator.calculate_dias_prima("2025-07-01", "2025-07-01")

        assert dias == 1
        assert semestre == "segundo_semestre"


# ============================================================================
# TESTS: calculate_prima
# ============================================================================


class TestCalculatePrima:
    """Tests para el cálculo de prima de servicios."""

    def test_primer_semestre_completo(self, calculator):
        """Test primer semestre completo."""
        result = calculator.calculate_prima(
            sbl_prima=2200000, fecha_ingreso="2025-01-01", fecha_corte="2025-06-30"
        )

        # (2.200.000 × 181) / 360 = 1.105.555,56 ≈ 1.105.556
        expected = int(
            Decimal("1105555.56").quantize(Decimal("1"), rounding="ROUND_HALF_UP")
        )
        assert abs(result["valor"] - expected) <= 1
        assert result["dias_liquidados"] == 181
        assert result["semestre"] == "primer_semestre"
        assert result["plazo_pago_legal"] == "2025-06-30"

    def test_segundo_semestre_completo(self, calculator):
        """Test segundo semestre completo."""
        result = calculator.calculate_prima(
            sbl_prima=2200000, fecha_ingreso="2025-07-01", fecha_corte="2025-12-31"
        )

        # (2.200.000 × 184) / 360 = 1.124.444,44 ≈ 1.124.444
        expected = int(
            Decimal("1124444.44").quantize(Decimal("1"), rounding="ROUND_HALF_UP")
        )
        assert abs(result["valor"] - expected) <= 1
        assert result["semestre"] == "segundo_semestre"
        assert result["plazo_pago_legal"] == "2025-12-20"

    def test_caso_finca_rural_segundo_semestre(self, calculator):
        """Test caso finca rural - segundo semestre proporcional."""
        result = calculator.calculate_prima(
            sbl_prima=2200000, fecha_ingreso="2024-11-16", fecha_corte="2025-11-15"
        )

        # 138 días en segundo semestre 2025
        # (2.200.000 × 138) / 360 = 843.333,33 ≈ 843.333
        expected = int(
            Decimal("843333.33").quantize(Decimal("1"), rounding="ROUND_HALF_UP")
        )
        assert abs(result["valor"] - expected) <= 1
        assert result["dias_liquidados"] == 138

    def test_medio_semestre(self, calculator):
        """Test medio semestre (aproximadamente 90 días)."""
        result = calculator.calculate_prima(
            sbl_prima=1500000, fecha_ingreso="2025-01-01", fecha_corte="2025-03-31"
        )

        # (1.500.000 × 90) / 360 = 375.000
        assert result["valor"] == 375000
        assert result["dias_liquidados"] == 90

    def test_un_dia(self, calculator):
        """Test un solo día."""
        result = calculator.calculate_prima(
            sbl_prima=1500000, fecha_ingreso="2025-01-01", fecha_corte="2025-01-01"
        )

        # (1.500.000 × 1) / 360 = 4.166,67 ≈ 4.167
        assert result["valor"] in [4166, 4167]
        assert result["dias_liquidados"] == 1

    def test_cero_dias(self, calculator):
        """Test cuando no hay días en el semestre de corte."""
        # Ingreso después del semestre de corte
        result = calculator.calculate_prima(
            sbl_prima=2000000, fecha_ingreso="2025-07-01", fecha_corte="2025-06-30"
        )

        assert result["valor"] == 0
        assert result["dias_liquidados"] == 0
        assert "advertencia" in result["metadata"]

    def test_sbl_negativo(self, calculator):
        """Test SBL negativo (debe fallar)."""
        with pytest.raises(ValueError, match="debe ser positivo"):
            calculator.calculate_prima(
                sbl_prima=-2000000, fecha_ingreso="2025-01-01", fecha_corte="2025-06-30"
            )

    def test_proporcionalidad_metadata(self, calculator):
        """Test que metadata incluya proporcionalidad."""
        result = calculator.calculate_prima(
            sbl_prima=2000000, fecha_ingreso="2025-01-01", fecha_corte="2025-03-31"
        )

        assert "proporcionalidad" in result["metadata"]
        # 90 días / 180 días = 50%
        assert result["metadata"]["proporcionalidad"] == 50.0

    def test_norma_legal(self, calculator):
        """Test que incluya referencia legal correcta."""
        result = calculator.calculate_prima(
            sbl_prima=2000000, fecha_ingreso="2025-01-01", fecha_corte="2025-06-30"
        )

        assert result["norma"] == "Art. 306-308 CST"


# ============================================================================
# TESTS: calculate_all_prestaciones
# ============================================================================


class TestCalculateAllPrestaciones:
    """Tests para el cálculo de todas las prestaciones."""

    def test_caso_finca_completo(self, calculator):
        """Test caso finca rural completo."""
        input_data = {"fecha_ingreso": "2024-11-16", "fecha_corte": "2025-11-15"}

        result = calculator.calculate_all_prestaciones(
            input_data=input_data, sbl_general=2200000, sbl_prima=2200000
        )

        # Validar estructura
        assert "dias_servicio" in result
        assert "cesantias" in result
        assert "intereses_cesantias" in result
        assert "prima" in result
        assert "total_prestaciones" in result

        # Validar valores
        assert result["dias_servicio"] == 365
        assert result["cesantias"]["valor"] == 2200000
        assert result["intereses_cesantias"]["valor"] == 264000

        # Total debe ser suma de prestaciones
        total_manual = (
            result["cesantias"]["valor"]
            + result["intereses_cesantias"]["valor"]
            + result["prima"]["valor"]
        )
        assert result["total_prestaciones"] == total_manual

    def test_medio_año(self, calculator):
        """Test medio año."""
        input_data = {"fecha_ingreso": "2025-01-01", "fecha_corte": "2025-06-30"}

        result = calculator.calculate_all_prestaciones(
            input_data=input_data, sbl_general=1500000, sbl_prima=1500000
        )

        assert result["dias_servicio"] == 181
        # Cesantías: (1.500.000 × 181) / 360 = 754.166,67 ≈ 754.167
        assert abs(result["cesantias"]["valor"] - 754167) <= 1


# ============================================================================
# TESTS: Validación contra casos conocidos
# ============================================================================


class TestValidacionCasosConocidos:
    """Tests de validación contra casos documentados."""

    @pytest.mark.parametrize(
        "caso,expected",
        [
            (
                {
                    "name": "Finca rural año completo",
                    "sbl_general": 2200000,
                    "sbl_prima": 2200000,
                    "fecha_ingreso": "2024-11-16",
                    "fecha_corte": "2025-11-15",
                },
                {"cesantias": 2200000, "intereses": 264000, "dias_servicio": 365},
            ),
            (
                {
                    "name": "SMMLV medio año",
                    "sbl_general": 1423500,
                    "sbl_prima": 1423500,
                    "fecha_ingreso": "2025-01-01",
                    "fecha_corte": "2025-06-30",
                },
                {
                    "cesantias": 715208,  # (1.423.500 × 181) / 360
                    "intereses": 43103,  # Aprox
                    "dias_servicio": 181,
                },
            ),
        ],
    )
    def test_casos_parametrizados(self, calculator, caso, expected):
        """Test casos parametrizados."""
        dias = calculator.calculate_dias_servicio(
            caso["fecha_ingreso"], caso["fecha_corte"]
        )

        ces = calculator.calculate_cesantias(
            caso["sbl_general"], dias, caso["fecha_ingreso"], caso["fecha_corte"]
        )

        inter = calculator.calculate_intereses_cesantias(
            ces["valor"], dias, caso["fecha_ingreso"], caso["fecha_corte"]
        )

        # Tolerancia de 1 peso
        assert abs(dias - expected["dias_servicio"]) == 0
        assert abs(ces["valor"] - expected["cesantias"]) <= 1
        assert abs(inter["valor"] - expected["intereses"]) <= 1


# ============================================================================
# TESTS: Casos de borde
# ============================================================================


class TestCasosBorde:
    """Tests para casos de borde y situaciones extremas."""

    def test_año_bisiesto_completo(self, calculator):
        """Test año bisiesto completo (2024)."""
        dias = calculator.calculate_dias_servicio("2024-01-01", "2024-12-31")
        assert dias == 366

        ces = calculator.calculate_cesantias(
            sbl_general=2000000,
            dias_servicio=366,
            fecha_ingreso="2024-01-01",
            fecha_corte="2024-12-31",
        )

        # (2.000.000 × 366) / 360 = 2.033.333,33
        expected = int(
            Decimal("2033333.33").quantize(Decimal("1"), rounding="ROUND_HALF_UP")
        )
        assert abs(ces["valor"] - expected) <= 1

    def test_salario_minimo(self, calculator):
        """Test con salario mínimo."""
        result = calculator.calculate_all_prestaciones(
            input_data={"fecha_ingreso": "2025-01-01", "fecha_corte": "2025-12-31"},
            sbl_general=1423500,
            sbl_prima=1423500,
        )

        # Validar que todos los cálculos sean consistentes
        assert result["cesantias"]["valor"] > 0
        assert result["intereses_cesantias"]["valor"] > 0
        assert result["prima"]["valor"] > 0

    def test_salario_muy_alto(self, calculator):
        """Test con salario muy alto."""
        sbl_alto = 50000000  # 50 millones

        result = calculator.calculate_all_prestaciones(
            input_data={"fecha_ingreso": "2025-01-01", "fecha_corte": "2025-12-31"},
            sbl_general=sbl_alto,
            sbl_prima=sbl_alto,
        )

        # Validar que los cálculos escalen proporcionalmente
        assert result["cesantias"]["valor"] > 40000000  # Aprox 50M para 360 días


# ============================================================================
# TESTS: Integración con logging
# ============================================================================


class TestLogging:
    """Tests para verificar logging correcto."""

    def test_logging_activado(self, calculator, caplog):
        """Test que el logging funcione."""
        import logging

        caplog.set_level(logging.INFO)

        calculator.calculate_cesantias(
            sbl_general=2000000,
            dias_servicio=360,
            fecha_ingreso="2025-01-01",
            fecha_corte="2025-12-31",
        )

        assert "Cesantías calculadas" in caplog.text


# ============================================================================
# EJECUCIÓN DIRECTA
# ============================================================================

if __name__ == "__main__":
    pytest.main(
        [__file__, "-v", "--cov=liquidator.calculators.prestaciones_calculator"]
    )
