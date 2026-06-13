import json
import pytest
from pathlib import Path
from liquidator.core.engine import LiquidacionEngine
from liquidator.core.input_parser import parse_input_file


class TestPeriodicaIntegration:
    """Tests de integración para modo PERIÓDICA"""

    @pytest.fixture
    def engine(self):
        return LiquidacionEngine()

    @pytest.fixture
    def finca_rural_input(self):
        input_path = (
            Path(__file__).parent.parent.parent.parent
            / "examples"
            / "example_finca_rural.json"
        )
        return parse_input_file(str(input_path))

    @pytest.fixture
    def salario_variable_input(self):
        input_path = (
            Path(__file__).parent.parent.parent.parent
            / "examples"
            / "example_salario_variable.json"
        )
        return parse_input_file(str(input_path))

    def test_finca_rural_completo(self, engine, finca_rural_input):
        """Test completo para trabajador de finca rural"""
        resultado = engine.process_input(finca_rural_input)

        # Verificar estructura básica
        assert "desglose" in resultado
        assert "compliance_report" in resultado

        # Verificar compliance
        assert resultado["compliance_report"]["compliance_status"] == "GO"

        # Verificar cálculos principales
        desglose = resultado["desglose"]

        # SBL calculations
        assert desglose["SBL_GENERAL"] == 2200000  # 2,000,000 + 200,000 (conectividad)
        assert desglose["SBL_VACACIONES"] == 2000000  # Sin auxilio ni extras

        # Prestaciones sociales
        assert desglose["cesantias"]["valor"] == 2200000
        assert desglose["intereses_cesantias"]["valor"] == 264000
        assert desglose["prima"]["valor"] > 0  # Debe ser positivo

        # Vacaciones deben ser 0 en modo PERIÓDICA
        assert desglose["vacaciones"]["valor"] == 0

        # Total debe coincidir con la suma
        total_esperado = (
            desglose["cesantias"]["valor"]
            + desglose["intereses_cesantias"]["valor"]
            + desglose["prima"]["valor"]
        )
        assert resultado["total_liquidacion_periodica"] == total_esperado

        # Verificar validaciones y alertas relevantes
        assert "auxilio_transporte_excluido" in resultado["validaciones_y_alertas"]
        assert "auxilio_conectividad_advertencia" in resultado["validaciones_y_alertas"]

    def test_salario_variable_completo(self, engine, salario_variable_input):
        """Test completo para salario variable"""
        resultado = engine.process_input(salario_variable_input)

        # Verificar compliance
        assert resultado["compliance_report"]["compliance_status"] == "GO"

        desglose = resultado["desglose"]

        # Verificar que el SBL_GENERAL refleja el promedio correcto
        # Salario base promedio: ~1,991,667 + comisiones (150,000) + extras (100,000) + bonificaciones (50,000)
        assert desglose["SBL_GENERAL"] > 2200000  # Debe ser mayor que 2,200,000

        # Verificar cálculos de prestaciones
        assert desglose["cesantias"]["valor"] > 0
        assert desglose["intereses_cesantias"]["valor"] > 0
        assert desglose["prima"]["valor"] > 0

        # Verificar plazos de pago documentados
        assert desglose["cesantias"]["plazo_pago_legal"] == "2026-02-14"
        assert desglose["intereses_cesantias"]["plazo_pago_legal"] == "2026-01-31"
        assert desglose["prima"]["plazo_pago_legal"] in ["2025-06-30", "2025-12-20"]

        # Verificar normas aplicadas
        normas_esperadas = ["Art.249-250 CST", "Ley 50/1990 Art.99", "Art.306-308 CST"]
        for norma in normas_esperadas:
            assert norma in resultado["normas_aplicadas"]

    def test_validacion_compliance_completa(self, engine, finca_rural_input):
        """Test de validación completa del compliance report"""
        resultado = engine.process_input(finca_rural_input)
        compliance = resultado["compliance_report"]

        # Verificar estructura del compliance report
        assert "summary" in compliance
        assert "checks" in compliance
        assert "blocking_failures" in compliance

        # Contar checks ejecutados
        checks_ejecutados = len(compliance["checks"])
        assert checks_ejecutados >= 10  # Debe haber al menos 10 checks

        # Verificar que las validaciones críticas pasaron
        checks_dict = {check["id"]: check for check in compliance["checks"]}

        # Validaciones críticas que deben pasar
        validaciones_criticas = [
            "V001",
            "V002",
            "V003",
            "V004",
            "V005",
            "V007",
            "V008",
            "V009",
            "V010",
        ]
        for validacion_id in validaciones_criticas:
            assert validacion_id in checks_dict
            assert checks_dict[validacion_id]["result"] in ["PASS", "WARN"]

    def test_hash_calculations(self, engine, finca_rural_input):
        """Test de cálculo de hashes para auditoría"""
        resultado = engine.process_input(finca_rural_input)

        # Verificar presencia de hashes
        assert "input_hash" in resultado["meta"]
        assert "output_hash" in resultado["meta"]
        assert "params_version" in resultado["meta"]

        # Verificar formato de hashes
        assert resultado["meta"]["input_hash"].startswith("sha256:")
        assert resultado["meta"]["output_hash"].startswith("sha256:")

        # Verificar que los hashes no están vacíos
        assert len(resultado["meta"]["input_hash"]) > 10
        assert len(resultado["meta"]["output_hash"]) > 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
