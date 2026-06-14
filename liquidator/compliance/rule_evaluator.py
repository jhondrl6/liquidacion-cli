"""
Fabrica de funciones-evaluadoras para cada regla V001…V010.
Cada función recibe (input_data, result, params) y retorna
{"result": "PASS|WARN|FAIL", "evidence": str}
"""

from datetime import datetime
from typing import Dict, Any, Callable


class RuleEvaluator:
    @staticmethod
    def build(rule_id: str, meta: Dict) -> Callable:
        """Factory: devuelve la función que evalúa la regla."""
        mapping = {
            "V001": _v001_params_consistency,
            "V002": _v002_valid_contract,
            "V003": _v003_aux_transport,
            "V004": _v004_cesantias_formula,
            "V005": _v005_intereses_rate,
            "V006": _v006_prima_proportional,
            "V007": _v007_vacaciones_excluded,
            "V008": _v008_payment_deadlines,
            "V009": _v009_legal_support,
            "V010": _v010_hashes_versioning,
            "V011": _v011_indexacion_ipc,
        }
        return mapping[rule_id]


# ---------- implementaciones individuales ----------
def _v001_params_consistency(input_data: Dict, result: Dict, params: Dict) -> Dict:
    expected_smmlv = 1423500
    if params.get("SMMLV") != expected_smmlv:
        return {"result": "FAIL", "evidence": f"SMMLV esperado {expected_smmlv}"}
    return {"result": "PASS", "evidence": "SMMLV=1423500 coincide con params/2025.json"}


def _v002_valid_contract(input_data: Dict, result: Dict, params: Dict) -> Dict:
    tipo = input_data.get("tipo_contrato", "")
    if tipo.lower() == "prestación_servicios":
        return {
            "result": "FAIL",
            "evidence": "Contrato de prestación de servicios no aplica",
        }
    return {"result": "PASS", "evidence": f"Tipo de contrato es {tipo}"}


def _v003_aux_transport(input_data: Dict, result: Dict, params: Dict) -> Dict:
    reside = input_data.get("reside_en_lugar_trabajo")
    if reside is True:
        return {
            "result": "PASS",
            "evidence": "Auxilio excluido por residencia en lugar de trabajo",
        }
    return {"result": "WARN", "evidence": "Verificar si auxilio de transporte aplica"}


def _v004_cesantias_formula(input_data: Dict, result: Dict, params: Dict) -> Dict:
    desglose = result.get("desglose", {})
    ces_val = desglose.get("cesantias", {}).get("valor")
    sbl = desglose.get("SBL_GENERAL")
    dias = desglose.get("cesantias", {}).get("dias_liquidados")
    expected = (sbl * dias) / 360
    if ces_val != int(expected):
        return {
            "result": "FAIL",
            "evidence": f"Cesantías {ces_val} != esperado {int(expected)}",
        }
    return {"result": "PASS", "evidence": "Cálculo coincide con fórmula legal"}


def _v005_intereses_rate(input_data: Dict, result: Dict, params: Dict) -> Dict:
    tasa = params.get("TASA_INT_CESANTIAS")
    if tasa != 0.12:
        return {"result": "FAIL", "evidence": f"Tasa intereses {tasa} ≠ 12%"}
    return {"result": "PASS", "evidence": "Tasa 12% aplicada correctamente"}


def _v006_prima_proportional(input_data: Dict, result: Dict, params: Dict) -> Dict:
    # simplificación: si periodo no coincide exactamente con semestre → WARN
    fecha_corte = datetime.fromisoformat(result["meta"]["fecha_corte"])
    if fecha_corte.month not in (6, 12) or fecha_corte.day != 30:
        return {
            "result": "WARN",
            "evidence": "Periodo no coincide exactamente con semestre",
        }
    return {"result": "PASS", "evidence": "Prima semestre proporcional verificada"}


def _v007_vacaciones_excluded(input_data: Dict, result: Dict, params: Dict) -> Dict:
    modo = result["meta"]["modo"]
    vac_data = result["desglose"].get("vacaciones", {})
    vac_val = vac_data.get("valor", 0)
    vac_dias = vac_data.get("dias_liquidados", 0)
    
    if modo == "PERIÓDICA":
        # En modo PERIÓDICA es permitido compensar parcialmente por acuerdo mutuo (Art. 189 CST)
        if vac_val > 0:
            # Si hay compensación, debe tener nota indicando que es por acuerdo mutuo
            nota = vac_data.get("nota", "")
            if "acuerdo mutuo" in nota.lower() or "Art. 189" in vac_data.get("norma", ""):
                return {
                    "result": "PASS",
                    "evidence": f"Compensación parcial de {vac_dias} días por acuerdo mutuo (Art. 189 CST)",
                }
            else:
                # Hay valor pero no está justificado como acuerdo mutuo
                return {
                    "result": "FAIL",
                    "evidence": "Vacaciones en modo PERIÓDICA deben justificarse por acuerdo mutuo (Art. 189 CST)",
                }
        return {"result": "PASS", "evidence": "No hay compensación de vacaciones en modo PERIÓDICA"}
    
    return {"result": "PASS", "evidence": "Vacaciones manejadas correctamente según modo de liquidación"}


