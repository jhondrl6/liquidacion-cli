"""
Tests de compliance para preaviso Art. 46 CST (Tarea 2.Y — Fase 2).

Reglas V012 (V_PREAVISO_TERMINO_FIJO) y V013 (V_PREAVISO_DECLARADO).

Patrón: 4 clases siguiendo convención S28 (addendum recipe):
1. TestV012PreavisoTerminoFijo — reglas de cálculo y suficiencia
2. TestV013PreavisoDeclarado — consistencia de declaración
3. TestPreavisoComplianceIntegration — integración con ComplianceEngine
4. TestReparosAddendumCerrados — enforcement de reparos del addendum
"""

import json
from pathlib import Path

import pytest

from liquidator.compliance.compliance_engine import ComplianceEngine
from liquidator.compliance.rule_evaluator import RuleEvaluator

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _build_input(
    *,
    modo="FINIQUITO",
    tipo="FIJO",
    motivo="termino_fijo_vencido",
    preaviso_entregado=True,
    fecha_preaviso="2026-05-01",
    dias_preaviso=None,
    fecha_vencimiento="2026-06-01",
    fecha_ingreso="2025-06-01",
    fecha_corte="2026-06-01",
    salario_mensual=2200000,
    nested=True,
):
    """Construye input canónico para tests de preaviso compliance."""
    if nested:
        contrato = {
            "fecha_ingreso": fecha_ingreso,
            "fecha_corte": fecha_corte,
            "tipo": tipo,
            "motivo_terminacion": motivo,
            "fecha_vencimiento_termino_fijo": fecha_vencimiento,
            "preaviso_entregado": preaviso_entregado,
            "fecha_preaviso": fecha_preaviso,
        }
        if dias_preaviso is not None:
            contrato["dias_preaviso"] = dias_preaviso
        return {
            "modo": modo,
            "trabajador": {"nombre": "Test", "documento": "000"},
            "empleador": {"nombre": "Empresa", "documento": "000"},
            "contrato": contrato,
            "salario": {"SBL": salario_mensual},
            "fecha_ingreso": fecha_ingreso,
            "fecha_corte": fecha_corte,
            "salario_mensual": salario_mensual,
        }
    else:
        # Forma 1 plana (legacy)
        d = {
            "modo": modo,
            "tipo_contrato": tipo,
            "motivo_terminacion": motivo,
            "fecha_ingreso": fecha_ingreso,
            "fecha_corte": fecha_corte,
            "salario_mensual": salario_mensual,
            "preaviso_entregado": preaviso_entregado,
        }
        if fecha_preaviso:
            d["fecha_preaviso"] = fecha_preaviso
        if fecha_vencimiento:
            d["fecha_vencimiento_termino_fijo"] = fecha_vencimiento
        if dias_preaviso is not None:
            d["dias_preaviso"] = dias_preaviso
        return d


_PARAMS = {"SMMLV": 1750905, "version": "2026"}

# Resultado de cálculo mínimo para que V004 no falle con None
_CALC_RESULT = {
    "meta": {"modo": "FINIQUITO", "fecha_corte": "2026-06-01"},
    "desglose": {
        "cesantias": {"valor": 0, "dias_liquidados": 0},
        "SBL_GENERAL": 0,
    },
}

def _eval_v012(input_data, result=None):
    func = RuleEvaluator.build("V012", {})
    return func(input_data, result or {}, _PARAMS)


def _eval_v013(input_data, result=None):
    func = RuleEvaluator.build("V013", {})
    return func(input_data, result or {}, _PARAMS)


# =========================================================================
# 1. TestV012PreavisoTerminoFijo
# =========================================================================

