"""
Tests unitarios para el Calculador de SBL (Salario Base de Liquidación)

Cubre:
- Cálculo de SBL_GENERAL con todos los componentes
- Cálculo de SBL_VACACIONES (exclusiones correctas)
- Validación de auxilio de transporte (residencia en finca)
- Validación de límite 2 SMMLV
- Cálculo de promedio de salarios variables
- Casos especiales y de borde
"""

from decimal import Decimal

import pytest

from liquidator.calculators.sbl_calculator import SBLCalculator


# Fixtures
@pytest.fixture
def params_2025():
    """Parámetros legales para 2025"""
    return {
        "SMMLV": 1423500,
        "AUXILIO_TRANS": 200000,
        "LIMITE_AUXILIO": 2847000,  # 2 * SMMLV
        "REDONDEO": 0,
    }


@pytest.fixture
def sbl_calculator(params_2025):
    """Instancia del calculador"""
    return SBLCalculator(params_2025)


# Tests de SBL_GENERAL
class TestSBLGeneral:
    """Tests para el cálculo de SBL_GENERAL"""

    def test_sbl_general_salario_base_solo(self, sbl_calculator):
        """Test con solo salario base"""
        sbl, alertas = sbl_calculator.calculate_sbl_general(salario_mensual=2000000)

        assert sbl == Decimal("2000000")
        assert len(alertas) == 0

    def test_sbl_general_con_todos_componentes(self, sbl_calculator):
        """Test con todos los componentes salariales"""
        sbl, alertas = sbl_calculator.calculate_sbl_general(
            salario_mensual=2000000,
            comisiones_promedio_mensual=300000,
            horas_extras_promedio_mensual=150000,
            bonificaciones_promedio_mensual=100000,
            auxilio_transporte=200000,
            reside_en_lugar_trabajo=False,
            auxilio_conectividad_pactado=False,
        )

        # 2,000,000 + 300,000 + 150,000 + 100,000 + 200,000 = 2,750,000
        assert sbl == Decimal("2750000")

    def test_sbl_general_finca_rural_sin_auxilio(self, sbl_calculator):
        """Test caso finca rural: excluye auxilio de transporte"""
        sbl, alertas = sbl_calculator.calculate_sbl_general(
            salario_mensual=2000000,
            auxilio_transporte=200000,
            reside_en_lugar_trabajo=True,  # Reside en finca
        )

        # Solo salario, sin auxilio
        assert sbl == Decimal("2000000")

        # Debe haber alerta de exclusión
        alertas_exclusion = [a for a in alertas if a["tipo"] == "EXCLUSION"]
        assert len(alertas_exclusion) == 1
        assert alertas_exclusion[0]["concepto"] == "auxilio_transporte"
        assert "Finca Rural" in alertas_exclusion[0]["razon"]

    def test_sbl_general_con_auxilio_conectividad_pactado(self, sbl_calculator):
        """Test con auxilio de conectividad explícitamente pactado"""
        sbl, alertas = sbl_calculator.calculate_sbl_general(
            salario_mensual=2000000,
            auxilio_conectividad=200000,
            reside_en_lugar_trabajo=False,
            auxilio_conectividad_pactado=True,  # Pactado como salario
        )

        # Incluye auxilio conectividad
        assert sbl == Decimal("2200000")

        # Debe haber alerta informativa
        alertas_info = [a for a in alertas if a["tipo"] == "INFO"]
        assert any("pactado como salario" in a["razon"] for a in alertas_info)

    def test_sbl_general_con_auxilio_conectividad_no_pactado(self, sbl_calculator):
        """Test con auxilio de conectividad NO pactado (debe excluirse)"""
        sbl, alertas = sbl_calculator.calculate_sbl_general(
            salario_mensual=2000000,
            auxilio_conectividad=200000,
            reside_en_lugar_trabajo=False,
            auxilio_conectividad_pactado=False,  # NO pactado
        )

        # NO debe incluir auxilio conectividad
        assert sbl == Decimal("2000000")

        # Debe haber WARNING
        alertas_warning = [a for a in alertas if a["tipo"] == "WARNING"]
        assert len(alertas_warning) == 1
        assert alertas_warning[0]["concepto"] == "auxilio_conectividad"

    def test_sbl_general_excede_limite_2_smmlv(self, sbl_calculator):
        """Test cuando salario excede 2 SMMLV (no aplica auxilio)"""
        sbl, alertas = sbl_calculator.calculate_sbl_general(
            salario_mensual=3000000, auxilio_transporte=200000  # > 2,847,000
        )

        # Solo salario, sin auxilio
        assert sbl == Decimal("3000000")

        # Debe haber alerta de exclusión por límite
        alertas_exclusion = [a for a in alertas if a["tipo"] == "EXCLUSION"]
        assert len(alertas_exclusion) == 1
        assert "2 SMMLV" in alertas_exclusion[0]["razon"]


