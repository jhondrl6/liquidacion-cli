"""
Fabrica de funciones-evaluadoras para cada regla V001…V010.
Cada función recibe (input_data, result, params) y retorna
{"result": "PASS|WARN|FAIL", "evidence": str}
"""

from datetime import datetime
from decimal import Decimal
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
            "V012": _v012_preaviso_termino_fijo,
            "V013": _v013_preaviso_declarado,
            "V014": _v014_vacaciones_finiquito,
            "V015": _v015_vacaciones_declaradas,
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


def _v012_preaviso_termino_fijo(
    input_data: Dict, result: Dict, params: Dict
) -> Dict:
    """Regla V012 — Preaviso Art. 46 CST para contrato a término fijo vencido.

    Tarea 2.Y (Fase 2, addendum preaviso).

    No es bloqueante (severity MEDIUM). Cuando el input declara
    modo FINIQUITO + tipo FIJO + motivo termino_fijo_vencido, valida:
    - Que los datos de preaviso estén declarados (preaviso_entregado).
    - Que haya suficiente información para calcular la indemnización
      (dias_preaviso o fecha_preaviso + fecha_vencimiento_termino_fijo).
    - Si el preaviso fue >= 30 días: PASS (no hay indemnización).
    - Si el preaviso fue < 30 días: WARN (indemnización Art. 46 se
      calculará como renglón SEPARADO de Art. 64 — reparo b).
    """
    contrato = input_data.get("contrato", {})
    if not isinstance(contrato, dict) or not contrato:
        # Forma 1 plana: buscar campos en top-level
        contrato = input_data

    modo = str(input_data.get("modo", "")).upper()
    tipo = str(contrato.get("tipo", "") or input_data.get("tipo_contrato", "")).upper()
    motivo = str(
        contrato.get("motivo_terminacion", "")
        or input_data.get("motivo_terminacion", "")
    ).lower()

    # Solo aplica a FINIQUITO + FIJO + termino_fijo_vencido
    if modo != "FINIQUITO" or tipo != "FIJO" or motivo != "termino_fijo_vencido":
        return {
            "result": "PASS",
            "evidence": (
                "V_PREAVISO_TERMINO_FIJO no aplica: "
                f"modo={modo}, tipo={tipo}, motivo={motivo}. "
                "Solo aplica a FINIQUITO + FIJO + termino_fijo_vencido."
            ),
        }

    # Obtener días de preaviso efectivos
    dias_preaviso = contrato.get("dias_preaviso")
    if isinstance(dias_preaviso, (int, float)) and dias_preaviso >= 0:
        dias_efectivos = int(dias_preaviso)
    else:
        # Intentar calcular desde fechas
        fecha_preaviso_str = contrato.get("fecha_preaviso")
        fecha_vencimiento = contrato.get("fecha_vencimiento_termino_fijo")
        fecha_terminacion = contrato.get("fecha_terminacion_real")
        fecha_ref_str = (
            fecha_vencimiento
            or fecha_terminacion
            or input_data.get("fecha_corte")
        )

        if not fecha_preaviso_str or not fecha_ref_str:
            return {
                "result": "WARN",
                "evidence": (
                    "FINIQUITO + FIJO + termino_fijo_vencido sin datos "
                    "suficientes de preaviso: falta dias_preaviso o "
                    "(fecha_preaviso + fecha_vencimiento_termino_fijo). "
                    "No se puede validar compliance Art. 46 CST."
                ),
            }

        try:
            fecha_prev = datetime.fromisoformat(str(fecha_preaviso_str))
            fecha_ref = datetime.fromisoformat(str(fecha_ref_str))
            dias_efectivos = (fecha_ref - fecha_prev).days
            if dias_efectivos < 0:
                return {
                    "result": "WARN",
                    "evidence": (
                        f"fecha_preaviso ({fecha_preaviso_str}) es posterior "
                        f"a fecha de referencia ({fecha_ref_str}). "
                        f"Fechas invertidas; no se puede validar preaviso."
                    ),
                }
        except (ValueError, TypeError):
            return {
                "result": "WARN",
                "evidence": (
                    f"Error parseando fechas de preaviso: "
                    f"fecha_preaviso={fecha_preaviso_str}, "
                    f"fecha_ref={fecha_ref_str}."
                ),
            }

    # Evaluar suficiencia del preaviso
    if dias_efectivos >= 30:
        return {
            "result": "PASS",
            "evidence": (
                f"Preaviso suficiente: {dias_efectivos} días >= 30 "
                f"(Art. 46 CST). No hay indemnización por preaviso."
            ),
        }

    dias_faltantes = 30 - dias_efectivos
    return {
        "result": "WARN",
        "evidence": (
            f"Preaviso insuficiente: {dias_efectivos} de 30 días "
            f"requeridos (Art. 46 CST). Faltan {dias_faltantes} días. "
            f"Indemnización = (SBL/30) × {dias_faltantes}. "
            f"Renglón SEPARADO de indemnización Art. 64 (reparo b)."
        ),
    }