class TestV012PreavisoTerminoFijo:
    """V012: preaviso Art. 46 CST — suficiencia y datos de cálculo."""

    def test_preaviso_suficiente_30_dias(self):
        """PASS: preaviso exactamente 30 días → no hay indemnización."""
        inp = _build_input(dias_preaviso=30)
        r = _eval_v012(inp)
        assert r["result"] == "PASS"
        assert "suficiente" in r["evidence"].lower()

    def test_preaviso_suficiente_mas_de_30(self):
        """PASS: preaviso > 30 días → no hay indemnización."""
        inp = _build_input(dias_preaviso=45)
        r = _eval_v012(inp)
        assert r["result"] == "PASS"

    def test_preaviso_insuficiente_15_dias(self):
        """WARN: preaviso 15 días → faltan 15, indemnización Art. 46."""
        inp = _build_input(dias_preaviso=15)
        r = _eval_v012(inp)
        assert r["result"] == "WARN"
        assert "15" in r["evidence"]
        assert "Art. 46" in r["evidence"]
        assert "SEPARADO" in r["evidence"]  # reparo b

    def test_preaviso_cero_dias(self):
        """WARN: preaviso 0 días → faltan 30, indemnización completa."""
        inp = _build_input(dias_preaviso=0)
        r = _eval_v012(inp)
        assert r["result"] == "WARN"
        assert "30" in r["evidence"]

    def test_preaviso_calculado_desde_fechas(self):
        """WARN: sin dias_preaviso pero con fechas → calcula días."""
        inp = _build_input(
            preaviso_entregado=True,
            fecha_preaviso="2026-05-15",
            fecha_vencimiento="2026-06-01",
            dias_preaviso=None,
        )
        r = _eval_v012(inp)
        assert r["result"] == "WARN"
        assert "17" in r["evidence"]  # 17 días de anticipación

    def test_no_aplica_periodica(self):
        """PASS: modo PERIODICA → no aplica."""
        inp = _build_input(modo="PERIODICA")
        r = _eval_v012(inp)
        assert r["result"] == "PASS"
        assert "no aplica" in r["evidence"].lower()

    def test_no_aplica_indefinido(self):
        """PASS: tipo INDEFINIDO → no aplica."""
        inp = _build_input(tipo="INDEFINIDO", motivo="despido_sin_justa_causa")
        r = _eval_v012(inp)
        assert r["result"] == "PASS"
        assert "no aplica" in r["evidence"].lower()

    def test_no_aplica_otro_motivo(self):
        """PASS: FIJO pero motivo mutuo_acuerdo → no aplica."""
        inp = _build_input(motivo="mutuo_acuerdo")
        r = _eval_v012(inp)
        assert r["result"] == "PASS"
        assert "no aplica" in r["evidence"].lower()

    def test_sin_datos_preaviso_warn(self):
        """WARN: FINIQUITO+FIJO+vencido sin datos suficientes."""
        inp = _build_input(
            preaviso_entregado=None,
            fecha_preaviso=None,
            dias_preaviso=None,
            fecha_vencimiento=None,
        )
        # Necesitamos que pase la validación de preaviso_entregado=None
        # para llegar al check de V012. Usamos resultado directo.
        contrato = inp["contrato"]
        contrato["preaviso_entregado"] = False  # Declarado pero sin fechas
        contrato.pop("fecha_preaviso", None)
        contrato.pop("fecha_vencimiento_termino_fijo", None)
        r = _eval_v012(inp)
        assert r["result"] == "WARN"
        assert "sin datos" in r["evidence"].lower() or "faltan" in r["evidence"].lower()

    def test_forma_1_plana(self):
        """PASS/WARN: Forma 1 plana (sin nested contrato)."""
        inp = _build_input(nested=False, dias_preaviso=10)
        r = _eval_v012(inp)
        assert r["result"] == "WARN"
        assert "20" in r["evidence"]  # faltan 20 días

    def test_fechas_invertidas(self):
        """WARN: fecha_preaviso posterior a fecha_vencimiento."""
        inp = _build_input(
            fecha_preaviso="2026-07-01",
            fecha_vencimiento="2026-06-01",
            dias_preaviso=None,
        )
        r = _eval_v012(inp)
        assert r["result"] == "WARN"
        assert "invertid" in r["evidence"].lower() or "posterior" in r["evidence"].lower()


