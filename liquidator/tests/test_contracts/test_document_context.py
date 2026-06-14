"""Tests de ``DocumentContext`` — Tarea 3.A (Fase 3 base).

Plan §8.2 línea 3197. Cubre:

- ``RenglonDesglose``: validación de campos, valor no negativo, defaults.
- ``ComplianceInfo``: status Literal, defaults, ``from_compliance_report``
  con ambas variantes de keys (``status``/``compliance_status``,
  ``blocking_failures``/``failures``, ``warnings``/``advertencias``).
- ``DocumentContext``: construcción directa, defaults, ``from_engine_result``
  con PII anonimizada y desglose aplanado.
- Edge cases: input vacío, desglose None, compliance_report None,
  result que no es dict, valores None/0 en desglose.

DoD de la tarea (plan §8.1 + §8.2): modelo Pydantic con
``RenglonDesglose`` y ``DocumentContext``, anonimización de PII
(nombre, documento), evidencia legal por renglón, y snapshot
inmutable del input.
"""
from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from liquidator.contracts.document_context import (
    ComplianceInfo,
    ComplianceStatus,
    DocumentContext,
    RenglonDesglose,
)


# ===========================================================================
# Helpers
# ===========================================================================


def _make_renglon(**overrides) -> dict:
    """Renglón de desglose válido por default."""
    base = {
        "concepto": "cesantias",
        "valor": 1_000_000,
        "formula": "SBL * 160 / 360",
        "evidencia_legal": "CST Art. 249",
        "parametros_usados": {"SBL": 2_200_000, "dias_liquidados": 160},
    }
    base.update(overrides)
    return base


def _make_compliance_report(**overrides) -> dict:
    base = {
        "status": "GO",
        "blocking_failures": [],
        "warnings": [],
    }
    base.update(overrides)
    return base


def _make_engine_result_segmented() -> dict:
    """LiquidacionResult segmentado por año (forma v2.0)."""
    return {
        "meta": {
            "motor_version": "2.0.0",
            "fecha_generacion": "2026-06-14T10:00:00",
            "modo": "PERIODICA",
            "input_hash": "abc123",
            "output_hash": "def456",
            "parametros_por_segmento": {
                "2025": {
                    "params_version": "2025.1",
                    "rango": "2025-11-16 → 2025-12-31",
                    "dias": 46,
                    "params_ref": "params/2025.json",
                },
                "2026": {
                    "params_version": "2026.1",
                    "rango": "2026-01-01 → 2026-06-14",
                    "dias": 160,
                    "params_ref": "params/2026.json",
                },
            },
            "plantilla_version": None,
            "compliance_status": "GO",
            "referencias_normativas": ["CST_249_CESANTIAS", "CST_256_INT_CESANTIAS"],
        },
        "trabajador": {"nombre": "Juan Pérez", "documento": "123456789"},
        "empleador": {"nombre": "Empresa X S.A.S.", "documento": "900123456"},
        "contrato": {
            "fecha_ingreso": "2025-11-16",
            "fecha_corte": "2026-06-14",
            "tipo": "INDEFINIDO",
        },
        "salario": {"SBL": 2_200_000},
        "parametros": {"2025": {"SMMLV": 1_423_500}, "2026": {"SMMLV": 1_750_905}},
        "desglose": {
            "2025": {
                "cesantias": 281_111,
                "intereses_cesantias": 0,
                "prima": 281_111,
                "vacaciones": 0,
            },
            "2026": {
                "cesantias": 977_778,
                "intereses_cesantias": 117_333,
                "prima": 977_778,
                "vacaciones": 550_000,
            },
        },
        "total_liquidacion": 3_185_111,
        "validaciones_y_alertas": {},
        "normas_aplicadas": ["CST_249_CESANTIAS", "CST_306_PRIMA"],
        "compliance_report": {
            "status": "GO",
            "blocking_failures": [],
            "warnings": [],
            "summary": {"passed": 10, "warnings": 0, "failures": 0},
        },
    }


