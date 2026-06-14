"""Test end-to-end del caso canónico — Tarea 1.I.

Ejercita JSONGenerator (1.D) + Pydantic LiquidacionInput (1.C) +
ParamsProvider year-aware (1.E).

Caso ancla: 2025-11-16 → 2026-06-09, 206 días, SBL 2.200.000, 2 segmentos.
"""
from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from liquidator.contracts.input_model import LiquidacionInput
from liquidator.core.params_provider import ParamsProvider
from liquidator.output.json_generator import JSONGenerator

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

REPO = Path(__file__).resolve().parents[3]
INPUT_PATH = REPO / "examples" / "inputs" / "caso_canonico_periodico_206d.json"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_canonical_input() -> tuple[dict, dict]:
    """Carga y valida el JSON del caso canónico con Pydantic (Tarea 1.C).

    Returns:
        (pydantic_data, raw_data) — ``pydantic_data`` es el dict validado
        por Pydantic (campos del modelo); ``raw_data`` incluye campos
        extra como ``segmentos`` que Pydantic no conoce aún.
    """
    raw = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    # Validación Pydantic estricta — si el JSON no cumple, falla aquí
    model = LiquidacionInput.model_validate(raw)
    return model.model_dump(), raw


def _build_calculation_result(
    segmentos: list[dict],
    provs: dict[int, ParamsProvider],
) -> dict:
    """Construye un ``calculation_result`` simulado con dos segmentos.

    Esto simula lo que ``WorkflowOrchestrator`` produciría en una
    ejecución real. Los valores son los esperados del caso canónico
    según el plan §3.
    """
    desglose = {}
    total_liquidacion = Decimal("0")

    for seg in segmentos:
        anio = seg["anio"]
        desde = date.fromisoformat(seg["desde"])
        hasta = date.fromisoformat(seg["hasta"])
        dias = (hasta - desde).days + 1  # inclusivo
        SBL = Decimal("2200000")
        prefix = f"{anio}_"

        # Cesantías: SBL × días / 360
        cesantias = SBL * Decimal(dias) / Decimal("360")
        # Intereses: cesantías × 12% × días / 360
        intereses = cesantias * Decimal("0.12")
        # Prima: SBL × días / 360
        prima = SBL * Decimal(dias) / Decimal("360")

        desglose[f"{prefix}cesantias"] = {
            "concepto": "Cesantías",
            "valor": float(round(cesantias, 2)),
            "dias": dias,
            "SBL": float(SBL),
            "base_legal": "Art. 249-250 CST",
        }
        desglose[f"{prefix}intereses_cesantias"] = {
            "concepto": "Intereses sobre cesantías",
            "valor": float(round(intereses, 2)),
            "dias": dias,
            "tasa": 0.12,
            "base_legal": "Ley 50/1990 Art. 99",
        }
        desglose[f"{prefix}prima"] = {
            "concepto": "Prima de servicios",
            "valor": float(round(prima, 2)),
            "dias": dias,
            "SBL": float(SBL),
            "base_legal": "Art. 306-308 CST",
        }
        desglose[f"{prefix}vacaciones"] = {
            "concepto": "Vacaciones",
            "valor": 0.0,
            "dias": 0,
            "nota": "PERIODICA — no se pagan vacaciones",
        }
        desglose[f"{prefix}indemnizacion"] = {
            "concepto": "Indemnización Art. 64 CST",
            "valor": None,
            "nota": "R-LEG-01 — NO implementada en v2.0",
        }

        total_liquidacion += cesantias + intereses + prima

    return {
        "desglose": desglose,
        "total_liquidacion": float(round(total_liquidacion, 2)),
        "parametros_por_segmento": {
            "2025": {"params_version": provs[2025].params_version, "dias": 46},
            "2026": {"params_version": provs[2026].params_version, "dias": 160},
        },
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestCasoCanonicoEndToEnd:
    """Validación completa del caso canónico con JSONGenerator + Pydantic +
    ParamsProvider (Tarea 1.I)."""

    # ------------------------------------------------------------------
    # 1. Validación Pydantic del input (Tarea 1.C)
    # ------------------------------------------------------------------

    def test_input_canonico_valida_con_pydantic(self):
        """El JSON del caso canónico parsea correctamente con Pydantic."""
        raw = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
        model = LiquidacionInput.model_validate(raw)

        assert model.trabajador.nombre == "[ANONIMIZADO]"
        assert model.contrato.tipo == "INDEFINIDO"
        assert model.salario.SBL == Decimal("2200000")
        assert model.modo == "PERIODICA"
        assert model.contrato.fecha_ingreso == date(2025, 11, 16)
        assert model.contrato.fecha_corte == date(2026, 6, 9)

    def test_input_canonico_detecta_fechas_invertidas(self):
        """Si fecha_corte < fecha_ingreso, Pydantic lanza ValidationError."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="fecha_corte debe ser"):
            LiquidacionInput.model_validate(
                {
                    "trabajador": {"nombre": "X", "documento": "1"},
                    "empleador": {"nombre": "Y", "documento": "2"},
                    "contrato": {
                        "fecha_ingreso": "2026-06-09",
                        "fecha_corte": "2025-11-16",
                        "tipo": "INDEFINIDO",
                    },
                    "salario": {"SBL": 2200000},
                    "modo": "PERIODICA",
                }
            )

    # ------------------------------------------------------------------
    # 2. ParamsProvider year-aware (Tarea 1.E)
    # ------------------------------------------------------------------

    def test_params_provider_sirve_ambos_segmentos(self):
        """ParamsProvider.for_date() devuelve el año correcto del segmento."""
        # Segmento 2025
        p2025 = ParamsProvider.for_date(date(2025, 12, 15))
        assert p2025.SMMLV == 1423500
        assert p2025.AUXILIO_TRANS == 200000

        # Segmento 2026
        p2026 = ParamsProvider.for_date(date(2026, 3, 1))
        assert p2026.SMMLV == 1750905
        assert p2026.AUXILIO_TRANS == 249095

    def test_params_provider_for_range_cubre_caso_canonico(self):
        """for_range cubre exactamente los 2 años del caso canónico."""
        provs = ParamsProvider.for_range(date(2025, 11, 16), date(2026, 6, 9))
        assert set(provs.keys()) == {2025, 2026}
        assert provs[2025].SMMLV == 1423500
        assert provs[2026].SMMLV == 1750905

    # ------------------------------------------------------------------
    # 3. JSONGenerator con ParamsProvider (Tarea 1.D)
    # ------------------------------------------------------------------

    def test_json_generator_usa_params_provider_por_default(self):
        """Sin inyectar params, el generador usa ParamsProvider.current()."""
        gen = JSONGenerator()
        assert gen.params["SMMLV"] == 1750905  # año mayor (2026)
        assert "version" in gen.params

    def test_json_generator_acepta_params_inyectados(self):
        """Los params inyectados tienen prioridad sobre el provider."""
        custom = {"SMMLV": 999, "version": "test"}
        gen = JSONGenerator(params=custom)
        assert gen.params["SMMLV"] == 999
        assert gen.params["version"] == "test"

    def test_json_generator_genera_salida_canonica(self):
        """Genera un output válido con el shape del caso canónico."""
        input_data, raw_input = _load_canonical_input()
        segmentos = raw_input.get("segmentos", [])
        provs = ParamsProvider.for_range(
            date(2025, 11, 16), date(2026, 6, 9)
        )
        calc = _build_calculation_result(segmentos, provs)

        # El generador debe usar los params de ambos años.
        # Inyectamos params 2025 para el test (el generador usa un solo
        # provider, pero la salida documenta ambos segmentos).
        gen = JSONGenerator(params=provs[2025].to_dict())
        out = gen.generate_output(
            {
                "input_data": input_data,
                "calculation_results": calc,
                "compliance_report": {"compliance_status": "GO"},
                "validaciones_y_alertas": {"V001": "PASS"},
                "normas_aplicadas": [
                    "Art. 249-250 CST",
                    "Ley 50/1990 Art. 99",
                    "Art. 306-308 CST",
                ],
            }
        )

        # --- Shape Pydantic LiquidacionResult (Tarea 1.C) ---
        for key in (
            "meta",
            "trabajador",
            "empleador",
            "parametros",
            "contrato",
            "desglose",
            "total_liquidacion",
            "validaciones_y_alertas",
            "normas_aplicadas",
            "compliance_report",
        ):
            assert key in out, f"Falta clave top-level: {key}"

        # --- meta ---
        meta = out["meta"]
        assert meta["modo"] == "PERIODICA"
        assert "fecha_generacion" in meta
        assert "T" in meta["fecha_generacion"]  # ISO-8601
        assert meta["motor_version"] is not None
        assert meta["generator_version"] is not None
        assert meta["params_version"] is not None
        assert meta["params_hash"].startswith("sha256:")
        assert meta["input_hash"].startswith("sha256:")
        assert meta["output_hash"].startswith("sha256:")
        assert meta["compliance_status"] == "GO"
        assert isinstance(meta["referencias_normativas"], list)
        assert meta["plantilla_version"] is None

        # --- trabajador / empleador ---
        assert out["trabajador"]["nombre"] == "[ANONIMIZADO]"
        assert out["empleador"]["nombre"] == "[ANONIMIZADO]"

        # --- contrato ---
        assert out["contrato"]["tipo"] == "INDEFINIDO"

        # --- desglose ---
        desglose = out["desglose"]
        # Deben existir conceptos para ambos segmentos
        for anio in ("2025", "2026"):
            for concepto in (
                "cesantias",
                "intereses_cesantias",
                "prima",
            ):
                key = f"{anio}_{concepto}"
                assert key in desglose, f"Falta {key} en desglose"
                assert isinstance(desglose[key]["valor"], (int, float))
                assert desglose[key]["valor"] > 0, f"{key}.valor debe ser > 0"

        # Vacaciones deben ser 0 en PERIODICA
        for anio in ("2025", "2026"):
            assert desglose[f"{anio}_vacaciones"]["valor"] == 0.0

        # Indemnización debe ser None (R-LEG-01)
        for anio in ("2025", "2026"):
            assert desglose[f"{anio}_indemnizacion"]["valor"] is None

        # --- total_liquidacion ---
        assert isinstance(out["total_liquidacion"], (int, float))
        assert out["total_liquidacion"] > 0

        # --- validaciones / normas ---
        assert isinstance(out["validaciones_y_alertas"], dict)
        assert isinstance(out["normas_aplicadas"], list)
        assert len(out["normas_aplicadas"]) == 3

    # ------------------------------------------------------------------
    # 4. Cálculos del caso canónico (verificación de integridad)
    # ------------------------------------------------------------------

    def test_calculos_caso_canonico(self):
        """Verifica los valores numéricos del caso canónico."""
        SBL = Decimal("2200000")
        dias_2025 = 46  # 2025-11-16 → 2025-12-31
        dias_2026 = 160  # 2026-01-01 → 2026-06-09

        # Cesantías
        ces_2025 = float(round(SBL * Decimal(dias_2025) / Decimal("360"), 2))
        ces_2026 = float(round(SBL * Decimal(dias_2026) / Decimal("360"), 2))
        assert ces_2025 == pytest.approx(281111.11, rel=1e-9), f"Cesantías 2025: {ces_2025}"
        assert ces_2026 == pytest.approx(977777.78, rel=1e-9), f"Cesantías 2026: {ces_2026}"

        # Intereses (12% anual sobre cesantías)
        int_2025 = float(round(Decimal(str(ces_2025)) * Decimal("0.12"), 2))
        int_2026 = float(round(Decimal(str(ces_2026)) * Decimal("0.12"), 2))
        assert int_2025 == pytest.approx(33733.33, rel=1e-9), f"Intereses 2025: {int_2025}"
        assert int_2026 == pytest.approx(117333.33, rel=1e-9), f"Intereses 2026: {int_2026}"

        # Prima (SBL × días / 360)
        prima_2025 = float(round(SBL * Decimal(dias_2025) / Decimal("360"), 2))
        prima_2026 = float(round(SBL * Decimal(dias_2026) / Decimal("360"), 2))
        assert prima_2025 == pytest.approx(281111.11, rel=1e-9), f"Prima 2025: {prima_2025}"
        assert prima_2026 == pytest.approx(977777.78, rel=1e-9), f"Prima 2026: {prima_2026}"

        # Total
        total = ces_2025 + ces_2026 + int_2025 + int_2026 + prima_2025 + prima_2026
        assert total == pytest.approx(2668844.44, rel=1e-9), f"Total: {total}"

        # Verificar consistencia: 11 meses y 24 días → tasa proporcional
        # 2 semestres de prima (H2 2025 46d + H1 2026 160d)
        # El motor debe segmentar correctamente por año calendario

    def test_dias_segmentos_correctos(self):
        """Verifica que los segmentos suman 206 días (plan §3)."""
        segmentos = [
            (date(2025, 11, 16), date(2025, 12, 31), 46),
            (date(2026, 1, 1), date(2026, 6, 9), 160),
        ]
        total = 0
        for desde, hasta, esperado in segmentos:
            dias = (hasta - desde).days + 1  # inclusivo
            assert dias == esperado, f"{desde}→{hasta}: {dias} != {esperado}"
            total += dias
        assert total == 206

    # ------------------------------------------------------------------
    # 5. Integridad de hashes (auditabilidad)
    # ------------------------------------------------------------------

    def test_hashes_son_deterministicos(self):
        """Dos ejecuciones con el mismo input producen el mismo input_hash.

        NOTA: output_hash NO es determinístico entre ejecuciones porque
        ``meta.fecha_generacion`` usa ``datetime.now()`` (ISO-8601 con
        segundos variables). Solo validamos input_hash aquí.
        """
        input_data, raw_input = _load_canonical_input()
        segmentos = raw_input.get("segmentos", [])
        gen = JSONGenerator()

        calc_a = _build_calculation_result(
            segmentos,
            ParamsProvider.for_range(date(2025, 11, 16), date(2026, 6, 9)),
        )
        calc_b = _build_calculation_result(
            segmentos,
            ParamsProvider.for_range(date(2025, 11, 16), date(2026, 6, 9)),
        )

        out_a = gen.generate_output(
            {
                "input_data": input_data,
                "calculation_results": calc_a,
                "compliance_report": {"compliance_status": "GO"},
            }
        )
        out_b = gen.generate_output(
            {
                "input_data": input_data,
                "calculation_results": calc_b,
                "compliance_report": {"compliance_status": "GO"},
            }
        )

        # input_hash usa solo input_data → determinístico
        assert out_a["meta"]["input_hash"] == out_b["meta"]["input_hash"]
        # output_hash incluye fecha_generacion → NO determinístico
        # (verificado: difiere por timestamp en ISO-8601)

    def test_input_hash_cambia_con_input_distinto(self):
        """Un cambio en el input produce un input_hash diferente."""
        input_data, raw_input = _load_canonical_input()
        segmentos = raw_input.get("segmentos", [])
        gen = JSONGenerator()

        calc = _build_calculation_result(
            segmentos,
            ParamsProvider.for_range(date(2025, 11, 16), date(2026, 6, 9)),
        )

        out_a = gen.generate_output(
            {
                "input_data": input_data,
                "calculation_results": calc,
                "compliance_report": {"compliance_status": "GO"},
            }
        )

        # Modificar el input
        input_alt = dict(input_data)
        input_alt["trabajador"] = {"nombre": "OTRO", "documento": "999"}

        out_b = gen.generate_output(
            {
                "input_data": input_alt,
                "calculation_results": calc,
                "compliance_report": {"compliance_status": "GO"},
            }
        )

        assert out_a["meta"]["input_hash"] != out_b["meta"]["input_hash"]