# =========================================================================
# 2. TestV013PreavisoDeclarado
# =========================================================================

class TestV013PreavisoDeclarado:
    """V013: consistencia de declaración de preaviso."""

    def test_declaracion_consistente_true_con_fecha(self):
        """PASS: preaviso_entregado=True con fecha_preaviso."""
        inp = _build_input(preaviso_entregado=True, fecha_preaviso="2026-05-01")
        r = _eval_v013(inp)
        assert r["result"] == "PASS"
        assert "consistente" in r["evidence"].lower()

    def test_declaracion_consistente_false(self):
        """WARN: preaviso_entregado=False en termino_fijo_vencido."""
        inp = _build_input(preaviso_entregado=False, fecha_preaviso=None)
        r = _eval_v013(inp)
        assert r["result"] == "WARN"
        assert "30 días" in r["evidence"] or "30 dias" in r["evidence"]

    def test_fail_true_sin_fecha(self):
        """FAIL: preaviso_entregado=True sin fecha_preaviso."""
        inp = _build_input(preaviso_entregado=True, fecha_preaviso=None)
        r = _eval_v013(inp)
        assert r["result"] == "FAIL"
        assert "fecha_preaviso" in r["evidence"]

    def test_fail_vencido_sin_declarar(self):
        """FAIL: FINIQUITO+FIJO+vencido sin preaviso_entregado."""
        inp = _build_input(preaviso_entregado=None, fecha_preaviso=None)
        r = _eval_v013(inp)
        assert r["result"] == "FAIL"
        assert "declarado" in r["evidence"].lower()

    def test_no_aplica_indefinido(self):
        """PASS: tipo INDEFINIDO → no aplica."""
        inp = _build_input(tipo="INDEFINIDO", motivo="despido_sin_justa_causa",
                           preaviso_entregado=None, fecha_preaviso=None)
        r = _eval_v013(inp)
        assert r["result"] == "PASS"
        assert "no aplica" in r["evidence"].lower()

    def test_warn_indefinido_con_campos_preaviso(self):
        """WARN: INDEFINIDO con campos de preaviso (drift)."""
        inp = _build_input(tipo="INDEFINIDO", motivo="despido_sin_justa_causa")
        inp["contrato"]["preaviso_entregado"] = True
        inp["contrato"]["fecha_preaviso"] = "2026-05-01"
        r = _eval_v013(inp)
        assert r["result"] == "WARN"
        assert "Art. 46" in r["evidence"]

    def test_fijo_sin_motivo_vencido_sin_preaviso_ok(self):
        """PASS: FIJO con motivo distinto y sin preaviso → OK."""
        inp = _build_input(motivo="mutuo_acuerdo", preaviso_entregado=None)
        r = _eval_v013(inp)
        assert r["result"] == "PASS"

    def test_false_en_motivo_no_vencido(self):
        """WARN: preaviso=False en FIJO pero motivo no vencido."""
        inp = _build_input(motivo="mutuo_acuerdo", preaviso_entregado=False)
        r = _eval_v013(inp)
        assert r["result"] == "WARN"
        assert "no genera indemnización" in r["evidence"] or "no genera indemnizacion" in r["evidence"]

    def test_forma_1_plana(self):
        """PASS: Forma 1 plana consistente."""
        inp = _build_input(nested=False, preaviso_entregado=True, fecha_preaviso="2026-05-01")
        r = _eval_v013(inp)
        assert r["result"] == "PASS"


# =========================================================================
# 3. TestPreavisoComplianceIntegration
# =========================================================================