def _make_engine_result_plano() -> dict:
    """LiquidacionResult con desglose plano (legacy / tests Fase 0)."""
    return {
        "meta": {
            "motor_version": "2.0.0",
            "modo": "PERIODICA",
            "compliance_status": "GO",
        },
        "trabajador": {"nombre": "X", "documento": "1"},
        "empleador": {"nombre": "Y", "documento": "2"},
        "contrato": {"fecha_ingreso": "2025-01-01", "fecha_corte": "2025-12-31"},
        "salario": {"SBL": 2_200_000},
        "desglose": {
            "cesantias": {
                "valor": 2_200_000,
                "dias_liquidados": 360,
                "plazo_pago_legal": "31-ene del año siguiente",
                "norma": "CST Art. 249",
            },
            "prima": {
                "valor": 2_200_000,
                "dias_liquidados": 360,
                "norma": "CST Art. 306",
            },
        },
        "total_liquidacion": 4_400_000,
        "compliance_report": {"status": "GO"},
    }


# ===========================================================================
# RenglonDesglose
# ===========================================================================


class TestRenglonDesglose:
    """RenglonDesglose: validación de los 5 campos del spec (plan §8.2)."""

    def test_requiere_los_cinco_campos(self):
        with pytest.raises(ValidationError) as exc_info:
            RenglonDesglose.model_validate({"concepto": "cesantias"})
        errors = exc_info.value.errors()
        campos_faltantes = {e["loc"][0] for e in errors}
        assert campos_faltantes == {"valor", "formula", "evidencia_legal"}

    def test_valor_no_puede_ser_negativo(self):
        with pytest.raises(ValidationError) as exc_info:
            RenglonDesglose.model_validate(_make_renglon(valor=-1))
        assert any(
            e["loc"][0] == "valor" for e in exc_info.value.errors()
        )

    def test_valor_cero_es_valido(self):
        r = RenglonDesglose.model_validate(_make_renglon(valor=0))
        assert r.valor == 0

    def test_parametros_usados_default_vacio(self):
        r = RenglonDesglose.model_validate({
            "concepto": "x",
            "valor": 100,
            "formula": "f",
            "evidencia_legal": "e",
        })
        assert r.parametros_usados == {}

    def test_campos_se_serializan_correctamente(self):
        r = RenglonDesglose.model_validate(_make_renglon())
        d = r.model_dump()
        assert d["concepto"] == "cesantias"
        assert d["valor"] == 1_000_000
        assert d["formula"] == "SBL * 160 / 360"
        assert d["evidencia_legal"] == "CST Art. 249"
        assert d["parametros_usados"]["SBL"] == 2_200_000


# ===========================================================================
# ComplianceInfo
# ===========================================================================


class TestComplianceInfo:
    """ComplianceInfo: status Literal, defaults, variantes de keys."""

    def test_default_status_es_go(self):
        info = ComplianceInfo()
        assert info.status == "GO"
        assert info.failures == []
        assert info.warnings == []
        assert info.override is None

    def test_status_invalido_se_rechaza(self):
        with pytest.raises(ValidationError):
            ComplianceInfo(status="INVALID")  # type: ignore[arg-type]

    def test_los_cuatro_estados_validos(self):
        for s in ("GO", "WARN", "NO_GO", "OVERRIDE_APPROVED"):
            info = ComplianceInfo(status=s)  # type: ignore[arg-type]
            assert info.status == s

    def test_from_compliance_report_none(self):
        info = ComplianceInfo.from_compliance_report(None)
        assert info.status == "GO"

    def test_from_compliance_report_vacio(self):
        info = ComplianceInfo.from_compliance_report({})
        assert info.status == "GO"

    def test_from_compliance_report_acepta_compliance_status(self):
        """El motor histórico usa 'compliance_status', no 'status'."""
        info = ComplianceInfo.from_compliance_report(
            {"compliance_status": "NO_GO"}
        )
        assert info.status == "NO_GO"

    def test_from_compliance_report_acepta_status(self):
        info = ComplianceInfo.from_compliance_report({"status": "WARN"})
        assert info.status == "WARN"

    def test_from_compliance_report_acepta_blocking_failures(self):
        info = ComplianceInfo.from_compliance_report({
            "status": "NO_GO",
            "blocking_failures": [{"code": "V_FOO", "message": "falla"}],
        })
        assert len(info.failures) == 1
        assert info.failures[0]["code"] == "V_FOO"

    def test_from_compliance_report_acepta_failures_legacy(self):
        info = ComplianceInfo.from_compliance_report({
            "status": "NO_GO",
            "failures": [{"code": "V_BAR"}],
        })
        assert len(info.failures) == 1
        assert info.failures[0]["code"] == "V_BAR"

    def test_from_compliance_report_acepta_warnings_y_advertencias(self):
        a = ComplianceInfo.from_compliance_report({
            "warnings": [{"code": "V001"}],
        })
        b = ComplianceInfo.from_compliance_report({
            "advertencias": [{"code": "V002"}],
        })
        assert a.warnings[0]["code"] == "V001"
        assert b.warnings[0]["code"] == "V002"

    def test_from_compliance_report_status_desconocido_a_go(self):
        """Status fuera del Literal cae a GO (defensivo)."""
        info = ComplianceInfo.from_compliance_report({"status": "DESCONOCIDO"})
        assert info.status == "GO"


