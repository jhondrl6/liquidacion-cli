"""Tests golden de anualización salarial — Tarea 2.B-bis.

SL2630-2024: validación de que el motor calcula correctamente cuando
el SBL varía por año calendario.
"""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from liquidator.core.params_provider import ParamsProvider
from liquidator.core.salario_resolver import (
    SalarioResolver,
    SegmentoCalculo,
    segmentar_periodo,
)
from liquidator.contracts.input_model import Salario
from liquidator.core.workflow_orchestrator import WorkflowOrchestrator

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

REPO = Path(__file__).resolve().parents[3]
CANONICO_PATH = REPO / "examples" / "inputs" / "caso_canonico_periodico_206d.json"


def _load_canonico() -> dict:
    return json.loads(CANONICO_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _provs_para_canonico() -> dict[int, ParamsProvider]:
    """ParamsProvider para el rango del caso canónico."""
    provs = ParamsProvider.for_range(
        date(2025, 11, 16),
        date(2026, 6, 9),
    )
    return provs


def _flat_input(anidado: bool = False, sbl_por_anio: dict | None = None) -> dict:
    """Construye un input plano compatible con el WorkflowOrchestrator.

    El orquestador usa ``salario_mensual`` como campo plano.  Cuando
    ``anidado=True``, también se incluye un objeto ``salario`` anidado
    con los campos de anualización.
    """
    inp = {
        "modo": "PERIODICA",
        "fecha_ingreso": "2025-11-16",
        "fecha_corte": "2026-06-09",
        "salario_mensual": 2200000,
        "auxilio_transporte": False,
        "tipo_contrato": "indefinido",
    }
    if anidado:
        salario_obj: dict = {
            "SBL": 2200000,
            "auxilio_transporte": False,
            "variable": False,
        }
        if sbl_por_anio is not None:
            salario_obj["sbl_por_anio"] = sbl_por_anio
        inp["salario"] = salario_obj
    return inp


# ---------------------------------------------------------------------------
# Regresión — caso canónico con SBL constante NO cambia
# ---------------------------------------------------------------------------


class TestRegresionCanonica:
    """El caso canónico con SBL=2.200.000 constante produce el mismo
    resultado con o sin anualización activada."""

    def test_canonico_sin_campos_nuevos_flat_input(self):
        """Input plano (sin salario anidado) → comportamiento actual."""
        inp = _flat_input(anidado=False)
        params = ParamsProvider.current().to_dict()
        orch = WorkflowOrchestrator(params)
        result = orch.execute(inp)
        # Cesantías: 2.200.000 × 206 / 360 = 1.258.889
        assert result.calculation_results["cesantias"] == 1258889

    def test_canonico_con_salario_anidado_sin_anualizacion(self):
        """Input con salario anidado pero SIN sbl_por_anio → mismo resultado."""
        inp = _flat_input(anidado=True, sbl_por_anio=None)
        params = ParamsProvider.current().to_dict()
        orch = WorkflowOrchestrator(params)
        result = orch.execute(inp)
        # Mismo resultado porque no hay campos de anualización
        assert result.calculation_results["cesantias"] == 1258889

    def test_canonico_con_sbl_por_anio_constante(self):
        """sbl_por_anio con el mismo SBL en ambos años → mismo resultado."""
        inp = _flat_input(
            anidado=True,
            sbl_por_anio={2025: 2200000, 2026: 2200000},
        )
        params = ParamsProvider.current().to_dict()
        orch = WorkflowOrchestrator(params)
        result = orch.execute(inp)
        # idéntico porque SBL es constante
        assert result.calculation_results["cesantias"] == 1258889

    def test_canonico_con_sbl_por_anio_constante_intereses(self):
        """Intereses también son idénticos con SBL constante.

        La vía segmentada puede diferir en ±2 pesos por redondeo
        (la vía plana usa 207 días inclusive vs 206 segmentados).
        """
        inp = _flat_input(
            anidado=True,
            sbl_por_anio={2025: 2200000, 2026: 2200000},
        )
        params = ParamsProvider.current().to_dict()
        orch = WorkflowOrchestrator(params)
        result = orch.execute(inp)
        # Intereses calculados con cesantías totales y 206 días.
        # 1.258.889 × 206 × 0.12 / 360 = 86.444 (redondeo half-up)
        interes = result.calculation_results["intereses_cesantias"]
        assert interes == pytest.approx(86444, abs=2)


# ---------------------------------------------------------------------------
# Caso nuevo — SBL variable por año
# ---------------------------------------------------------------------------


class TestSBLVariable:
    """SBL cambia de 2.200.000 (2025) a 2.400.000 (2026) → resultados distintos."""

    def test_sbl_variable_cesantias(self):
        """Cesantías con SBL variable por año."""
        inp = _flat_input(
            anidado=True,
            sbl_por_anio={2025: 2200000, 2026: 2400000},
        )
        params = ParamsProvider.current().to_dict()
        orch = WorkflowOrchestrator(params)
        result = orch.execute(inp)
        # 2025: 2.200.000 × 46 / 360 = 281.111
        # 2026: 2.400.000 × 160 / 360 = 1.066.667
        # Total: 1.347.778
        assert result.calculation_results["cesantias"] == 1347778

    def test_sbl_variable_intereses(self):
        """Intereses con SBL variable por año.

        Con cesantías totales = 1.347.778 y 206 días:
        1.347.778 × 206 × 0.12 / 360 = 92.547 (redondeo half-up).
        Distinto del caso canónico (86.444) porque las cesantías base
        son mayores (1.347.778 vs 1.258.889).
        """
        inp = _flat_input(
            anidado=True,
            sbl_por_anio={2025: 2200000, 2026: 2400000},
        )
        params = ParamsProvider.current().to_dict()
        orch = WorkflowOrchestrator(params)
        result = orch.execute(inp)
        interes = result.calculation_results["intereses_cesantias"]
        # Verificar que es distinto del caso canónico (86.444)
        assert interes != 86444
        assert interes == 92547

    def test_sbl_variable_es_distinto_del_canonico(self):
        """SBL variable produce cesantías DISTINTAS del caso canónico."""
        inp = _flat_input(
            anidado=True,
            sbl_por_anio={2025: 2200000, 2026: 2400000},
        )
        params = ParamsProvider.current().to_dict()
        orch = WorkflowOrchestrator(params)
        result = orch.execute(inp)

        # Caso canónico (SBL constante 2.200.000)
        inp_canon = _flat_input(anidado=False)
        orch_canon = WorkflowOrchestrator(params)
        result_canon = orch_canon.execute(inp_canon)

        assert result.calculation_results["cesantias"] != result_canon.calculation_results["cesantias"]


# ---------------------------------------------------------------------------
# SalarioResolver con historial_salarial a través del orquestador
# ---------------------------------------------------------------------------


class TestHistorialSalarialOrquestador:
    """El orquestador usa el historial cuando está presente."""

    def test_historial_promedio_constante(self):
        """historial_salarial con promedio 2.200.000 → resultado canónico."""
        inp = _flat_input(anidado=True, sbl_por_anio=None)
        inp["salario"]["historial_salarial"] = [
            {"año": 2025, "mes": 11, "valor": 2100000},
            {"año": 2025, "mes": 12, "valor": 2300000},
            {"año": 2026, "mes": 1, "valor": 2200000},
        ]
        params = ParamsProvider.current().to_dict()
        orch = WorkflowOrchestrator(params)
        result = orch.execute(inp)
        # 2025: avg(2.1M, 2.3M) = 2.2M → cesantías 2025 = 2.2M × 46 / 360 = 281.111
        # 2026: avg(2.2M) = 2.2M → cesantías 2026 = 2.2M × 160 / 360 = 977.778
        # Total: 1.258.889 (idéntico al canónico porque el promedio es 2.2M)
        assert result.calculation_results["cesantias"] == 1258889

    def test_historial_variable(self):
        """historial_salarial con promedios distintos por año."""
        inp = _flat_input(anidado=True, sbl_por_anio=None)
        inp["salario"]["historial_salarial"] = [
            {"año": 2025, "mes": 11, "valor": 2100000},
            {"año": 2025, "mes": 12, "valor": 2300000},
            {"año": 2026, "mes": 1, "valor": 2400000},
            {"año": 2026, "mes": 2, "valor": 2400000},
        ]
        params = ParamsProvider.current().to_dict()
        orch = WorkflowOrchestrator(params)
        result = orch.execute(inp)
        # 2025: avg(2.1M, 2.3M) = 2.2M → 2.2M × 46 / 360 = 281.111
        # 2026: avg(2.4M, 2.4M) = 2.4M → 2.4M × 160 / 360 = 1.066.667
        # Total: 1.347.778
        assert result.calculation_results["cesantias"] == 1347778
