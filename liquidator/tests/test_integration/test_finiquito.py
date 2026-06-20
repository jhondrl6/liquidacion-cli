from pathlib import Path

import pytest

from liquidator.core.engine import LiquidacionEngine
from liquidator.core.input_parser import parse_input_file


class TestFiniquitoIntegration:
    """Tests de integración para modo FINIQUITO"""

    @pytest.fixture
    def engine(self):
        return LiquidacionEngine()

    @pytest.fixture
    def finiquito_input(self):
        input_path = (
            Path(__file__).parent.parent.parent.parent
            / "examples"
            / "example_finiquito.json"
        )
        return parse_input_file(str(input_path))

    def test_finiquito_completo(self, engine, finiquito_input):
        """Test completo para modo FINIQUITO con indemnización"""
        resultado = engine.process_input(finiquito_input)

        # Verificar modo correcto
        assert resultado["meta"]["modo"] == "FINIQUITO"

        # Verificar compliance
        assert resultado["compliance_report"]["compliance_status"] in {"GO", "WARN"}

        desglose = resultado["desglose"]

        # Verificar que las vacaciones están incluidas
        assert desglose["vacaciones"]["valor"] > 0
        assert desglose["vacaciones"]["dias_liquidados"] == 15

        # Verificar cálculo de indemnización (debe existir en el resultado)
        assert "indemnizacion" in desglose or "total_indemnizacion" in resultado

        # Verificar salario pendiente
        assert "salario_pendiente" in desglose or "salario_pendiente" in resultado

        # Verificar plazos de pago (deben ser inmediatos para finiquito)
        plazo_esperado = "2025-11-15"  # Fecha de corte (pago inmediato)
        for concepto in ["cesantias", "intereses_cesantias", "prima"]:
            if concepto in desglose:
                assert desglose[concepto]["plazo_pago_legal"] == plazo_esperado

        # Verificar tope de indemnización aplicado
        if "indemnizacion" in desglose:
            smmlv_2025 = 1423500
            tope_maximo = 20 * smmlv_2025
            assert desglose["indemnizacion"]["valor"] <= tope_maximo

    def test_validaciones_especificas_finiquito(self, engine, finiquito_input):
        """Test de validaciones específicas para modo FINIQUITO"""
        resultado = engine.process_input(finiquito_input)
        compliance = resultado["compliance_report"]

        # Obtener checks como diccionario para fácil acceso
        checks_dict = {check["id"]: check for check in compliance["checks"]}

        # Verificar validaciones específicas de finiquito
        # V007: Vacaciones deben estar incluidas en finiquito
        assert "V007" in checks_dict
        assert (
            checks_dict["V007"]["result"] == "PASS"
        )  # Debe pasar porque vacaciones están incluidas

        # V008: Plazos de pago deben ser inmediatos
        assert "V008" in checks_dict
        assert checks_dict["V008"]["result"] == "PASS"

        # Verificar que hay alertas sobre pago inmediato
        assert (
            "plazo_pago_inmediato" in str(resultado["validaciones_y_alertas"]).lower()
        )

    def test_calculo_indemnizacion(self, engine, finiquito_input):
        """Test específico de cálculo de indemnización"""
        resultado = engine.process_input(finiquito_input)
        desglose = resultado["desglose"]

        # Verificar que indemnización existe y es positiva cuando aplica
        if "indemnizacion" in desglose and desglose["indemnizacion"]["valor"] > 0:
            # Indemnización debe estar dentro del tope legal (20 SMMLV)
            smmlv_2025 = 1423500
            tope_maximo = 20 * smmlv_2025
            assert desglose["indemnizacion"]["valor"] <= tope_maximo
            assert desglose["indemnizacion"]["dias_liquidados"] > 0

    def test_total_finiquito_coherente(self, engine, finiquito_input):
        """Test de coherencia del total en modo finiquito"""
        resultado = engine.process_input(finiquito_input)
        desglose = resultado["desglose"]

        # Calcular total manualmente
        total_manual = 0

        # Conceptos que deben sumarse
        conceptos = [
            "cesantias",
            "intereses_cesantias",
            "prima",
            "vacaciones",
            "salario_pendiente",
        ]

        for concepto in conceptos:
            if concepto in desglose and "valor" in desglose[concepto]:
                total_manual += desglose[concepto]["valor"]

        # Agregar indemnización si existe
        if "indemnizacion" in desglose:
            total_manual += desglose["indemnizacion"]["valor"]

        # Verificar que el total coincide (con margen de redondeo)
        total_calculado = resultado.get(
            "total_finiquito", resultado.get("total_liquidacion", 0)
        )
        diferencia = abs(total_calculado - total_manual)

        assert diferencia <= 1000  # Margen de $1,000 para redondeos


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