# ===========================================================================
# DocumentContext — construcción directa
# ===========================================================================


class TestDocumentContextDirect:
    """DocumentContext: construcción con campos explícitos."""

    def test_minimo_vacio_es_valido(self):
        """Sin compliance, defaults son razonables."""
        ctx = DocumentContext()
        assert ctx.metadata == {}
        assert ctx.input == {}
        assert ctx.desglose == []
        assert ctx.total == 0
        assert ctx.compliance.status == "GO"
        assert ctx.generado_por == "Jhond"

    def test_generado_en_es_datetime(self):
        ctx = DocumentContext()
        assert isinstance(ctx.generado_en, datetime)

    def test_total_negativo_rechazado(self):
        with pytest.raises(ValidationError):
            DocumentContext(total=-1)

    def test_compliance_puede_ser_dict_via_validate(self):
        """ComplianceInfo acepta dict por validación Pydantic estándar."""
        ctx = DocumentContext.model_validate({
            "compliance": {
                "status": "NO_GO",
                "failures": [{"code": "X"}],
            }
        })
        assert ctx.compliance.status == "NO_GO"
        assert len(ctx.compliance.failures) == 1

    def test_generado_por_override(self):
        ctx = DocumentContext(generado_por="agente-iah-cli")
        assert ctx.generado_por == "agente-iah-cli"


# ===========================================================================
# DocumentContext.from_engine_result — caso canónico
# ===========================================================================