# Tests de SBL_VACACIONES
class TestSBLVacaciones:
    """Tests para el cálculo de SBL_VACACIONES"""

    def test_sbl_vacaciones_base(self, sbl_calculator):
        """Test cálculo básico SBL_VACACIONES"""
        sbl, alertas = sbl_calculator.calculate_sbl_vacaciones(
            salario_mensual=2000000, comisiones_promedio_mensual=300000
        )

        # Solo salario + comisiones
        assert sbl == Decimal("2300000")

    def test_sbl_vacaciones_sin_comisiones(self, sbl_calculator):
        """Test SBL_VACACIONES sin comisiones"""
        sbl, alertas = sbl_calculator.calculate_sbl_vacaciones(salario_mensual=2000000)

        assert sbl == Decimal("2000000")

        # Debe tener alerta informativa sobre exclusiones
        assert any("excluye" in a["razon"].lower() for a in alertas)

    def test_sbl_vacaciones_excluye_componentes_correctamente(self, sbl_calculator):
        """
        Test que verifica que SBL_VACACIONES NO incluye:
        - Horas extras
        - Recargos
        - Auxilios
        """
        # Este test es conceptual - SBL_VACACIONES solo acepta
        # salario_mensual y comisiones
        sbl, alertas = sbl_calculator.calculate_sbl_vacaciones(
            salario_mensual=2000000, comisiones_promedio_mensual=300000
        )

        # Verificar que solo incluye los dos componentes
        assert sbl == Decimal("2300000")

        # Verificar alerta sobre exclusiones
        alertas_info = [a for a in alertas if a["tipo"] == "INFO"]
        assert len(alertas_info) >= 1
        assert any("excluye" in a["razon"].lower() for a in alertas_info)


# Tests de SBL_PRIMA
class TestSBLPrima:
    """Tests para el cálculo de SBL_PRIMA"""

    def test_sbl_prima_igual_a_general(self, sbl_calculator):
        """Test que SBL_PRIMA usa mismas reglas que SBL_GENERAL"""
        sbl, alertas = sbl_calculator.calculate_sbl_prima(
            salario_mensual=2000000,
            comisiones_promedio_mensual=300000,
            horas_extras_promedio_mensual=150000,
        )

        assert sbl == Decimal("2450000")

    def test_sbl_prima_salario_variable(self, sbl_calculator):
        """Test SBL_PRIMA con salario variable"""
        sbl, alertas = sbl_calculator.calculate_sbl_prima(
            salario_mensual=2000000,
            comisiones_promedio_mensual=300000,
            es_salario_variable=True,
        )

        assert sbl == Decimal("2300000")

        # Debe haber alerta sobre promediación
        alertas_info = [a for a in alertas if a["tipo"] == "INFO"]
        assert any("variable" in a["razon"].lower() for a in alertas_info)


# Tests de Validación de Auxilios
class TestAuxilioRules:
    """Tests para validación de reglas de auxilios"""

    def test_auxilio_transporte_aplica(self, sbl_calculator):
        """Test auxilio de transporte aplica correctamente"""
        resultado = sbl_calculator.apply_auxilio_rules(
            salario_mensual=1500000,
            auxilio_transporte=200000,
            auxilio_conectividad=0,
            reside_en_lugar_trabajo=False,
            auxilio_conectividad_pactado=False,
        )

        assert resultado["auxilio_transporte_aplica"] is True
        assert resultado["auxilio_transporte_valor"] == 200000

    def test_auxilio_transporte_excluido_por_residencia(self, sbl_calculator):
        """Test auxilio excluido por residencia en finca"""
        resultado = sbl_calculator.apply_auxilio_rules(
            salario_mensual=1500000,
            auxilio_transporte=200000,
            auxilio_conectividad=0,
            reside_en_lugar_trabajo=True,  # Reside en finca
            auxilio_conectividad_pactado=False,
        )

        assert resultado["auxilio_transporte_aplica"] is False
        assert resultado["auxilio_transporte_valor"] == 0

        # Verificar alerta
        alertas = resultado["alertas"]
        assert any("Finca Rural" in a["razon"] for a in alertas)

    def test_auxilio_excluido_por_limite_2_smmlv(self, sbl_calculator):
        """Test auxilio excluido cuando salario > 2 SMMLV"""
        resultado = sbl_calculator.apply_auxilio_rules(
            salario_mensual=3000000,  # > 2,847,000
            auxilio_transporte=200000,
            auxilio_conectividad=0,
            reside_en_lugar_trabajo=False,
            auxilio_conectividad_pactado=False,
        )

        assert resultado["auxilio_transporte_aplica"] is False

        # Verificar alerta sobre límite
        alertas = resultado["alertas"]
        assert any("2 SMMLV" in a["razon"] for a in alertas)

    def test_auxilio_conectividad_warning_no_pactado(self, sbl_calculator):
        """Test warning cuando auxilio conectividad no está pactado"""
        resultado = sbl_calculator.apply_auxilio_rules(
            salario_mensual=1500000,
            auxilio_transporte=0,
            auxilio_conectividad=200000,
            reside_en_lugar_trabajo=False,
            auxilio_conectividad_pactado=False,  # NO pactado
        )

        assert resultado["auxilio_conectividad_aplica"] is False

        # Debe haber WARNING
        alertas_warning = [a for a in resultado["alertas"] if a["tipo"] == "WARNING"]
        assert len(alertas_warning) == 1


