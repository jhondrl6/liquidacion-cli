"""
Tests de compliance para vacaciones en finiquito (Tarea 2.Z — Fase 2).

Reglas V014 (V_VACACIONES_FINIQUITO, CRITICAL) y
V015 (V_VACACIONES_DECLARADAS_FINIQUITO, MEDIUM).

Patrón: 4 clases siguiendo convención S29/S30 (addendum recipe):
1. TestV014VacacionesFiniquito — regla CRITICAL: renglón obligatorio
2. TestV015VacacionesDeclaradas — regla MEDIUM: declaración recomendada
3. TestVacacionesComplianceIntegration — integración con ComplianceEngine
4. TestReparosAddendumVacacionesCerrados — enforcement de reparos
"""

import json
from pathlib import Path
from decimal import Decimal

import pytest

from liquidator.compliance.rule_evaluator import RuleEvaluator
from liquidator.compliance.compliance_engine import ComplianceEngine


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _build_input(
    *,
    modo="FINIQUITO",
    tipo="INDEFINIDO",
    motivo="renuncia_voluntaria",
    vacaciones=None,  # None = no declarado, dict = declarado
    fecha_ingreso="2025-11-16",
    fecha_corte="2026-06-09",
    fecha_terminacion="2026-06-09",
    salario=2200000,
):
    """Construye input canónico para tests de vacaciones compliance."""
    contrato = {
        "fecha_ingreso": fecha_ingreso,
        "fecha_corte": fecha_corte,
        "tipo": tipo,
    }
    if motivo:
        contrato["motivo_terminacion"] = motivo
    if fecha_terminacion:
        contrato["fecha_terminacion_real"] = fecha_terminacion

    d = {
        "modo": modo,
        "trabajador": {"nombre": "Test", "documento": "000"},
        "empleador": {"nombre": "Empresa", "documento": "000"},
        "contrato": contrato,
        "salario": {"SBL": salario},
    }
    if vacaciones is not None:
        d["vacaciones"] = vacaciones
    return d


def _build_desglose(
    *,
    con_vacaciones_compensadas=False,
    valor_vacaciones=0,
):
    """Construye desglose mínimo para compliance."""
    desglose = {
        "cesantias": {"valor": 282778, "dias_liquidados": 46},
        "SBL_GENERAL": 2200000,
    }
    if con_vacaciones_compensadas:
        desglose["vacaciones_compensadas_finiquito"] = {
            "concepto": "Vacaciones compensadas (finiquito)",
            "valor": valor_vacaciones,
            "dias": Decimal("7.5"),
            "formula": "SBL / 30 × días_pendientes",
            "evidencia_legal": "Art. 189-190 CST",
            "obligatorio_en_finiquito": True,
        }
    return desglose


_PARAMS = {"SMMLV": 1750905, "version": "2026"}


def _build_calc_result(desglose=None):
    """Resultado de cálculo mínimo para compliance."""
    return {
        "meta": {"modo": "FINIQUITO", "fecha_corte": "2026-06-09"},
        "desglose": desglose or _build_desglose(),
    }


def _eval_v014(input_data, result=None):
    func = RuleEvaluator.build("V014", {})
    return func(input_data, result or {}, _PARAMS)


def _eval_v015(input_data, result=None):
    func = RuleEvaluator.build("V015", {})
    return func(input_data, result or {}, _PARAMS)


# =========================================================================
# 1. TestV014VacacionesFiniquito
# =========================================================================