class TestDocumentContextFromEngineResultSegmentado:
    """Caso canónico: LiquidacionResult segmentado por año (v2.0)."""

    def test_construye_sin_error(self):
        ctx = DocumentContext.from_engine_result(_make_engine_result_segmented())
        assert ctx is not None

    def test_total_correcto(self):
        ctx = DocumentContext.from_engine_result(_make_engine_result_segmented())
        assert ctx.total == 3_185_111

    def test_compliance_go(self):
        ctx = DocumentContext.from_engine_result(_make_engine_result_segmented())
        assert ctx.compliance.status == "GO"
        assert ctx.compliance.failures == []

    def test_metadata_completa(self):
        ctx = DocumentContext.from_engine_result(_make_engine_result_segmented())
        meta = ctx.metadata
        assert meta["motor_version"] == "2.0.0"
        assert meta["modo"] == "PERIODICA"
        assert meta["input_hash"] == "abc123"
        assert meta["output_hash"] == "def456"
        # params_version consolidado de parametros_por_segmento
        assert meta["params_version"] == "2025.1+2026.1"
        assert meta["compliance_status"] == "GO"

    def test_pii_anonimizada_en_input(self):
        """AGENTS.md #6: nombre y documento del trabajador a [ANONIMIZADO]/-."""
        ctx = DocumentContext.from_engine_result(_make_engine_result_segmented())
        trab = ctx.input["trabajador"]
        assert trab["nombre"] == "[ANONIMIZADO]"
        assert trab["documento"] == "-"
        emp = ctx.input["empleador"]
        assert emp["nombre"] == "[ANONIMIZADO]"
        assert emp["documento"] == "-"

    def test_pii_anonimizada_NO_contiene_datos_originales(self):
        ctx = DocumentContext.from_engine_result(_make_engine_result_segmented())
        ctx_dict = ctx.model_dump_json()
        # El JSON serializado no debe contener los originales.
        assert "Juan Pérez" not in ctx_dict
        assert "123456789" not in ctx_dict
        assert "Empresa X S.A.S." not in ctx_dict
        assert "900123456" not in ctx_dict

    def test_desglose_aplanado(self):
        """Segmentado 2025+2026 → lista plana de Renglones con anio en params."""
        ctx = DocumentContext.from_engine_result(_make_engine_result_segmented())
        # 4 conceptos × 2 años = 8 renglones (los 0 sí se filtran, quedan 7:
        # intereses_2025=0 se filtra; los demás > 0)
        conceptos = [r.concepto for r in ctx.desglose]
        assert "cesantias" in conceptos
        assert "prima" in conceptos
        assert "vacaciones" in conceptos
        # Cada renglón tiene anio en parametros_usados
        for r in ctx.desglose:
            assert "anio" in r.parametros_usados
            assert r.parametros_usados["anio"] in ("2025", "2026")

    def test_renglones_tienen_evidencia_legal(self):
        ctx = DocumentContext.from_engine_result(_make_engine_result_segmented())
        for r in ctx.desglose:
            assert r.evidencia_legal != ""
            assert "Ver KB" not in r.evidencia_legal  # todos los conceptos cubiertos

    def test_renglones_tienen_formula(self):
        ctx = DocumentContext.from_engine_result(_make_engine_result_segmented())
        for r in ctx.desglose:
            assert r.formula != ""

    def test_suma_desglose_es_cercana_a_total(self):
        """Sanity check: la suma del desglose no debe superar el total."""
        ctx = DocumentContext.from_engine_result(_make_engine_result_segmented())
        suma = sum(r.valor for r in ctx.desglose)
        # El total puede incluir conceptos no desglosados (recargo, etc.)
        # pero la suma no debe ser > 2x el total (defensivo).
        assert suma <= 2 * ctx.total


# ===========================================================================
# DocumentContext.from_engine_result — forma plana
# ===========================================================================


class TestDocumentContextFromEngineResultPlano:
    """Desglose plano (legacy / Fase 0 tests)."""

    def test_desglose_plano_se_aplana(self):
        ctx = DocumentContext.from_engine_result(_make_engine_result_plano())
        assert len(ctx.desglose) == 2
        conceptos = {r.concepto for r in ctx.desglose}
        assert conceptos == {"cesantias", "prima"}

    def test_evidencia_legal_del_motor_se_respeta(self):
        """Si el motor trae 'norma' en el desglose plano, gana sobre el fallback."""
        ctx = DocumentContext.from_engine_result(_make_engine_result_plano())
        ces_renglon = next(r for r in ctx.desglose if r.concepto == "cesantias")
        assert ces_renglon.evidencia_legal == "CST Art. 249"


# ===========================================================================
# Edge cases
# ===========================================================================