def _v013_preaviso_declarado(
    input_data: Dict, result: Dict, params: Dict
) -> Dict:
    """Regla V013 — Consistencia de declaración de preaviso.

    Tarea 2.Y (Fase 2, addendum preaviso).

    No es bloqueante (severity MEDIUM). Valida que:
    - Si tipo=FIJO y preaviso_entregado=True, fecha_preaviso debe existir.
    - Si tipo=FIJO y motivo=termino_fijo_vencido, preaviso_entregado
      debe estar declarado (defensa en profundidad contra drift del schema).
    - Si tipo NO es FIJO y hay campos de preaviso: WARN (campos
      sin base legal fuera de término fijo).

    Nota: el schema Pydantic (1.C-quater, model_validator
    _preaviso_consistencia) ya valida estas reglas a nivel de parse.
    Esta regla de compliance captura drift en datos que bypasean
    el schema (ej. input procesado por ruta legacy sin Pydantic).
    """
    contrato = input_data.get("contrato", {})
    if not isinstance(contrato, dict) or not contrato:
        contrato = input_data

    tipo = str(contrato.get("tipo", "") or input_data.get("tipo_contrato", "")).upper()
    motivo = str(
        contrato.get("motivo_terminacion", "")
        or input_data.get("motivo_terminacion", "")
    ).lower()
    preaviso_entregado = contrato.get(
        "preaviso_entregado", input_data.get("preaviso_entregado")
    )
    fecha_preaviso = contrato.get(
        "fecha_preaviso", input_data.get("fecha_preaviso")
    )
    modo = str(input_data.get("modo", "")).upper()

    # --- Tipo NO FIJO con campos de preaviso: WARN ---
    if tipo != "FIJO":
        has_preaviso_fields = any(
            contrato.get(f) is not None
            for f in ("preaviso_entregado", "fecha_preaviso", "dias_preaviso")
        ) or any(
            input_data.get(f) is not None
            for f in ("preaviso_entregado", "fecha_preaviso", "dias_preaviso")
        )
        if has_preaviso_fields:
            return {
                "result": "WARN",
                "evidence": (
                    f"Campos de preaviso declarados en contrato tipo "
                    f"{tipo}, pero Art. 46 CST solo aplica a FIJO. "
                    f"Campos ignorados por motor."
                ),
            }
        return {
            "result": "PASS",
            "evidence": (
                f"V_PREAVISO_DECLARADO no aplica: tipo={tipo}. "
                "Art. 46 CST solo aplica a término fijo."
            ),
        }

    # --- Tipo FIJO ---
    # Regla: FINIQUITO + FIJO + termino_fijo_vencido exige preaviso_entregado
    if motivo == "termino_fijo_vencido" and preaviso_entregado is None:
        return {
            "result": "FAIL",
            "evidence": (
                "FINIQUITO + FIJO + termino_fijo_vencido sin "
                "preaviso_entregado declarado. Art. 46 CST requiere "
                "declarar si hubo preaviso (True/False). "
                "Schema Pydantic debió rechazar esto; posible bypass."
            ),
        }

    # Regla: preaviso_entregado=True exige fecha_preaviso
    if preaviso_entregado is True and fecha_preaviso is None:
        return {
            "result": "FAIL",
            "evidence": (
                "preaviso_entregado=True pero fecha_preaviso no está "
                "presente. Sin fecha no se pueden calcular días de "
                "anticipación (Art. 46 CST). Schema Pydantic debió "
                "rechazar esto; posible bypass."
            ),
        }

    # Regla: preaviso_entregado=False → indemnización completa (30 días)
    if preaviso_entregado is False:
        return {
            "result": "WARN",
            "evidence": (
                "preaviso_entregado=False en contrato FIJO"
                + (
                    " + termino_fijo_vencido. "
                    "Indemnización Art. 46 CST será 30 días completos."
                    if motivo == "termino_fijo_vencido"
                    else ". "
                    "Si el motivo no es termino_fijo_vencido, preaviso "
                    "no genera indemnización."
                )
            ),
        }

    # PASS: declaración consistente
    return {
        "result": "PASS",
        "evidence": (
            f"Declaración de preaviso consistente: "
            f"preaviso_entregado={preaviso_entregado}, "
            f"fecha_preaviso={fecha_preaviso}. "
            f"Tipo FIJO, motivo={motivo}."
        ),
    }


