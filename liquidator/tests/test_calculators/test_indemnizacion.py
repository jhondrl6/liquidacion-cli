# liquidator/tests/test_calculators/test_indemnizacion.py
"""
Tests para el módulo de cálculo de indemnizaciones.
Verifica que los cálculos sean correctos y que las reglas legales se apliquen adecuadamente.
"""


import pytest

from liquidator.calculators.indemnizacion_calculator import IndemnizacionCalculator


class TestIndemnizacionCalculator:
    """Tests para IndemnizacionCalculator"""

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
        return IndemnizacionCalculator(params)

    def test_aplica_indemnizacion_sin_justa_causa(self, calculator):
        """Test que aplica indemnización para sin justa causa"""
        assert calculator._aplica_indemnizacion("sin_justa_causa")
        assert calculator._aplica_indemnizacion("sin justa causa")
        assert calculator._aplica_indemnizacion("despido injustificado")

    def test_no_aplica_indemnizacion_justa_causa(self, calculator):
        """Test que no aplica indemnización para justa causa"""
        assert not calculator._aplica_indemnizacion("justa_causa")
        assert not calculator._aplica_indemnizacion("justa causa")
        assert not calculator._aplica_indemnizacion("renuncia")
        assert not calculator._aplica_indemnizacion("renuncia_voluntaria")

    def test_calculate_indemnizacion_indefinido_un_ano(self, calculator):
        """Test cálculo indemnización contrato indefinido - un año"""
        sbl_general = 2000000  # $2.000.000
        fecha_ingreso = "2023-01-01"
        fecha_corte = "2024-01-01"

        resultado = calculator._calculate_indemnizacion_indefinido(
            sbl_general, fecha_ingreso, fecha_corte
        )

        # 1 año = 30 días de indemnización
        # Valor: 2.000.000 * 30 / 30 = 2.000.000
        assert resultado["dias_indemnizacion"] == 30
        assert resultado["valor"] == 2000000
        assert resultado["tipo_calculo"] == "indefinido"
        assert resultado["aplica"] is True

    def test_calculate_indemnizacion_indefinido_dos_anos(self, calculator):
        """Test cálculo indemnización contrato indefinido - dos años"""
        sbl_general = 2000000
        fecha_ingreso = "2022-01-01"
        fecha_corte = "2024-01-01"

        resultado = calculator._calculate_indemnizacion_indefinido(
            sbl_general, fecha_ingreso, fecha_corte
        )

        # 2 años = 60 días de indemnización
        # Valor: 2.000.000 * 60 / 30 = 4.000.000
        assert resultado["dias_indemnizacion"] == 60
        assert resultado["valor"] == 4000000
        assert resultado["tipo_calculo"] == "indefinido"

    def test_calculate_indemnizacion_indefinido_periodo_parcial(self, calculator):
        """Test cálculo indemnización contrato indefinido - periodo parcial"""
        sbl_general = 2000000
        fecha_ingreso = "2023-07-01"
        fecha_corte = "2024-01-01"  # 6 meses

        resultado = calculator._calculate_indemnizacion_indefinido(
            sbl_general, fecha_ingreso, fecha_corte
        )

        # 6 meses = fracción de año = 30 días de indemnización
        # Valor: 2.000.000 * 30 / 30 = 2.000.000
        assert resultado["dias_indemnizacion"] == 30
        assert resultado["valor"] == 2000000
        assert resultado["tipo_calculo"] == "indefinido"

    def test_apply_tope_20_smmlv_aplica(self, calculator):
        """Test aplicación de tope 20 SMMLV cuando aplica"""
        smmlv = calculator.params["SMMLV"]
        tope_valor = smmlv * calculator.params["TOPE_INDEMNIZACION_SMMLV"]

        # Caso donde el valor supera el tope
        valor_indemnizacion = tope_valor + 1000000
        sbl_general = smmlv + 1  # SBL mayor que SMMLV

        valor_con_tope = calculator.apply_tope_20_smmlv(
            valor_indemnizacion, sbl_general
        )

        assert (
            valor_con_tope == tope_valor
        ), f"Debe aplicar tope. Esperado: {tope_valor}, Obtenido: {valor_con_tope}"

    def test_apply_tope_20_smmlv_no_aplica(self, calculator):
        """Test que no aplica tope 20 SMMLV cuando SBL <= SMMLV"""
        smmlv = calculator.params["SMMLV"]
        tope_valor = smmlv * calculator.params["TOPE_INDEMNIZACION_SMMLV"]

        # Caso donde SBL <= SMMLV (no aplica tope)
        valor_indemnizacion = tope_valor + 1000000
        sbl_general = smmlv  # SBL igual a SMMLV

        valor_con_tope = calculator.apply_tope_20_smmlv(
            valor_indemnizacion, sbl_general
        )

        assert (
            valor_con_tope == valor_indemnizacion
        ), "No debe aplicar tope cuando SBL <= SMMLV"

    def test_calculate_salario_pendiente(self, calculator):
        """Test cálculo de salario pendiente"""
        salario_mensual = 2000000
        dias_pendientes = 5
        recargos_pendientes = 100000

        resultado = calculator.calculate_salario_pendiente(
            salario_mensual, dias_pendientes, recargos_pendientes
        )

        # Salario diario: 2.000.000 / 30 = 66.666,667 -> redondeado a 66.667
        # Valor base: 66.667 * 5 = 333.333,333 -> redondeado a 333.333
        # Valor total: 333.333 + 100.000 = 433.333
        salario_diario_esperado = 66667  # round(2000000 / 30) with REDONDEO=0

        assert resultado["valor"] == 433333.0
        assert resultado["valor_base"] == 333333.0
        assert resultado["recargos"] == 100000
        assert resultado["dias_pendientes"] == 5
        assert resultado["salario_diario"] == salario_diario_esperado

    def test_calculate_indemnizacion_completa_periodica(self, calculator):
        """Test cálculo completo en modo PERIÓDICA (no aplica indemnización)"""
        input_data = {
            "modo": "PERIODICA",
            "fecha_ingreso": "2023-01-01",
            "fecha_corte": "2024-01-01",
            "tipo_contrato": "indefinido",
            "motivo_terminacion": "sin_justa_causa",
        }
        sbl_general = 2000000

        resultado = calculator.calculate_indemnizacion_completa(input_data, sbl_general)

        assert resultado["indemnizacion"]["valor"] == 0
        assert not resultado["indemnizacion"]["aplica"]
        assert "No aplica en modo PERIÓDICA" in resultado["indemnizacion"]["nota"]

    def test_calculate_indemnizacion_completa_finiquito_indefinido(self, calculator):
        """Test cálculo completo en modo FINIQUITO para contrato indefinido"""
        input_data = {
            "modo": "FINIQUITO",
            "fecha_ingreso": "2023-01-01",
            "fecha_corte": "2024-01-01",
            "tipo_contrato": "indefinido",
            "motivo_terminacion": "sin_justa_causa",
            "salario_pendiente_dias": 0,
        }
        sbl_general = 2000000

        resultado = calculator.calculate_indemnizacion_completa(input_data, sbl_general)

        assert resultado["indemnizacion"]["valor"] == 2000000
        assert resultado["indemnizacion"]["aplica"] is True
        assert resultado["indemnizacion"]["dias_indemnizacion"] == 30

    def test_calculate_indemnizacion_completa_finiquito_con_salario_pendiente(
        self, calculator
    ):
        """Test cálculo completo en modo FINIQUITO con salario pendiente"""
        input_data = {
            "modo": "FINIQUITO",
            "fecha_ingreso": "2023-01-01",
            "fecha_corte": "2024-01-01",
            "tipo_contrato": "indefinido",
            "motivo_terminacion": "sin_justa_causa",
            "salario_mensual": 2000000,
            "salario_pendiente_dias": 5,
            "salario_pendiente": 333333,  # 5 días de salario
        }
        sbl_general = 2000000

        resultado = calculator.calculate_indemnizacion_completa(input_data, sbl_general)

        assert resultado["indemnizacion"]["valor"] == 2000000
        assert resultado["salario_pendiente"]["valor"] > 0
        assert resultado["salario_pendiente"]["dias_pendientes"] == 5

    def test_calculate_indemnizacion_completa_finiquito_tope_aplicado(self, calculator):
        """Test cálculo completo en modo FINIQUITO con tope 20 SMMLV aplicado"""
        smmlv = calculator.params["SMMLV"]
        tope_smmlv = calculator.params["TOPE_INDEMNIZACION_SMMLV"]
        tope_valor = smmlv * tope_smmlv

        input_data = {
            "modo": "FINIQUITO",
            "fecha_ingreso": "2020-01-01",  # 4 años
            "fecha_corte": "2024-01-01",
            "tipo_contrato": "indefinido",
            "motivo_terminacion": "sin_justa_causa",
        }
        # SBL muy alto para asegurar que se aplique el tope
        sbl_general = smmlv * 100

        resultado = calculator.calculate_indemnizacion_completa(input_data, sbl_general)

        # 4 años = 120 días de indemnización
        # Sin tope: sbl_general * 120 / 30 = sbl_general * 4
        # Con tope: debe ser exactamente 20 SMMLV
        assert resultado["indemnizacion"]["valor"] == tope_valor
        assert resultado["indemnizacion"]["tope_aplicado"] is True
        assert resultado["indemnizacion"]["dias_indemnizacion"] == 120

    def test_calculate_indemnizacion_completa_finiquito_no_aplica(self, calculator):
        """Test cálculo completo en modo FINIQUITO cuando no aplica indemnización"""
        input_data = {
            "modo": "FINIQUITO",
            "fecha_ingreso": "2023-01-01",
            "fecha_corte": "2024-01-01",
            "tipo_contrato": "indefinido",
            "motivo_terminacion": "justa_causa",  # No aplica indemnización
        }
        sbl_general = 2000000

        resultado = calculator.calculate_indemnizacion_completa(input_data, sbl_general)

        assert resultado["indemnizacion"]["valor"] == 0
        assert not resultado["indemnizacion"]["aplica"]
        assert "No aplica indemnización" in resultado["indemnizacion"]["nota"]

    # Tests for uncovered methods and branches

    def test_init_calculator(self, params):
        """Test initialization of IndemnizacionCalculator"""
        calculator = IndemnizacionCalculator(params)

        assert calculator.params == params
        assert calculator.topes_manager is not None

    def test_calculate_indemnizacion_sin_justa_causa_with_termination_types(
        self, calculator
    ):
        """Test different termination reasons for indemnizaciones"""
        sbl_general = 2000000
        fecha_ingreso = "2023-01-01"
        fecha_corte = "2024-01-01"
        tipo_contrato = "indefinido"

        # Test with termination types that should work
        for motivo in [
            "sin_justa_causa",
            "despido",
            "terminacion_empresa",
            "fuerza_mayor",
        ]:
            resultado = calculator.calculate_indemnizacion_sin_justa_causa(
                sbl_general, fecha_ingreso, fecha_corte, tipo_contrato, motivo
            )
            assert resultado["aplica"] is True
            assert resultado["valor"] > 0
            assert resultado["dias_indemnizacion"] == 30

    def test_calculate_indemnizacion_sin_justa_causa_termino_fijo(self, calculator):
        """Test cálculo indemnización para contrato a término fijo"""
        sbl_general = 2000000
        fecha_ingreso = "2023-01-01"
        fecha_corte = "2024-01-01"

        resultado = calculator.calculate_indemnizacion_sin_justa_causa(
            sbl_general, fecha_ingreso, fecha_corte, "fijo", "sin_justa_causa"
        )

        # Para término fijo, se asume 360 días totales - 360 días cumplidos = 0
        assert resultado["aplica"] is False
        assert resultado["valor"] == 0
        assert resultado["tipo_calculo"] == "termino_fijo"
        assert "Contrato cumplido en su totalidad" in resultado["nota"]

    def test_calculate_indemnizacion_termino_fijo_parcial(self, calculator):
        """Test cálculo indemnización para contrato a término fijo con tiempo parcial"""
        sbl_general = 2000000
        fecha_ingreso = "2023-07-01"  # 6 meses
        fecha_corte = "2024-01-01"

        resultado = calculator._calculate_indemnizacion_termino_fijo(
            sbl_general, fecha_ingreso, fecha_corte
        )

        # 360 días totales - ~185 días cumplidos (Jul-Dic incluyendo día de fin) = 175 días no cumplidos
        assert resultado["aplica"] is True
        assert resultado["dias_indemnizacion"] == 175
        assert resultado["tipo_calculo"] == "termino_fijo"
        assert resultado["valor"] > 0

    def test_calculate_indemnizacion_termino_fijo_alternative_names(self, calculator):
        """Test different names for fixed-term contracts"""
        sbl_general = 2000000
        fecha_ingreso = "2023-01-01"
        fecha_corte = "2024-01-01"

        for tipo in ["fijo", "termino_fijo", "a_termino_fijo"]:
            resultado = calculator.calculate_indemnizacion_sin_justa_causa(
                sbl_general, fecha_ingreso, fecha_corte, tipo, "sin_justa_causa"
            )

            assert resultado["tipo_calculo"] == "termino_fijo"

    def test_calculate_indemnizacion_tipo_contrato_invalido(self, calculator):
        """Test with invalid contract type"""
        sbl_general = 2000000
        fecha_ingreso = "2023-01-01"
        fecha_corte = "2024-01-01"

        with pytest.raises(ValueError, match="Tipo de contrato no válido"):
            calculator.calculate_indemnizacion_sin_justa_causa(
                sbl_general, fecha_ingreso, fecha_corte, "invalido", "sin_justa_causa"
            )

    def test_calculate_indemnizacion_indefinido_menor_a_un_ano(self, calculator):
        """Test cálculo indemnización para menos de un año"""
        sbl_general = 2000000
        fecha_ingreso = "2023-06-01"  # 7 meses
        fecha_corte = "2024-01-01"

        resultado = calculator._calculate_indemnizacion_indefinido(
            sbl_general, fecha_ingreso, fecha_corte
        )

        # Menos de un año: días de servicio (máximo 30)
        assert resultado["dias_indemnizacion"] == 30  # min(30, dias_servicio)
        assert resultado["aplica"] is True
        assert resultado["tipo_calculo"] == "indefinido"

    def test_calculate_indemnizacion_indefinido_menor_30_dias(self, calculator):
        """Test cálculo indemnización para menos de 30 días"""
        sbl_general = 2000000
        fecha_ingreso = "2023-12-20"  # 12 días
        fecha_corte = "2024-01-01"

        resultado = calculator._calculate_indemnizacion_indefinido(
            sbl_general, fecha_ingreso, fecha_corte
        )

        # Menos de 30 días, entre Dic 20 y Ene 1 hay 13 días (incluyendo día de fin)
        assert resultado["dias_indemnizacion"] == 13  # min(30, dias_servicio)
        assert resultado["aplica"] is True
        assert resultado["tipo_calculo"] == "indefinido"

    def test_calculate_indemnizacion_indefinido_mas_de_un_año_con_fraccion(
        self, calculator
    ):
        """Test cálculo indemnización para más de un año con fracción"""
        sbl_general = 2000000
        fecha_ingreso = "2022-01-01"  # 2 años
        fecha_corte = "2024-06-01"

        resultado = calculator._calculate_indemnizacion_indefinido(
            sbl_general, fecha_ingreso, fecha_corte
        )

        # 2 años completos + fracción = 2*30 + 30 = 90 días
        assert resultado["dias_indemnizacion"] == 90
        assert resultado["aplica"] is True
        assert resultado["tipo_calculo"] == "indefinido"

    def test_aplica_indemnizacion_false_cases(self, calculator):
        """Test various termination reasons that don't apply indemnizació"""
        motivos_no_aplican = [
            "justa_causa",
            "justa causa",
            "renuncia",
            "renuncia_voluntaria",
            "muerte",
            "incapacidad_absoluta",
        ]

        for motivo in motivos_no_aplican:
            assert not calculator._aplica_indemnizacion(motivo)

    def test_calculate_salario_pendiente_con_recargos(self, calculator):
        """Test cálculo de salario pendiente con recargos"""
        salario_mensual = 2000000
        dias_pendientes = 10
        recargos_pendientes = 500000

        resultado = calculator.calculate_salario_pendiente(
            salario_mensual, dias_pendientes, recargos_pendientes
        )

        assert resultado["valor"] == 1166667.0
        assert resultado["valor_base"] == 666667.0
        assert resultado["recargos"] == 500000
        assert resultado["dias_pendientes"] == 10

    def test_calculate_salario_pendiente_sin_recargos(self, calculator):
        """Test cálculo de salario pendiente sin recargos"""
        salario_mensual = 2000000
        dias_pendientes = 5

        resultado = calculator.calculate_salario_pendiente(
            salario_mensual, dias_pendientes
        )

        assert resultado["valor"] == 333333.0
        assert resultado["valor_base"] == resultado["valor"]
        assert resultado["recargos"] == 0

    def test_calculate_salario_pendiente_un_dia(self, calculator):
        """Test cálculo de salario pendiente para un día"""
        salario_mensual = 2000000
        dias_pendientes = 1

        resultado = calculator.calculate_salario_pendiente(
            salario_mensual, dias_pendientes
        )

        salario_diario_esperado = 66667  # round(2000000 / 30) with REDONDEO=0
        assert resultado["valor"] == salario_diario_esperado
        assert resultado["dias_pendientes"] == 1

    def test_calculate_salario_pendiente_errores(self, calculator):
        """Test errores al calcular salario pendiente"""
        # Días pendientes negativos
        with pytest.raises(ValueError, match="Días pendientes no pueden ser negativos"):
            calculator.calculate_salario_pendiente(2000000, -5)

        # Salario mensual cero o negativo
        with pytest.raises(ValueError, match="Salario mensual debe ser mayor a cero"):
            calculator.calculate_salario_pendiente(0, 5)

        with pytest.raises(ValueError, match="Salario mensual debe ser mayor a cero"):
            calculator.calculate_salario_pendiente(-100000, 5)

    def test_calculate_indemnizacion_completa_finiquito_alternative_cases(
        self, calculator
    ):
        """Test cálculo completo con diferentes escenarios FINIQUITO"""
        # Caso con contrato a término fijo
        input_data = {
            "modo": "FINIQUITO",
            "fecha_ingreso": "2023-01-01",
            "fecha_corte": "2023-06-01",  # 5 meses
            "tipo_contrato": "fijo",
            "motivo_terminacion": "despido",
            "salario_mensual": 2000000,
            "salario_pendiente_dias": 10,
        }
        sbl_general = 2000000

        resultado = calculator.calculate_indemnizacion_completa(input_data, sbl_general)

        # Debería tener indemnización (término fijo)
        assert resultado["indemnizacion"]["aplica"] is True
        assert resultado["indemnizacion"]["valor"] > 0
        assert resultado["indemnizacion"]["tipo_calculo"] == "termino_fijo"

        # Debería tener salario pendiente
        assert "valor" in resultado["salario_pendiente"]
        assert resultado["salario_pendiente"]["dias_pendientes"] == 10

    def test_calculate_indemnizacion_completa_varios_motivos(self, calculator):
        """Test cálculo completo con varios motivos de terminación"""
        motivos_aplican = ["despido", "terminacion_empresa"]
        motivos_no_aplican = ["muerte", "incapacidad_absoluta"]

        input_data = {
            "modo": "FINIQUITO",
            "fecha_ingreso": "2023-01-01",
            "fecha_corte": "2024-01-01",
            "tipo_contrato": "indefinido",
            "salario_mensual": 2000000,
        }
        sbl_general = 2000000

        # Motivos que sí aplican
        for motivo in motivos_aplican:
            input_data["motivo_terminacion"] = motivo
            resultado = calculator.calculate_indemnizacion_completa(
                input_data, sbl_general
            )
            assert resultado["indemnizacion"]["aplica"] is True

        # Motivos que no aplican
        for motivo in motivos_no_aplican:
            input_data["motivo_terminacion"] = motivo
            resultado = calculator.calculate_indemnizacion_completa(
                input_data, sbl_general
            )
            assert resultado["indemnizacion"]["aplica"] is False
            assert resultado["indemnizacion"]["valor"] == 0
