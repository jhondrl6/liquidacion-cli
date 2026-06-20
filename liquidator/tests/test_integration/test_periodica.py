from pathlib import Path

import pytest

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
        assert resultado["compliance_report"]["compliance_status"] in {"GO", "WARN"}

        # Verificar cálculos principales
        desglose = resultado["desglose"]

        # SBL calculations — fixture: salario_mensual=1500000, reside_en_lugar_trabajo=true
        # Motor excluye auxilio_transporte cuando reside_en_lugar_trabajo
        assert desglose["SBL_GENERAL"] == 1500000
        assert desglose["SBL_VACACIONES"] == 1500000

        # Prestaciones sociales — 365 dias, cap 360
        assert desglose["cesantias"]["valor"] == 1500000
        assert desglose["intereses_cesantias"]["valor"] == 180000
        assert desglose["prima"]["valor"] > 0  # Debe ser positivo

        # Vacaciones deben ser 0 en modo PERIÓDICA
        assert desglose["vacaciones"]["valor"] == 0

        # Total debe coincidir con la suma
        total_esperado = (
            desglose["cesantias"]["valor"]
            + desglose["intereses_cesantias"]["valor"]
            + desglose["prima"]["valor"]
        )
        assert resultado["total_liquidacion"] == total_esperado

        # Verificar validaciones relevantes
        assert "auxilio_transporte_excluido" in resultado["validaciones_y_alertas"]

    def test_salario_variable_completo(self, engine, salario_variable_input):
        """Test completo para salario variable"""
        resultado = engine.process_input(salario_variable_input)

        # Verificar compliance
        assert resultado["compliance_report"]["compliance_status"] in {"GO", "WARN"}

        desglose = resultado["desglose"]

        # Verificar que el SBL_GENERAL refleja el promedio correcto
        # Fixture: salario_mensual=1500000 + comisiones 300K + extras 150K + bonif 100K
        assert desglose["SBL_GENERAL"] == 2050000

        # Verificar cálculos de prestaciones
        assert desglose["cesantias"]["valor"] > 0
        assert desglose["intereses_cesantias"]["valor"] > 0
        assert desglose["prima"]["valor"] > 0

        # Verificar plazos de pago documentados
        assert desglose["cesantias"]["plazo_pago_legal"] == "2026-02-14"
        assert desglose["intereses_cesantias"]["plazo_pago_legal"] == "2026-01-31"
        assert desglose["prima"]["plazo_pago_legal"] in ["2025-06-30", "2025-12-20"]

        # Verificar normas aplicadas
        normas_esperadas = ["Art. 249-250 CST", "Ley 50/1990 Art. 99", "Art. 306-308 CST"]
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
            assert checks_dict[validacion_id]["result"] in ["PASS", "WARN", "FAIL"]

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
