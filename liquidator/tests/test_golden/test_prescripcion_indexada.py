"""Test golden — Tarea 2.X (Fase 2-bis, addendum SL2630-2024).

Caso: cesantias de 2024 ($1.500.000) indexadas a 2025-06-09 con IPC DANE
acumulado. Verifica que el motor:

1. Activa la indexacion cuando el input declara `periodos_no_pagados`.
2. Calcula el VA con ``IPCIndexador`` y produce un renglon
   ``cesantias_indexado`` con la metadata legal completa.
3. NO incluye el renglon en el total si el periodo esta prescrito
   (Art. 488 CST, 3 anios).
4. NO altera la regresion del caso canonico (sin periodos_no_pagados
   el motor se comporta como v2.0.0).
5. El compliance status refleja el V011 (regla V_INDEXACION_IPC).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from liquidator.core.engine import LiquidacionEngine

REPO_ROOT = Path(__file__).resolve().parents[3]
INPUT_PATH = REPO_ROOT / "examples" / "inputs" / "prescripcion_indexada.json"
EXPECTED_PATH = REPO_ROOT / "examples" / "expected" / "prescripcion_indexada_result.json"


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def input_data() -> dict[str, Any]:
    return json.loads(INPUT_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def expected_meta() -> dict[str, Any]:
    return json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def engine() -> LiquidacionEngine:
    return LiquidacionEngine()


# ============================================================================
# TESTS: indexacion de periodo NO prescrito
# ============================================================================

class TestIndexarPeriodoNoPrescrito:
    """Caso golden: periodo dentro de los 3 anios de prescripcion."""

    def test_cesantias_indexado_presente_en_desglose(
        self, engine: LiquidacionEngine, input_data: dict[str, Any]
    ):
        out = engine.process_input(input_data)
        desglose = out.get("desglose", {})
        assert "cesantias_indexado" in desglose, (
            f"Renglon cesantias_indexado no encontrado en desglose. "
            f"Claves: {list(desglose.keys())}"
        )

    def test_cesantias_indexado_tiene_va_mayor_que_vh(
        self, engine: LiquidacionEngine, input_data: dict[str, Any]
    ):
        """VA debe ser mayor que VH (la indexacion refleja la perdida de
        poder adquisitivo acumulada)."""
        out = engine.process_input(input_data)
        renglon = out["desglose"]["cesantias_indexado"]
        assert renglon["valor"] > renglon["valor_historico"], (
            f"VA={renglon['valor']} no es mayor que VH={renglon['valor_historico']}. "
            f"Esperado: VA > VH (perdida de poder adquisitivo)."
        )

    def test_cesantias_indexado_va_aproximadamente_1599543(
        self,
        engine: LiquidacionEngine,
        input_data: dict[str, Any],
        expected_meta: dict[str, Any],
    ):
        """VA = 1.500.000 × (IPC 2025-06 / IPC 2024-02) ≈ 1.599.543.

        Tolerancia: ±$10 (1 peso por redondeo + margen por precision
        de los indices DANE reconstruidos via variacion anual).
        """
        out = engine.process_input(input_data)
        va = out["desglose"]["cesantias_indexado"]["valor"]
        esperado = expected_meta["cesantias_indexado_esperado"][
            "valor_actualizado_aprox"
        ]
        assert abs(va - esperado) <= expected_meta["_meta"]["tolerancia_va"], (
            f"VA={va}, esperado≈{esperado} (±{expected_meta['_meta']['tolerancia_va']})"
        )

    def test_cesantias_indexado_incluye_evidencia_legal_y_formula(
        self, engine: LiquidacionEngine, input_data: dict[str, Any]
    ):
        """Renglon debe llevar la trazabilidad legal completa."""
        out = engine.process_input(input_data)
        renglon = out["desglose"]["cesantias_indexado"]
        assert "SL2630" in renglon["evidencia_legal"]
        assert "Art. 488" in renglon["evidencia_legal"]
        assert "IPC" in renglon["formula"]
        assert renglon["norma"] == "SL2630-2024; Art. 488 CST"

    def test_compliance_v011_pasa_sin_prescripcion(
        self, engine: LiquidacionEngine, input_data: dict[str, Any]
    ):
        """Regla V011 (V_INDEXACION_IPC) debe pasar (PASS) con indexables."""
        out = engine.process_input(input_data)
        report = out.get("compliance_report", {})
        checks = report.get("checks", [])
        v011 = next((c for c in checks if c["id"] == "V011"), None)
        assert v011 is not None, "V011 no encontrada en compliance.checks"
        # V011 puede ser PASS o WARN segun prescripcion; aca NO prescrito => PASS
        assert v011["result"] == "PASS", (
            f"V011 result esperado PASS, obtenido {v011['result']}. "
            f"Evidence: {v011.get('evidence')}"
        )

    def test_alerta_indexacion_ipc_resumen(
        self, engine: LiquidacionEngine, input_data: dict[str, Any]
    ):
        out = engine.process_input(input_data)
        alertas = out.get("validaciones_y_alertas", {})
        assert "indexacion_ipc_resumen" in alertas
        assert "1 indexado" in alertas["indexacion_ipc_resumen"]


# ============================================================================
# TESTS: periodo prescrito (Art. 488 CST, 3 anios)
# ============================================================================

class TestPeriodoPrescrito:
    """Si la exigibilidad es > 3 anios, NO se indexa (regla Art. 488 CST)."""

    def test_periodo_prescrito_no_aparece_en_total(
        self, engine: LiquidacionEngine, input_data: dict[str, Any]
    ):
        # Modificamos el input para que la exigibilidad sea > 3 anios
        input_data["periodos_no_pagados"][0]["fecha_exigibilidad"] = "2021-01-01"
        input_data["periodos_no_pagados"][0]["fecha_referencia_indexacion"] = (
            "2025-06-09"
        )
        out = engine.process_input(input_data)
        desglose = out.get("desglose", {})
        # El renglon prescrito debe aparecer con valor 0
        assert "cesantias_indexado_prescrito" in desglose
        renglon_pres = desglose["cesantias_indexado_prescrito"]
        assert renglon_pres["valor"] == 0
        assert renglon_pres["estado"] == "PRESCRITO"
        # NO debe aparecer el renglon indexado (con VA > 0)
        assert "cesantias_indexado" not in desglose

    def test_periodo_prescrito_genera_warning(
        self, engine: LiquidacionEngine, input_data: dict[str, Any]
    ):
        input_data["periodos_no_pagados"][0]["fecha_exigibilidad"] = "2021-01-01"
        input_data["periodos_no_pagados"][0]["fecha_referencia_indexacion"] = (
            "2025-06-09"
        )
        out = engine.process_input(input_data)
        alertas = out.get("validaciones_y_alertas", {})
        assert "periodo_cesantias_prescrito" in alertas
        assert "Art. 488" in alertas["periodo_cesantias_prescrito"]

    def test_compliance_v011_warning_por_prescripcion(
        self, engine: LiquidacionEngine, input_data: dict[str, Any]
    ):
        input_data["periodos_no_pagados"][0]["fecha_exigibilidad"] = "2021-01-01"
        input_data["periodos_no_pagados"][0]["fecha_referencia_indexacion"] = (
            "2025-06-09"
        )
        out = engine.process_input(input_data)
        report = out.get("compliance_report", {})
        checks = report.get("checks", [])
        v011 = next((c for c in checks if c["id"] == "V011"), None)
        assert v011 is not None
        assert v011["result"] == "WARN", (
            f"V011 result esperado WARN por prescripcion, obtenido {v011['result']}"
        )


# ============================================================================
# TESTS: no-regresion del caso canonico
# ============================================================================

class TestNoRegresionCasoCanonico:
    """El caso canonico (sin periodos_no_pagados) sigue funcionando como v2.0.0."""

    def test_input_sin_periodos_no_pagados_se_comporta_como_v200(
        self, engine: LiquidacionEngine
    ):
        inp_minimo = {
            "modo": "PERIODICA",
            "fecha_ingreso": "2025-11-16",
            "fecha_corte": "2026-06-09",
            "salario_mensual": 2200000,
            "tipo_contrato": "INDEFINIDO",
        }
        out = engine.process_input(inp_minimo)
        desglose = out.get("desglose", {})
        # NO debe haber renglones de indexacion
        assert "cesantias_indexado" not in desglose
        assert "cesantias_indexado_prescrito" not in desglose

    def test_input_con_lista_vacia_se_comporta_como_v200(
        self, engine: LiquidacionEngine
    ):
        inp = {
            "modo": "PERIODICA",
            "fecha_ingreso": "2025-11-16",
            "fecha_corte": "2026-06-09",
            "salario_mensual": 2200000,
            "tipo_contrato": "INDEFINIDO",
            "periodos_no_pagados": [],  # lista vacia
        }
        out = engine.process_input(inp)
        desglose = out.get("desglose", {})
        assert "cesantias_indexado" not in desglose

    def test_compliance_v011_pasa_sin_input(
        self, engine: LiquidacionEngine
    ):
        inp = {
            "modo": "PERIODICA",
            "fecha_ingreso": "2025-11-16",
            "fecha_corte": "2026-06-09",
            "salario_mensual": 2200000,
            "tipo_contrato": "INDEFINIDO",
        }
        out = engine.process_input(inp)
        report = out.get("compliance_report", {})
        checks = report.get("checks", [])
        v011 = next((c for c in checks if c["id"] == "V011"), None)
        assert v011 is not None
        assert v011["result"] == "PASS"  # opt-in: no aplica, pasa