class TestV014VacacionesFiniquito:
    """V014: vacaciones obligatorias en finiquito — Art. 189-190 CST."""

    def test_finiquito_con_vacaciones_y_renglon_pasa(self):
        """PASS camino feliz: el motor calculó vacaciones, la CRITICAL pasa."""
        inp = _build_input(vacaciones={"dias_pendientes": 7.5})
        desglose = _build_desglose(
            con_vacaciones_compensadas=True, valor_vacaciones=550000
        )
        result = _build_calc_result(desglose)
        r = _eval_v014(inp, result)
        assert r["result"] == "PASS"
        assert "550,000" in r["evidence"]

    def test_finiquito_con_vacaciones_sin_renglon_bloquea(self):
        """FAIL camino de fallo: dias>0 pero sin renglón → CRITICAL."""
        inp = _build_input(vacaciones={"dias_pendientes": 7.5})
        desglose = _build_desglose(con_vacaciones_compensadas=False)
        result = _build_calc_result(desglose)
        r = _eval_v014(inp, result)
        assert r["result"] == "FAIL"
        assert "Art. 189" in r["evidence"]
        assert "7.5" in r["evidence"]

    def test_finiquito_con_vacaciones_renglon_cero_bloquea(self):
        """FAIL: renglón existe pero valor=0 → CRITICAL."""
        inp = _build_input(vacaciones={"dias_pendientes": 7})
        desglose = _build_desglose(
            con_vacaciones_compensadas=True, valor_vacaciones=0
        )
        result = _build_calc_result(desglose)
        r = _eval_v014(inp, result)
        assert r["result"] == "FAIL"

    def test_finiquito_vacaciones_cero_no_aplica(self):
        """PASS: dias_pendientes=0 → regla N/A (todas disfrutadas)."""
        inp = _build_input(vacaciones={"dias_pendientes": 0})
        desglose = _build_desglose(con_vacaciones_compensadas=False)
        result = _build_calc_result(desglose)
        r = _eval_v014(inp, result)
        assert r["result"] == "PASS"
        assert "no aplica" in r["evidence"].lower()

    def test_finiquito_sin_vacaciones_declaradas_no_aplica(self):
        """PASS: vacaciones=None → V015 advierte, V014 es N/A."""
        inp = _build_input(vacaciones=None)
        result = _build_calc_result()
        r = _eval_v014(inp, result)
        assert r["result"] == "PASS"
        assert "V015" in r["evidence"]  # redirige a V015

    def test_periodica_no_aplica(self):
        """PASS: modo PERIODICA → regla no aplica."""
        inp = _build_input(modo="PERIODICA", vacaciones={"dias_pendientes": 7})
        result = _build_calc_result()
        r = _eval_v014(inp, result)
        assert r["result"] == "PASS"
        assert "no aplica" in r["evidence"].lower()

    def test_finiquito_renuncia_con_renglon_pasa(self):
        """PASS: renuncia voluntaria + vacaciones pagadas → OK."""
        inp = _build_input(
            motivo="renuncia_voluntaria",
            vacaciones={"dias_pendientes": 7.5},
        )
        desglose = _build_desglose(
            con_vacaciones_compensadas=True, valor_vacaciones=550000
        )
        result = _build_calc_result(desglose)
        r = _eval_v014(inp, result)
        assert r["result"] == "PASS"

    def test_finiquito_despido_con_renglon_pasa(self):
        """PASS: despido sin justa causa + vacaciones pagadas → OK."""
        inp = _build_input(
            motivo="despido_sin_justa_causa",
            vacaciones={"dias_pendientes": 10},
        )
        desglose = _build_desglose(
            con_vacaciones_compensadas=True, valor_vacaciones=733333
        )
        result = _build_calc_result(desglose)
        r = _eval_v014(inp, result)
        assert r["result"] == "PASS"


# =========================================================================
# 2. TestV015VacacionesDeclaradas
# =========================================================================