# Tests de Promedio Variable
class TestPromedioVariable:
    """Tests para cálculo de promedio de salarios variables"""

    def test_promedio_12_meses_completos(self, sbl_calculator):
        """Test promedio con 12 meses completos"""
        salarios_historicos = [
            {"periodo": "2024-01", "valor": 2000000},
            {"periodo": "2024-02", "valor": 2100000},
            {"periodo": "2024-03", "valor": 2050000},
            {"periodo": "2024-04", "valor": 2200000},
            {"periodo": "2024-05", "valor": 2150000},
            {"periodo": "2024-06", "valor": 2000000},
            {"periodo": "2024-07", "valor": 2100000},
            {"periodo": "2024-08", "valor": 2250000},
            {"periodo": "2024-09", "valor": 2300000},
            {"periodo": "2024-10", "valor": 2100000},
            {"periodo": "2024-11", "valor": 2150000},
            {"periodo": "2024-12", "valor": 2200000},
        ]

        promedio, alertas = sbl_calculator.calculate_promedio_variable(
            salarios_historicos=salarios_historicos, meses_requeridos=12
        )

        # Promedio: 25,600,000 / 12 = 2,133,333.33 → 2,133,333
        assert promedio == Decimal("2133333")

    def test_promedio_periodo_incompleto(self, sbl_calculator):
        """Test promedio con menos de 12 meses disponibles"""
        salarios_historicos = [
            {"periodo": "2024-07", "valor": 2000000},
            {"periodo": "2024-08", "valor": 2100000},
            {"periodo": "2024-09", "valor": 2050000},
            {"periodo": "2024-10", "valor": 2200000},
            {"periodo": "2024-11", "valor": 2150000},
            {"periodo": "2024-12", "valor": 2000000},
        ]

        promedio, alertas = sbl_calculator.calculate_promedio_variable(
            salarios_historicos=salarios_historicos, meses_requeridos=12
        )

        # Debe promediar los 6 meses disponibles
        # 12,500,000 / 6 = 2,083,333.33 → 2,083,333
        assert promedio == Decimal("2083333")

        # Debe haber WARNING sobre meses insuficientes
        alertas_warning = [a for a in alertas if a["tipo"] == "WARNING"]
        assert len(alertas_warning) == 1
        assert "6 meses disponibles" in alertas_warning[0]["razon"]

    def test_promedio_sin_historico(self, sbl_calculator):
        """Test cuando no hay histórico disponible"""
        promedio, alertas = sbl_calculator.calculate_promedio_variable(
            salarios_historicos=[], meses_requeridos=12
        )

        assert promedio == Decimal("0")

        # Debe haber ERROR
        alertas_error = [a for a in alertas if a["tipo"] == "ERROR"]
        assert len(alertas_error) == 1