class TestPreavisoComplianceIntegration:
    """Integración V012+V013 con ComplianceEngine real."""

    @pytest.fixture
    def checklist_path(self):
        return Path(__file__).resolve().parents[3] / "params" / "checklist.json"

    def test_engine_loads_v012_v013(self, checklist_path):
        """El ComplianceEngine carga V012 y V013 sin KeyError."""
        engine = ComplianceEngine(checklist_path)
        inp = _build_input()
        report = engine.run(inp, _PARAMS, calculation_result=_CALC_RESULT)
        check_ids = [c["id"] for c in report["checks"]]
        assert "V012" in check_ids
        assert "V013" in check_ids

    def test_finiquito_fijo_vencido_completo(self, checklist_path):
        """Caso completo FINIQUITO+FIJO+vencido → V012 WARN, V013 WARN."""
        engine = ComplianceEngine(checklist_path)
        inp = _build_input(preaviso_entregado=False, fecha_preaviso=None,
                           fecha_vencimiento=None)
        report = engine.run(inp, _PARAMS, calculation_result=_CALC_RESULT)
        v12 = next(c for c in report["checks"] if c["id"] == "V012")
        v13 = next(c for c in report["checks"] if c["id"] == "V013")
        # V012: preaviso=False → 0 días efectivos → insuficiente
        assert v12["result"] == "WARN"
        # V013: preaviso=False → WARN
        assert v13["result"] == "WARN"

    def test_periodica_sin_preaviso(self, checklist_path):
        """PERIODICA → V012 PASS, V013 PASS (no aplica)."""
        engine = ComplianceEngine(checklist_path)
        inp = _build_input(modo="PERIODICA", motivo="renuncia_voluntaria",
                           preaviso_entregado=None, fecha_preaviso=None)
        inp["contrato"].pop("fecha_vencimiento_termino_fijo", None)
        report = engine.run(inp, _PARAMS, calculation_result=_CALC_RESULT)
        v12 = next(c for c in report["checks"] if c["id"] == "V012")
        v13 = next(c for c in report["checks"] if c["id"] == "V013")
        assert v12["result"] == "PASS"
        assert v13["result"] == "PASS"

    def test_preaviso_suficiente_no_bloquea(self, checklist_path):
        """Preaviso suficiente (45 días) → compliance NO_GO unaffected."""
        engine = ComplianceEngine(checklist_path)
        inp = _build_input(dias_preaviso=45)
        report = engine.run(inp, _PARAMS, calculation_result=_CALC_RESULT)
        v12 = next(c for c in report["checks"] if c["id"] == "V012")
        assert v12["result"] == "PASS"
        # V012+V013 son MEDIUM non-blocking, NO afectan compliance_status
        assert "V012" not in report.get("blocking_failures", [])
        assert "V013" not in report.get("blocking_failures", [])


# =========================================================================
# 4. TestReparosAddendumCerrados
# =========================================================================

class TestReparosAddendumCerrados:
    """Enforcement de reparos del addendum preaviso (S30)."""

    def test_reparo_b_preaviso_separado_art64(self):
        """Reparo b: V012 menciona 'SEPARADO' de Art. 64."""
        mod_path = Path(__file__).resolve().parents[2] / "compliance" / "rule_evaluator.py"
        text = mod_path.read_text(encoding="utf-8")
        assert "SEPARADO" in text

    def test_art_46_cst_presente_en_v012(self):
        """Art. 46 CST está citado en la función V012."""
        mod_path = Path(__file__).resolve().parents[2] / "compliance" / "rule_evaluator.py"
        text = mod_path.read_text(encoding="utf-8")
        assert "Art. 46" in text

    def test_normas_json_cst_46_verificado(self):
        """normas.json tiene entrada CST_46_PREAVISO VERIFICADO."""
        normas_path = Path(__file__).resolve().parents[3] / "params" / "normas.json"
        normas = json.loads(normas_path.read_text(encoding="utf-8"))
        cst46 = next(
            (n for n in normas.get("normas", []) if n.get("id") == "CST_46_PREAVISO"),
            None,
        )
        assert cst46 is not None
        assert cst46.get("estado_verificacion") == "VERIFICADO"