class TestV015VacacionesDeclaradas:
    """V015: declaración de vacaciones en finiquito (MEDIUM, no bloqueante)."""

    def test_finiquito_sin_vacaciones_declaradas_emite_warning(self):
        """WARN: vacaciones=None → WARNING MEDIUM."""
        inp = _build_input(vacaciones=None)
        result = _build_calc_result()
        r = _eval_v015(inp, result)
        assert r["result"] == "WARN"
        assert "declaradas" in r["evidence"].lower()

    def test_finiquito_con_vacaciones_pasa(self):
        """PASS: vacaciones declaradas (dias=7.5) → OK."""
        inp = _build_input(vacaciones={"dias_pendientes": 7.5})
        result = _build_calc_result()
        r = _eval_v015(inp, result)
        assert r["result"] == "PASS"
        assert "7.5" in r["evidence"]

    def test_finiquito_vacaciones_cero_pasa(self):
        """PASS: vacaciones={dias_pendientes:0} → OK (declaración válida)."""
        inp = _build_input(vacaciones={"dias_pendientes": 0})
        result = _build_calc_result()
        r = _eval_v015(inp, result)
        assert r["result"] == "PASS"
        assert "0" in r["evidence"]

    def test_periodica_no_aplica(self):
        """PASS: modo PERIODICA → no aplica."""
        inp = _build_input(modo="PERIODICA", vacaciones=None)
        result = _build_calc_result()
        r = _eval_v015(inp, result)
        assert r["result"] == "PASS"
        assert "no aplica" in r["evidence"].lower()


# =========================================================================
# 3. TestVacacionesComplianceIntegration
# =========================================================================

class TestVacacionesComplianceIntegration:
    """Integración V014+V015 con ComplianceEngine real."""

    @pytest.fixture
    def checklist_path(self):
        return Path(__file__).resolve().parents[3] / "params" / "checklist.json"

    def test_engine_loads_v014_v015(self, checklist_path):
        """El ComplianceEngine carga V014 y V015 sin KeyError."""
        engine = ComplianceEngine(checklist_path)
        inp = _build_input(vacaciones={"dias_pendientes": 7.5})
        desglose = _build_desglose(
            con_vacaciones_compensadas=True, valor_vacaciones=550000
        )
        result = _build_calc_result(desglose)
        report = engine.run(inp, _PARAMS, calculation_result=result)
        check_ids = [c["id"] for c in report["checks"]]
        assert "V014" in check_ids
        assert "V015" in check_ids

    def test_finiquito_completo_go(self, checklist_path):
        """FINIQUITO + vacaciones declaradas + renglón → compliance OK."""
        engine = ComplianceEngine(checklist_path)
        inp = _build_input(vacaciones={"dias_pendientes": 7.5})
        desglose = _build_desglose(
            con_vacaciones_compensadas=True, valor_vacaciones=550000
        )
        result = _build_calc_result(desglose)
        report = engine.run(inp, _PARAMS, calculation_result=result)
        v14 = next(c for c in report["checks"] if c["id"] == "V014")
        v15 = next(c for c in report["checks"] if c["id"] == "V015")
        assert v14["result"] == "PASS"
        assert v15["result"] == "PASS"
        assert "V014" not in report.get("blocking_failures", [])

    def test_finiquito_sin_renglon_no_go(self, checklist_path):
        """FINIQUITO + dias>0 + sin renglón → NO_GO (V014 CRITICAL)."""
        engine = ComplianceEngine(checklist_path)
        inp = _build_input(vacaciones={"dias_pendientes": 7.5})
        desglose = _build_desglose(con_vacaciones_compensadas=False)
        result = _build_calc_result(desglose)
        report = engine.run(inp, _PARAMS, calculation_result=result)
        v14 = next(c for c in report["checks"] if c["id"] == "V014")
        assert v14["result"] == "FAIL"
        assert v14["blocking"] is True
        assert "V014" in report["blocking_failures"]
        assert report["compliance_status"] == "NO_GO"

    def test_finiquito_sin_declarar_warn_pero_go(self, checklist_path):
        """FINIQUITO + vacaciones=None → WARN pero NO_GO unaffected."""
        engine = ComplianceEngine(checklist_path)
        inp = _build_input(vacaciones=None)
        result = _build_calc_result()
        report = engine.run(inp, _PARAMS, calculation_result=result)
        v15 = next(c for c in report["checks"] if c["id"] == "V015")
        assert v15["result"] == "WARN"
        assert v15["blocking"] is False
        # V015 es MEDIUM non-blocking, NO afecta compliance_status por sí solo
        assert "V015" not in report.get("blocking_failures", [])

    def test_finiquito_vacaciones_cero_go(self, checklist_path):
        """FINIQUITO + dias=0 → ambas reglas N/A/PASS, compliance OK."""
        engine = ComplianceEngine(checklist_path)
        inp = _build_input(vacaciones={"dias_pendientes": 0})
        desglose = _build_desglose(con_vacaciones_compensadas=False)
        result = _build_calc_result(desglose)
        report = engine.run(inp, _PARAMS, calculation_result=result)
        v14 = next(c for c in report["checks"] if c["id"] == "V014")
        v15 = next(c for c in report["checks"] if c["id"] == "V015")
        assert v14["result"] == "PASS"
        assert v15["result"] == "PASS"

    def test_periodica_ambas_no_aplica(self, checklist_path):
        """PERIODICA → V014 y V015 no aplican."""
        engine = ComplianceEngine(checklist_path)
        inp = _build_input(modo="PERIODICA", vacaciones=None)
        result = _build_calc_result()
        report = engine.run(inp, _PARAMS, calculation_result=result)
        v14 = next(c for c in report["checks"] if c["id"] == "V014")
        v15 = next(c for c in report["checks"] if c["id"] == "V015")
        assert v14["result"] == "PASS"
        assert v15["result"] == "PASS"


