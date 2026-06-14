"""Test golden — Tarea 2.B-ter (Fase 2, addendum finiquito/vacaciones).

Caso: renuncia voluntaria con 7.5 días de vacaciones pendientes,
SBL 2.200.000, 212 días (2025-11-16 a 2026-06-15).

Verifica que el motor:
1. Activa vacaciones compensadas en finiquito cuando modo=FINIQUITO
   y vacaciones.dias_pendientes > 0.
2. Calcula el renglón con fórmula Art. 189-190 CST: (SBL/30) x dias_pendientes.
3. El valor es exactamente $550.000 para 7.5 días con SBL 2.200.000.
4. NO altera la regresión del caso canónico PERIODICA (sin vacaciones,
   sin finiquito).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from liquidator.core.engine import LiquidacionEngine

REPO_ROOT = Path(__file__).resolve().parents[3]
INPUT_PATH = REPO_ROOT / "examples" / "inputs" / "finiquito_renuncia_212d.json"


@pytest.fixture
def input_data() -> dict[str, Any]:
    return json.loads(INPUT_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def engine() -> LiquidacionEngine:
    return LiquidacionEngine()


# ============================================================================
# TESTS: vacaciones compensadas en finiquito
# ============================================================================


class TestVacacionesCompensadasFiniquito:
    """Caso golden del addendum: renuncia voluntaria con 7.5 dias."""

    def test_vacaciones_compensadas_presente_en_desglose(
        self, engine: LiquidacionEngine, input_data: dict[str, Any]
    ):
        out = engine.process_input(input_data)
        desglose = out.get("desglose", {})
        assert "vacaciones_compensadas_finiquito" in desglose, (
            f"Renglon vacaciones_compensadas_finiquito no encontrado en desglose. "
            f"Claves: {list(desglose.keys())}"
        )

    def test_vacaciones_compensadas_valor_550000(
        self, engine: LiquidacionEngine, input_data: dict[str, Any]
    ):
        """7.5 dias x (2.200.000 / 30) = 550.000 exacto."""
        out = engine.process_input(input_data)
        renglon = out["desglose"]["vacaciones_compensadas_finiquito"]
        assert renglon["valor"] == 550000, (
            f"Esperado 550000, obtenido {renglon['valor']}"
        )
        assert renglon["dias"] == 7.5

    def test_vacaciones_compensadas_evidencia_legal(
        self, engine: LiquidacionEngine, input_data: dict[str, Any]
    ):
        """Renglon debe llevar la trazabilidad legal completa."""
        out = engine.process_input(input_data)
        renglon = out["desglose"]["vacaciones_compensadas_finiquito"]
        assert "Art. 189" in renglon["evidencia_legal"]
        assert "Art. 190" in renglon["evidencia_legal"]
        assert renglon["obligatorio_en_finiquito"] is True
        assert renglon["formula"] == "SBL / 30 × días_pendientes"

    def test_vacaciones_compensadas_contribuye_al_total(
        self, engine: LiquidacionEngine, input_data: dict[str, Any]
    ):
        """El total debe reflejar las vacaciones compensadas.
        Verificamos que el total_liquidacion supera las cesantias+intereses+prima
        (las vacaciones compensadas suman $550.000)."""
        out = engine.process_input(input_data)
        total = out.get("total_liquidacion", 0)
        desglose = out.get("desglose", {})
        # Sumar todos los conceptos del desglose excepto SBL_*
        suma_conceptos = sum(
            v.get("valor", 0)
            for k, v in desglose.items()
            if isinstance(v, dict) and not k.startswith("SBL_")
        )
        # El total debe ser al menos la suma de conceptos
        assert total >= suma_conceptos, (
            f"Total={total:,} < suma_conceptos={suma_conceptos:,}"
        )
        # Las vacaciones compensadas deben estar incluidas
        assert total > 3_000_000, (
            f"Total={total:,} muy bajo; vacaciones compensadas quizas no sumadas"
        )

    def test_alerta_vacaciones_compensadas(
        self, engine: LiquidacionEngine, input_data: dict[str, Any]
    ):
        out = engine.process_input(input_data)
        alertas = out.get("validaciones_y_alertas", {})
        assert "vacaciones_compensadas_finiquito" in alertas
        assert "550,000" in alertas["vacaciones_compensadas_finiquito"]
        assert "Art. 189-190" in alertas["vacaciones_compensadas_finiquito"]


# ============================================================================
# TESTS: finiquito sin vacaciones pendientes
# ============================================================================


class TestFiniquitoSinVacaciones:
    """Si dias_pendientes = 0, NO se genera renglon compensado."""

    def test_finiquito_sin_dias_pendientes_no_genera_compensacion(
        self, engine: LiquidacionEngine
    ):
        inp = {
            "modo": "FINIQUITO",
            "fecha_ingreso": "2025-11-16",
            "fecha_corte": "2026-06-15",
            "salario_mensual": 2200000,
            "tipo_contrato": "INDEFINIDO",
            "motivo_terminacion": "renuncia_voluntaria",
            "fecha_terminacion_real": "2026-06-15",
            "vacaciones": {"dias_pendientes": 0, "dias_disfrutados": 0},
        }
        out = engine.process_input(inp)
        desglose = out.get("desglose", {})
        assert "vacaciones_compensadas_finiquito" not in desglose


# ============================================================================
# TESTS: no-regresion del caso canonico PERIODICA
# ============================================================================


class TestNoRegresionCasoCanonico:
    """El caso canonico PERIODICA NO debe generar vacaciones compensadas."""

    def test_periodica_sin_vacaciones_no_genera_compensacion(
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
        desglose = out.get("desglose", {})
        assert "vacaciones_compensadas_finiquito" not in desglose

    def test_periodica_con_vacaciones_no_genera_compensacion(
        self, engine: LiquidacionEngine
    ):
        """Modo PERIODICA con vacaciones declaradas NO debe compensar
        (las vacaciones en periodo vigente son logica distinta —
        acuerdo mutuo Art. 189, NO compensacion obligatoria en finiquito)."""
        inp = {
            "modo": "PERIODICA",
            "fecha_ingreso": "2025-11-16",
            "fecha_corte": "2026-06-09",
            "salario_mensual": 2200000,
            "tipo_contrato": "INDEFINIDO",
            "vacaciones": {"dias_pendientes": 7.5, "dias_disfrutados": 0},
        }
        out = engine.process_input(inp)
        desglose = out.get("desglose", {})
        # PERIODICA NO activa el hook de vacaciones compensadas finiquito
        assert "vacaciones_compensadas_finiquito" not in desglose
