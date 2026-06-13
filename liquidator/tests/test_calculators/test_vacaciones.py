# liquidator/tests/test_calculators/test_vacaciones.py
"""
Tests para el módulo de cálculo de vacaciones.
Verifica que los cálculos sean correctos y que las reglas legales se apliquen adecuadamente.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from liquidator.calculators.vacaciones_calculator import VacacionesCalculator
from liquidator.utils.date_utils import calculate_days_between


class TestVacacionesCalculator:
    """Tests para VacacionesCalculator"""

    @pytest.fixture
    def params(self):
        """Parámetros de prueba estándar"""
        return {
            "SMMLV": 1423500,
            "AUXILIO_TRANS": 200000,
            "LIMITE_AUXILIO": 2847000,
            "TASA_INT_CESANTIAS": 0.12,
            "DIAS_BASE": 360.0,
            "VACACIONES_DENOM": 720.0,
            "REDONDEO": 0,
            "TOPE_INDEMNIZACION_SMMLV": 20,
            "FECHA_APLICACION_RECARGO_DOMINICAL": "2025-07-01",
        }

    @pytest.fixture
    def calculator(self, params):
        """Fixture del calculador con parámetros de prueba"""
        return VacacionesCalculator(params)

    def test_calculate_dias_vacaciones_causadas_un_ano(self, calculator):
        """Test cálculo de días de vacaciones para un año exacto"""
        fecha_ingreso = "2023-01-01"
        fecha_corte = "2024-01-01"

        dias = calculator.calculate_dias_vacaciones_causadas(fecha_ingreso, fecha_corte)

        assert dias == 15, f"Esperado 15 días para un año exacto, obtenido {dias}"

    def test_calculate_dias_vacaciones_causadas_dos_anos(self, calculator):
        """Test cálculo de días de vacaciones para dos años exactos"""
        fecha_ingreso = "2022-01-01"
        fecha_corte = "2024-01-01"

        dias = calculator.calculate_dias_vacaciones_causadas(fecha_ingreso, fecha_corte)

        assert dias == 30, f"Esperado 30 días para dos años exactos, obtenido {dias}"

    def test_calculate_dias_vacaciones_causadas_periodo_parcial(self, calculator):
        """Test cálculo de días de vacaciones para periodo parcial"""
        fecha_ingreso = "2023-07-01"
        fecha_corte = "2024-01-01"  # 6 meses

        dias = calculator.calculate_dias_vacaciones_causadas(fecha_ingreso, fecha_corte)

        # 6 meses = 0.5 años = 7.5 días, se redondea a 7 días (proporcional)
        assert dias == 7, f"Esperado 7 días para 6 meses, obtenido {dias}"

    def test_calculate_valor_vacaciones_base_720(self, calculator):
        """Test cálculo del valor de vacaciones con base 720"""
        sbl_vacaciones = 2000000  # $2.000.000
        dias_vacaciones = 15

        valor = calculator.calculate_valor_vacaciones(sbl_vacaciones, dias_vacaciones)

        # Fórmula: (2.000.000 * 15) / 720 = 41.666,67 -> redondeado a 41.667
        valor_esperado = round((2000000 * 15) / 720)
        assert (
            valor == valor_esperado
        ), f"Valor incorrecto. Esperado: {valor_esperado}, Obtenido: {valor}"

    def test_calculate_valor_vacaciones_cero_dias(self, calculator):
        """Test cálculo de valor cuando no hay días de vacaciones"""
        sbl_vacaciones = 2000000
        dias_vacaciones = 0

        valor = calculator.calculate_valor_vacaciones(sbl_vacaciones, dias_vacaciones)

        assert valor == 0, f"Valor debe ser 0 cuando no hay días, obtenido {valor}"

    def test_determinar_compensacion_dinero_periodica(self, calculator):
        """Test que en modo PERIÓDICA no aplica compensación en dinero"""
        modo = "PERIODICA"
        dias_pendientes = 15

        resultado = calculator.determinar_compensacion_dinero(modo, dias_pendientes)

        assert not resultado[
            "aplica_compensacion"
        ], "No debe aplicar compensación en modo PERIÓDICA"
        assert resultado["motivo"] == "No aplica en modo PERIÓDICA sin acuerdo de compensación"
        assert resultado["norma_aplicada"] == "Arts.186-192 CST"

    def test_determinar_compensacion_dinero_finiquito_con_dias(self, calculator):
        """Test que en modo FINIQUITO aplica compensación si hay días pendientes"""
        modo = "FINIQUITO"
        dias_pendientes = 15

        resultado = calculator.determinar_compensacion_dinero(modo, dias_pendientes)

        assert resultado[
            "aplica_compensacion"
        ], "Debe aplicar compensación en modo FINIQUITO con días pendientes"
        assert resultado["dias_compensados"] == 15
        assert resultado["norma_aplicada"] == "Arts.186-192 CST"

    def test_determinar_compensacion_dinero_finiquito_sin_dias(self, calculator):
        """Test que en modo FINIQUITO no aplica compensación si no hay días pendientes"""
        modo = "FINIQUITO"
        dias_pendientes = 0

        resultado = calculator.determinar_compensacion_dinero(modo, dias_pendientes)

        assert not resultado[
            "aplica_compensacion"
        ], "No debe aplicar compensación sin días pendientes"
        assert (
            resultado["motivo"] == "No hay días de vacaciones pendientes para compensar"
        )

    def test_calculate_vacaciones_completas_periodica(self, calculator):
        """Test cálculo completo en modo PERIÓDICA"""
        input_data = {
            "modo": "PERIODICA",
            "fecha_ingreso": "2023-01-01",
            "fecha_corte": "2024-01-01",
            "dias_vacaciones_pendientes": 15,
        }
        sbl_vacaciones = 2000000

        resultado = calculator.calculate_vacaciones_completas(
            input_data, sbl_vacaciones
        )

        assert resultado["valor"] == 0, "En modo PERIÓDICA el valor debe ser 0"
        assert (
            resultado["dias_liquidados"] == 0
        ), "En modo PERIÓDICA los días liquidados deben ser 0"
        assert (
            resultado["dias_causados"] == 15
        ), "Debe calcular los días causados correctamente"
        assert "No aplica compensación" in resultado["nota"]

    def test_calculate_vacaciones_completas_finiquito(self, calculator):
        """Test cálculo completo en modo FINIQUITO con días pendientes"""
        input_data = {
            "modo": "FINIQUITO",
            "fecha_ingreso": "2023-01-01",
            "fecha_corte": "2024-01-01",
            "dias_vacaciones_pendientes": 15,
        }
        sbl_vacaciones = 2000000

        resultado = calculator.calculate_vacaciones_completas(
            input_data, sbl_vacaciones
        )

        valor_esperado = round((2000000 * 15) / 720)

        assert (
            resultado["valor"] == valor_esperado
        ), f"Valor incorrecto. Esperado: {valor_esperado}, Obtenido: {resultado['valor']}"
        assert (
            resultado["dias_liquidados"] == 15
        ), "En modo FINIQUITO debe liquidar los días pendientes"
        assert (
            resultado["dias_causados"] == 15
        ), "Debe calcular los días causados correctamente"
        assert resultado["aplica_compensacion"] is True
        assert "Compensación" in resultado["nota"]

    def test_calculate_vacaciones_completas_finiquito_sin_pendientes(self, calculator):
        """Test cálculo completo en modo FINIQUITO sin días pendientes"""
        input_data = {
            "modo": "FINIQUITO",
            "fecha_ingreso": "2023-01-01",
            "fecha_corte": "2024-01-01",
            "dias_vacaciones_pendientes": 0,
        }
        sbl_vacaciones = 2000000

        resultado = calculator.calculate_vacaciones_completas(
            input_data, sbl_vacaciones
        )

        assert resultado["valor"] == 0, "Sin días pendientes, el valor debe ser 0"
        assert (
            resultado["dias_liquidados"] == 0
        ), "Sin días pendientes, los días liquidados deben ser 0"
        assert resultado["aplica_compensacion"] is False

    @pytest.mark.forensic_audit
    def test_TEMPORAL_impacto_formula_720_vs_30(self, calculator):
        """
        TEST TEMPORAL DE AUDITORÍA FORENSE - Fecha: 2025-12-02
        TODO: REMOVER después de validación de auditoría completa (Ticket: #AUDIT-720-2025)
        
        Propósito: Documentar impacto del error crítico de fórmula /30 vs /720 (Art. 186-192 CST)
        
        Antecedente: Se reportó una "corrección" que cambió el denominador de 720 a 30.
        Esta auditoría forense comprueba que /720 es el valor legalmente correcto.
        
        Caso de prueba: SBL=$2,000,000, 15 días vacaciones
        - Fórmula correcta (/720): $41,667 (legal según Art. 186-192 CST)
        - Fórmula errónea (/30): $1,000,000 (error de +2,300%)
        """
        sbl = 2000000
        dias = 15
        
        # Cálculos de comparación para auditoría
        valor_correcto_720 = round((sbl * dias) / 720)  # $41,667 (legal)
        valor_erroneo_30 = round((sbl * dias) / 30)     # $1,000,000 (error)
        
        diferencia_porcentual = ((valor_erroneo_30 - valor_correcto_720) / valor_correcto_720) * 100
        
        # Documentación forense del impacto
        assert valor_correcto_720 == 41667, f"Valor legal Art.186-192 CST debería ser: {valor_correcto_720}"
        assert valor_erroneo_30 == 1000000, f"Valor erróneo con /30 sería: {valor_erroneo_30}"
        assert diferencia_porcentual >= 2299, f"Diferencia de impacto: +{diferencia_porcentual:.0f}%"
        
        # Verificación crítica: El calculador debe usar la fórmula legal (/720)
        valor_calculado = calculator.calculate_valor_vacaciones(sbl, dias)
        assert valor_calculado == valor_correcto_720, \
            f"CRÍTICO: Calculador debe usar /720 (legal). Esperado: ${valor_correcto_720:,}, Obtenido: ${valor_calculado:,}"
        
        # Evidencia de corrección
        print(f"\n[AUDITORÍA FORENSE] Validación de corrección de fórmula de vacaciones:")
        print(f"  • SBL: ${sbl:,}")
        print(f"  • Días: {dias}")
        print(f"  • Fórmula correcta (720): ${valor_correcto_720:,} ✓ LEGAL (Art. 186-192 CST)")
        print(f"  • Fórmula errónea (30):  ${valor_erroneo_30:,} ✗ INCORRECTO (+{diferencia_porcentual:.0f}%)")
        print(f"  • Valor calculado por sistema: ${valor_calculado:,} ✓ CORRECCIÓN APLICADA")