# =========================================================================
# 4. TestReparosAddendumVacacionesCerrados
# =========================================================================

class TestReparosAddendumVacacionesCerrados:
    """Enforcement de reparos del addendum finiquito/vacaciones (2.Z)."""

    def test_art_189_cst_presente_en_v014(self):
        """Art. 189-190 CST está citado en la función V014."""
        mod_path = Path(__file__).resolve().parents[2] / "compliance" / "rule_evaluator.py"
        text = mod_path.read_text(encoding="utf-8")
        assert "Art. 189-190" in text

    def test_v014_es_blocking(self):
        """V014 está declarada como blocking=true en checklist.json."""
        checklist_path = Path(__file__).resolve().parents[3] / "params" / "checklist.json"
        checklist = json.loads(checklist_path.read_text(encoding="utf-8"))
        v014 = next(r for r in checklist["rules"] if r["id"] == "V014")
        assert v014["severity"] == "CRITICAL"
        assert v014["blocking"] is True

    def test_v015_no_es_blocking(self):
        """V015 está declarada como blocking=false en checklist.json."""
        checklist_path = Path(__file__).resolve().parents[3] / "params" / "checklist.json"
        checklist = json.loads(checklist_path.read_text(encoding="utf-8"))
        v015 = next(r for r in checklist["rules"] if r["id"] == "V015")
        assert v015["severity"] == "MEDIUM"
        assert v015["blocking"] is False

    def test_normas_json_cst_189_verificado(self):
        """normas.json tiene entrada CST_189_VACACIONES VERIFICADO."""
        normas_path = Path(__file__).resolve().parents[3] / "params" / "normas.json"
        normas = json.loads(normas_path.read_text(encoding="utf-8"))
        cst189 = next(
            (n for n in normas.get("normas", []) if n.get("id") == "CST_189_VACACIONES"),
            None,
        )
        assert cst189 is not None
        assert cst189.get("estado_verificacion") == "VERIFICADO"

    def test_key_desglose_consistente_con_engine(self):
        """La key del desglose que V014 busca coincide con la que engine.py inyecta."""
        engine_path = Path(__file__).resolve().parents[2] / "core" / "engine.py"
        evaluator_path = Path(__file__).resolve().parents[2] / "compliance" / "rule_evaluator.py"
        engine_text = engine_path.read_text(encoding="utf-8")
        eval_text = evaluator_path.read_text(encoding="utf-8")
        # Engine inyecta en: calc_results["desglose"]["vacaciones_compensadas_finiquito"]
        assert '"vacaciones_compensadas_finiquito"' in engine_text
        # V014 busca la misma key
        assert '"vacaciones_compensadas_finiquito"' in eval_text