def _v014_vacaciones_finiquito(
    input_data: Dict, result: Dict, params: Dict
) -> Dict:
    """Regla V014 — Vacaciones obligatorias en finiquito (Art. 189-190 CST).

    Tarea 2.Z (Fase 2, addendum finiquito/vacaciones).

    Bloqueante (severity CRITICAL). Cuando el input declara
    modo FINIQUITO y vacaciones.dias_pendientes > 0, valida:
    - Que el desglose contenga el renglón de vacaciones compensadas
      (key 'vacaciones_compensadas_finiquito').
    - Que el valor del renglón sea > 0.

    Excepción: si vacaciones.dias_pendientes == 0 (todas disfrutadas),
    la regla NO aplica.

    Si modo != FINIQUITO, la regla NO aplica.
    """
    modo = str(input_data.get("modo", "")).upper()
    if modo != "FINIQUITO":
        return {
            "result": "PASS",
            "evidence": (
                "V_VACACIONES_FINIQUITO no aplica: "
                f"modo={modo}. Solo aplica a FINIQUITO."
            ),
        }

    vacaciones = input_data.get("vacaciones")
    if not isinstance(vacaciones, dict):
        # vacaciones no declaradas → V015 lo advierte; aquí es N/A
        return {
            "result": "PASS",
            "evidence": (
                "V_VACACIONES_FINIQUITO no aplica: "
                "vacaciones no declaradas (N/A). "
                "Regla V015 (V_VACACIONES_DECLARADAS) emitirá WARNING."
            ),
        }

    dias_pendientes = vacaciones.get("dias_pendientes", 0)
    try:
        dias = Decimal(str(dias_pendientes))
    except (ValueError, TypeError):
        dias = Decimal(0)

    if dias <= 0:
        return {
            "result": "PASS",
            "evidence": (
                "V_VACACIONES_FINIQUITO no aplica: "
                f"dias_pendientes={dias} (todas disfrutadas o 0). "
                "Regla N/A."
            ),
        }

    # CRITICAL: dias_pendientes > 0 → debe existir renglón en desglose
    desglose = result.get("desglose", {})
    renglon_vac = desglose.get("vacaciones_compensadas_finiquito", {})
    valor_vac = renglon_vac.get("valor", 0) if isinstance(renglon_vac, dict) else 0

    try:
        valor_dec = Decimal(str(valor_vac))
    except (ValueError, TypeError):
        valor_dec = Decimal(0)

    if valor_dec <= 0:
        return {
            "result": "FAIL",
            "evidence": (
                f"FINIQUITO con vacaciones.dias_pendientes={dias} "
                f"pero renglón 'vacaciones_compensadas_finiquito' "
                f"ausente o con valor 0 en el desglose. "
                f"Art. 189-190 CST exige pago obligatorio "
                f"(SBL/30 × {dias} días)."
            ),
        }

    return {
        "result": "PASS",
        "evidence": (
            f"Vacaciones compensadas en finiquito: "
            f"{valor_dec:,} COP ({dias} días, Art. 189-190 CST)."
        ),
    }


def _v015_vacaciones_declaradas(
    input_data: Dict, result: Dict, params: Dict
) -> Dict:
    """Regla V015 — Declaración de vacaciones en finiquito.

    Tarea 2.Z (Fase 2, addendum finiquito/vacaciones).

    No es bloqueante (severity MEDIUM). Cuando el input declara
    modo FINIQUITO y vacaciones es None, emite WARNING recomendando
    declarar vacaciones explícitamente.

    Si vacaciones.dias_pendientes == 0 (declaración explícita de que
    todas se disfrutaron), NO se advierte.

    Si modo != FINIQUITO, la regla NO aplica.
    """
    modo = str(input_data.get("modo", "")).upper()
    if modo != "FINIQUITO":
        return {
            "result": "PASS",
            "evidence": (
                "V_VACACIONES_DECLARADAS no aplica: "
                f"modo={modo}. Solo aplica a FINIQUITO."
            ),
        }

    vacaciones = input_data.get("vacaciones")
    if vacaciones is not None:
        # vacaciones declaradas (incluso dias=0 es válida declaración)
        return {
            "result": "PASS",
            "evidence": (
                "Vacaciones declaradas en FINIQUITO: "
                f"dias_pendientes={vacaciones.get('dias_pendientes', 'N/A')}. "
                "Regla V015 OK."
            ),
        }

    # vacaciones es None → WARNING MEDIUM
    return {
        "result": "WARN",
        "evidence": (
            "FINIQUITO sin vacaciones declaradas. "
            "Si hubo vacaciones pendientes, declararlas en "
            "input.vacaciones.dias_pendientes. "
            "Si todas se disfrutaron, declarar "
            "vacaciones: {dias_pendientes: 0} explícitamente. "
            "Compliance no puede inventar el dato."
        ),
    }