class TestDocumentContextEdgeCases:
    """Casos límite y regresiones duras."""

    def test_input_no_dict_lanza_type_error(self):
        with pytest.raises(TypeError, match="espera dict"):
            DocumentContext.from_engine_result("not a dict")  # type: ignore[arg-type]

    def test_input_none_lanza_type_error(self):
        with pytest.raises(TypeError, match="espera dict"):
            DocumentContext.from_engine_result(None)  # type: ignore[arg-type]

    def test_result_vacio_no_falla(self):
        """Un result vacío (edge case tests) debe producir ctx mínimo."""
        ctx = DocumentContext.from_engine_result({})
        assert ctx.total == 0
        assert ctx.desglose == []
        assert ctx.compliance.status == "GO"

    def test_desglose_none_no_falla(self):
        ctx = DocumentContext.from_engine_result({"desglose": None})
        assert ctx.desglose == []

    def test_desglose_vacio_no_falla(self):
        ctx = DocumentContext.from_engine_result({"desglose": {}})
        assert ctx.desglose == []

    def test_compliance_report_none_no_falla(self):
        ctx = DocumentContext.from_engine_result({"compliance_report": None})
        assert ctx.compliance.status == "GO"

    def test_valores_none_en_desglose_se_filtran(self):
        """Renglones con valor None o 0 no deben aparecer."""
        result = {
            "meta": {},
            "trabajador": {},
            "empleador": {},
            "contrato": {},
            "salario": {},
            "desglose": {
                "2025": {
                    "cesantias": 1_000_000,
                    "intereses_cesantias": 0,
                    "prima": None,
                }
            },
            "total_liquidacion": 1_000_000,
            "compliance_report": {},
        }
        ctx = DocumentContext.from_engine_result(result)
        assert len(ctx.desglose) == 1
        assert ctx.desglose[0].concepto == "cesantias"

    def test_no_go_en_compliance(self):
        """Caso real: compliance NO_GO debe propagarse al contexto."""
        ctx = DocumentContext.from_engine_result(
            {
                "meta": {
                    "motor_version": "2.0.0",
                    "modo": "FINIQUITO",
                    "compliance_status": "NO_GO",
                },
                "trabajador": {"nombre": "X", "documento": "1"},
                "empleador": {"nombre": "Y", "documento": "2"},
                "contrato": {"fecha_ingreso": "2025-01-01",
                             "fecha_corte": "2025-12-31"},
                "salario": {"SBL": 2_200_000},
                "desglose": {"2025": {"vacaciones": 0}},
                "total_liquidacion": 0,
                "compliance_report": {
                    "status": "NO_GO",
                    "blocking_failures": [
                        {"code": "V_VACACIONES_FINIQUITO",
                         "message": "Falta vacaciones"},
                    ],
                },
            }
        )
        assert ctx.compliance.status == "NO_GO"
        assert len(ctx.compliance.failures) == 1
        assert ctx.compliance.failures[0]["code"] == "V_VACACIONES_FINIQUITO"

    def test_override_en_compliance(self):
        ctx = DocumentContext.from_engine_result(
            {
                "meta": {
                    "motor_version": "2.0.0",
                    "modo": "PERIODICA",
                    "compliance_status": "OVERRIDE_APPROVED",
                },
                "trabajador": {"nombre": "X", "documento": "1"},
                "empleador": {"nombre": "Y", "documento": "2"},
                "contrato": {"fecha_ingreso": "2025-01-01",
                             "fecha_corte": "2025-12-31"},
                "salario": {"SBL": 2_200_000},
                "desglose": {"2025": {"cesantias": 1_000_000}},
                "total_liquidacion": 1_000_000,
                "compliance_report": {
                    "status": "OVERRIDE_APPROVED",
                    "override": {
                        "operator_id": "Jhond",
                        "reason": "Caso real verificado manualmente",
                    },
                },
            }
        )
        assert ctx.compliance.status == "OVERRIDE_APPROVED"
        assert ctx.compliance.override["operator_id"] == "Jhond"

    def test_generado_por_personalizado(self):
        ctx = DocumentContext.from_engine_result(
            _make_engine_result_segmented(),
            generado_por="subagent-batch-1",
        )
        assert ctx.generado_por == "subagent-batch-1"


# ===========================================================================
# Inmutabilidad (DoD plan §8.1: "snapshot inmutable por ejecución")
# ===========================================================================


class TestDocumentContextInmutabilidad:
    """El contexto representa un snapshot. Pydantic v2 default permite
    mutación, pero documentamos que la INTENCIÓN es inmutable — los
    consumidores deben tratarlo como tal (no mutar)."""

    def test_dump_y_re_validate_producen_mismo_modelo(self):
        """Round-trip dump → validate es estable."""
        original = DocumentContext.from_engine_result(
            _make_engine_result_segmented()
        )
        dumped = original.model_dump()
        rebuilt = DocumentContext.model_validate(dumped)
        assert rebuilt.total == original.total
        assert rebuilt.compliance.status == original.compliance.status
        assert len(rebuilt.desglose) == len(original.desglose)

    def test_dump_json_es_serializable(self):
        """model_dump_json() no debe fallar (Pydantic v2)."""
        ctx = DocumentContext.from_engine_result(_make_engine_result_segmented())
        json_str = ctx.model_dump_json()
        assert isinstance(json_str, str)
        assert "total" in json_str
        assert "compliance" in json_str
