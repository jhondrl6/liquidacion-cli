import json
import pytest
from pathlib import Path
from liquidator.core.engine import LiquidacionEngine
from liquidator.core.input_parser import parse_input_file


class TestEdgeCasesIntegration:
    """Tests de integración para casos de borde"""

    @pytest.fixture
    def engine(self):
        return LiquidacionEngine()

    def load_edge_case(self, filename):
        """Cargar caso de borde desde fixtures"""
        fixtures_path = Path(__file__).parent.parent / "fixtures" / "edge_cases"
        return parse_input_file(str(fixtures_path / filename))

    @pytest.fixture
    def contrato_1_dia_input(self):
        return self.load_edge_case("contrato_1_dia.json")

    @pytest.fixture
    def contrato_365_dias_input(self):
        return self.load_edge_case("contrato_365_dias.json")

    @pytest.fixture
    def salario_limite_auxilio_input(self):
        return self.load_edge_case("salario_limite_auxilio.json")

    @pytest.fixture
    def periodo_recargo_dominical_input(self):
        return self.load_edge_case("periodo_recargo_dominical.json")

    def test_contrato_1_dia(self, engine, contrato_1_dia_input):
        """Test para contrato de 1 día"""
        resultado = engine.process_input(contrato_1_dia_input)

        # Verificar que no hay errores
        assert resultado["compliance_report"]["compliance_status"] == "GO"

        desglose = resultado["desglose"]

        # Verificar cálculos para 1 día
        dias_servicio = 1
        sbl_general = desglose["SBL_GENERAL"]

        # Cesantías para 1 día
        cesantias_esperadas = (sbl_general * dias_servicio) / 360
        assert abs(desglose["cesantias"]["valor"] - cesantias_esperadas) <= 1

        # Intereses para 1 día (deben ser mínimos)
        intereses_esperados = (
            desglose["cesantias"]["valor"] * dias_servicio * 0.12
        ) / 360
        assert abs(desglose["intereses_cesantias"]["valor"] - intereses_esperados) <= 1

        # Prima: depende del semestre, pero debe ser proporcional
        assert desglose["prima"]["dias_liquidados"] >= 0
        assert desglose["prima"]["valor"] >= 0

    def test_contrato_365_dias(self, engine, contrato_365_dias_input):
        """Test para contrato de 365 días (año bisiesto)"""
        resultado = engine.process_input(contrato_365_dias_input)

        # Verificar compliance
        assert resultado["compliance_report"]["compliance_status"] == "GO"

        desglose = resultado["desglose"]

        # Verificar días de servicio
        # 2024 es año bisiesto, 366 días, pero el periodo es 365 días (2024-01-01 a 2024-12-31)
        assert desglose["cesantias"]["dias_liquidados"] == 365

        # Verificar cálculo de cesantías para 365 días
        sbl_general = desglose["SBL_GENERAL"]
        cesantias_esperadas = (sbl_general * 365) / 360
        diferencia = abs(desglose["cesantias"]["valor"] - cesantias_esperadas)
        assert diferencia <= 1000  # Margen para redondeo

        # Verificar que todos los conceptos tienen valores razonables
        assert desglose["cesantias"]["valor"] > 0
        assert desglose["intereses_cesantias"]["valor"] > 0
        assert desglose["prima"]["valor"] > 0

    def test_salario_limite_auxilio(self, engine, salario_limite_auxilio_input):
        """Test para salario en límite de auxilio (2 SMMLV)"""
        resultado = engine.process_input(salario_limite_auxilio_input)

        # Verificar compliance
        assert resultado["compliance_report"]["compliance_status"] == "GO"

        desglose = resultado["desglose"]
        compliance = resultado["compliance_report"]

        # Obtener checks como diccionario
        checks_dict = {check["id"]: check for check in compliance["checks"]}

        # Verificar que V003 (auxilio transporte) pasó correctamente
        assert "V003" in checks_dict
        assert checks_dict["V003"]["result"] == "PASS"

        # Verificar que el SBL incluye auxilio de transporte (200,000)
        sbl_esperado = 2847000 + 200000  # Salario + auxilio transporte
        assert desglose["SBL_GENERAL"] == sbl_esperado

        # Verificar cesantías con el SBL correcto
        dias_servicio = 365  # 2024-01-01 a 2024-12-31
        cesantias_esperadas = (sbl_esperado * dias_servicio) / 360
        diferencia = abs(desglose["cesantias"]["valor"] - cesantias_esperadas)
        assert diferencia <= 1000

    def test_periodo_recargo_dominical(self, engine, periodo_recargo_dominical_input):
        """Test para periodo que cruza la fecha de aplicación de recargo dominical (2025-07-01)"""
        resultado = engine.process_input(periodo_recargo_dominical_input)

        # Verificar compliance
        assert resultado["compliance_report"]["compliance_status"] == "GO"

        # Verificar alertas sobre recargo dominical
        assert "recargo_dominical_aplicado" in resultado["validaciones_y_alertas"]

        # Verificar que el periodo incluye fechas posteriores a 2025-07-01
        alerta_texto = resultado["validaciones_y_alertas"]["recargo_dominical_aplicado"]
        assert "aplica" in alerta_texto.lower() or "incluye" in alerta_texto.lower()

        # Verificar normas aplicadas incluyen Ley 2466/2025
        assert "Ley 2466/2025" in resultado["normas_aplicadas"]

    def test_multiples_componentes_salariales(self, engine):
        """Test para múltiples componentes salariales"""
        input_data = self.load_edge_case("multiples_componentes.json")
        resultado = engine.process_input(input_data)

        # Verificar que todos los componentes se incluyeron en el SBL
        desglose = resultado["desglose"]
        sbl_general = desglose["SBL_GENERAL"]

        # Componentes esperados:
        # salario_mensual: 1,500,000
        # comisiones: 800,000
        # horas extras: 400,000
        # bonificaciones: 300,000
        # Total esperado: 3,000,000
        sbl_esperado = 1500000 + 800000 + 400000 + 300000
        assert sbl_general == sbl_esperado

        # Verificar cesantías
        dias_servicio = 365
        cesantias_esperadas = (sbl_esperado * dias_servicio) / 360
        diferencia = abs(desglose["cesantias"]["valor"] - cesantias_esperadas)
        assert diferencia <= 1000

    def test_todos_casos_borde_juntos(self, engine):
        """Test que ejecuta todos los casos de borde para verificar estabilidad"""
        casos = [
            "contrato_1_dia.json",
            "contrato_365_dias.json",
            "salario_limite_auxilio.json",
            "multiples_componentes.json",
            "periodo_recargo_dominical.json",
        ]

        resultados_exitosos = 0

        for caso in casos:
            try:
                input_data = self.load_edge_case(caso)
                resultado = engine.process_input(input_data)

                # Verificar que el compliance es GO
                assert resultado["compliance_report"]["compliance_status"] == "GO"

                # Verificar que hay valores calculados
                assert resultado["desglose"]["cesantias"]["valor"] >= 0
                assert resultado["desglose"]["intereses_cesantias"]["valor"] >= 0
                assert resultado["desglose"]["prima"]["valor"] >= 0

                resultados_exitosos += 1
            except Exception as e:
                print(f"Error en caso {caso}: {str(e)}")
                raise

        assert resultados_exitosos == len(
            casos
        ), f"Fallaron {len(casos) - resultados_exitosos} casos de borde"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