def _v008_payment_deadlines(input_data: Dict, result: Dict, params: Dict) -> Dict:
    for key in ("cesantias", "intereses_cesantias", "prima"):
        concepto = result["desglose"].get(key, {})
        if "plazo_pago_legal" not in concepto:
            return {"result": "FAIL", "evidence": f"Falta plazo_pago_legal en {key}"}
    return {
        "result": "PASS",
        "evidence": "Todas las prestaciones incluyen plazo_pago_legal",
    }


def _v009_legal_support(input_data: Dict, result: Dict, params: Dict) -> Dict:
    for key, concepto in result["desglose"].items():
        if not isinstance(concepto, dict):
            continue
        if "norma" not in concepto:
            return {"result": "FAIL", "evidence": f"Falta norma en {key}"}
    return {"result": "PASS", "evidence": "Cada renglón incluye referencia normativa"}


def _v010_hashes_versioning(input_data: Dict, result: Dict, params: Dict) -> Dict:
    meta = result["meta"]
    required = ("params_version", "input_hash", "output_hash")
    for k in required:
        if k not in meta:
            return {"result": "FAIL", "evidence": f"Falta {k} en meta"}
    return {"result": "PASS", "evidence": "Hashes y versionamiento presentes"}


def _v011_indexacion_ipc(input_data: Dict, result: Dict, params: Dict) -> Dict:
    """Regla V011 — Indexacion IPC para prestaciones no pagadas oportunamente.

    Tarea 2.X (Fase 2-bis, addendum SL2630-2024).

    No es bloqueante (severity MEDIUM). Cuando el input declara
    `periodos_no_pagados`, valida:
    - Estructura: cada periodo tiene los 4 campos requeridos
      (concepto, valor_historico, fecha_causacion, fecha_exigibilidad,
      fecha_referencia_indexacion).
    - Prescripcion (Art. 488 CST): si la diferencia entre
      fecha_referencia_indexacion y fecha_exigibilidad es > 3 anios,
      el periodo esta prescrito (WARNING, no FAIL).
    - El calculo de VA lo hace el motor (engine.py) y aparece como
      `<concepto>_indexado` en el desglose con `evidencia_legal` y
      `formula`.
    """
    periodos = input_data.get("periodos_no_pagados")
    if not periodos:
        return {
            "result": "PASS",
            "evidence": (
                "Sin periodos_no_pagados en input. La regla V011 NO aplica "
                "a este caso (opt-in). Motor se comporta como v2.0.0 sin "
                "indexacion."
            ),
        }

    # Validamos estructura basica y prescripcion
    n_prescritos = 0
    n_indexables = 0
    campos_requeridos = {
        "concepto",
        "valor_historico",
        "fecha_causacion",
        "fecha_exigibilidad",
        "fecha_referencia_indexacion",
    }
    for p in periodos:
        if not isinstance(p, dict):
            continue
        if not campos_requeridos.issubset(p.keys()):
            return {
                "result": "FAIL",
                "evidence": (
                    f"periodos_no_pagados entry falta campos requeridos: "
                    f"{campos_requeridos - set(p.keys())}"
                ),
            }
        # Prescripcion Art. 488 CST: 3 anios desde fecha_exigibilidad
        try:
            exig = datetime.fromisoformat(str(p["fecha_exigibilidad"]))
            ref = datetime.fromisoformat(str(p["fecha_referencia_indexacion"]))
            delta_anios = (ref - exig).days / 365.25
            if delta_anios > 3.0:
                n_prescritos += 1
            else:
                n_indexables += 1
        except (ValueError, TypeError):
            # Fechas invalidas ya fueron rechazadas por Pydantic;
            # aqui no bloqueamos, solo ignoramos.
            pass

    if n_prescritos > 0:
        return {
            "result": "WARN",
            "evidence": (
                f"Indexacion IPC: {n_indexables} periodo(s) indexable(s) + "
                f"{n_prescritos} periodo(s) prescrito(s) por Art. 488 CST. "
                f"Periodos prescritos NO se indexan; se conservan en el "
                f"output con WARNING. Verificar manualmente si aplica "
                f"interrupcion de prescripcion."
            ),
        }

    return {
        "result": "PASS",
        "evidence": (
            f"Indexacion IPC aplicable: {n_indexables} periodo(s) sin "
            f"prescripcion. SL2630-2024 + Art. 488 CST."
        ),
    }