# Tests de Casos Especiales
class TestCasosEspeciales:
    """Tests de casos especiales y de borde"""

    def test_caso_finca_rural_completo(self, sbl_calculator):
        """
        Test del caso completo de finca rural del ejemplo:
        - Salario: 2,000,000
        - Auxilio conectividad: 200,000 (pactado)
        - Reside en finca: True
        - Auxilio transporte: NO aplica
        """
        sbl_general, alertas_general = sbl_calculator.calculate_sbl_general(
            salario_mensual=2000000,
            auxilio_transporte=200000,
            auxilio_conectividad=200000,
            reside_en_lugar_trabajo=True,
            auxilio_conectividad_pactado=True,
        )

        # SBL_GENERAL = 2,000,000 + 200,000 = 2,200,000
        # (auxilio transporte excluido por residencia)
        assert sbl_general == Decimal("2200000")

        # Verificar alertas
        assert any(
            "Finca Rural" in a["razon"]
            for a in alertas_general
            if a["tipo"] == "EXCLUSION"
        )

        # SBL_VACACIONES
        sbl_vac, _ = sbl_calculator.calculate_sbl_vacaciones(salario_mensual=2000000)
        assert sbl_vac == Decimal("2000000")

    def test_salario_exactamente_2_smmlv(self, sbl_calculator):
        """Test cuando salario es exactamente 2 SMMLV"""
        sbl, alertas = sbl_calculator.calculate_sbl_general(
            salario_mensual=2847000, auxilio_transporte=200000  # Exactamente 2 SMMLV
        )

        # En el límite, NO debe aplicar auxilio
        assert sbl == Decimal("2847000")

    def test_salario_justo_debajo_2_smmlv(self, sbl_calculator):
        """Test cuando salario está justo debajo de 2 SMMLV"""
        sbl, alertas = sbl_calculator.calculate_sbl_general(
            salario_mensual=2846999,  # 1 peso menos que 2 SMMLV
            auxilio_transporte=200000,
        )

        # Debe incluir auxilio
        assert sbl == Decimal("3046999")

    def test_multiples_componentes_con_exclusiones(self, sbl_calculator):
        """Test caso complejo con múltiples componentes y exclusiones"""
        sbl, alertas = sbl_calculator.calculate_sbl_general(
            salario_mensual=1800000,
            comisiones_promedio_mensual=400000,
            horas_extras_promedio_mensual=300000,
            bonificaciones_promedio_mensual=200000,
            auxilio_transporte=200000,
            auxilio_conectividad=150000,
            reside_en_lugar_trabajo=False,
            auxilio_conectividad_pactado=False,  # NO pactado
        )

        # Debe incluir todo EXCEPTO auxilio conectividad (no pactado)
        # 1,800,000 + 400,000 + 300,000 + 200,000 + 200,000 = 2,900,000
        assert sbl == Decimal("2900000")

        # Debe haber WARNING sobre auxilio conectividad
        assert any(
            a["tipo"] == "WARNING" and a["concepto"] == "auxilio_conectividad"
            for a in alertas
        )


# Tests de Integración
class TestIntegracionSBL:
    """Tests de integración del calculador completo"""

    def test_calculo_completo_todas_variantes(self, sbl_calculator):
        """Test que calcula todas las variantes de SBL para un caso"""
        # Datos del trabajador
        salario = 2000000
        comisiones = 300000
        horas_extras = 150000

        # Calcular todas las variantes
        sbl_general, _ = sbl_calculator.calculate_sbl_general(
            salario_mensual=salario,
            comisiones_promedio_mensual=comisiones,
            horas_extras_promedio_mensual=horas_extras,
        )

        sbl_vacaciones, _ = sbl_calculator.calculate_sbl_vacaciones(
            salario_mensual=salario, comisiones_promedio_mensual=comisiones
        )

        sbl_prima, _ = sbl_calculator.calculate_sbl_prima(
            salario_mensual=salario,
            comisiones_promedio_mensual=comisiones,
            horas_extras_promedio_mensual=horas_extras,
        )

        # Verificaciones
        assert sbl_general == Decimal("2450000")
        assert sbl_vacaciones == Decimal("2300000")
        assert sbl_prima == Decimal("2450000")

        # SBL_VACACIONES debe ser menor (excluye horas extras)
        assert sbl_vacaciones < sbl_general

    def test_gestion_alertas(self, sbl_calculator):
        """Test gestión de alertas acumuladas"""
        # Resetear alertas
        sbl_calculator.reset_alertas()
        assert len(sbl_calculator.get_alertas()) == 0

        # Generar cálculo con alertas
        sbl_calculator.calculate_sbl_general(
            salario_mensual=2000000,
            auxilio_transporte=200000,
            reside_en_lugar_trabajo=True,
        )

        # Verificar que hay alertas
        alertas = sbl_calculator.get_alertas()
        assert len(alertas) > 0

        # Resetear
        sbl_calculator.reset_alertas()
        assert len(sbl_calculator.get_alertas()) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
