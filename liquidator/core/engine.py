"""Motor principal de orquestación de la liquidación.

Tarea 2.X (Fase 2-bis, S28): integración de ``IPCIndexador`` para
indexar prestaciones no pagadas oportunamente (SL2630-2024 + Art. 488 CST).
Activa SOLO cuando el input declara ``periodos_no_pagados``.

Tarea 2.B-cuater (Fase 2, S30): indemnización por preaviso insuficiente
Art. 46 CST. Activa SOLO en FINIQUITO + FIJO + termino_fijo_vencido.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from copy import deepcopy
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional

from liquidator.params.params_loader import ParamsLoader
from liquidator.output.json_generator import JSONGenerator
from liquidator.compliance.compliance_engine import ComplianceEngine
from liquidator.calculators.indexacion import IPCIndexador
from liquidator.calculators.prestaciones_calculator import PrestacionesCalculator
from liquidator.calculators.indemnizacion_calculator import IndemnizacionCalculator

from .input_parser import InputParser
from .workflow_orchestrator import WorkflowOrchestrator

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tarea 2.X — constantes para indexación IPC
# ---------------------------------------------------------------------------

# Plazo de prescripción general (Art. 488 CST): 3 años desde fecha_exigibilidad.
# Salvo prescripciones especiales que NO se manejan en v2.0.0.
_PRESCRIPCION_ANIOS = 3
_PRESCRIPCION_DIAS_TOLERANCIA = 5  # tolerancia 5 días para evitar falsos positivos


def _dias_entre(desde: date, hasta: date) -> int:
    return (hasta - desde).days


def _esta_prescrito(fecha_exigibilidad: date, fecha_referencia: date) -> bool:
    """True si el periodo esta prescrito bajo Art. 488 CST (3 anios).

    Tolerancia de 5 dias para evitar falsos positivos por un dia de
    desfase en fechas limite.
    """
    delta = _dias_entre(fecha_exigibilidad, fecha_referencia)
    return delta > _PRESCRIPCION_ANIOS * 365 + _PRESCRIPCION_DIAS_TOLERANCIA


def _safe_hash(data: Dict[str, Any]) -> str:
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
    import hashlib

    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@dataclass
class EngineConfig:
    params_year: int = 2025
    checklist_path: Optional[Path] = None


class LiquidacionEngine:
    """Motor que coordina parsing, cálculos, compliance y auditoría."""

    def __init__(self, config: Optional[EngineConfig] = None):
        config = config or EngineConfig()
        self.config = config
        self.params_loader = ParamsLoader()
        self.input_parser = InputParser()
        self.json_generator = JSONGenerator()
        self.compliance_engine = ComplianceEngine(config.checklist_path)

        self._audit_logger = None
        self._audit_trail = None
        self._hash_calculator = None
        self._load_audit_utilities()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Compatibilidad con CLI: alias de :meth:`process_input`."""

        return self.process_input(payload)

    def process_input(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta el flujo completo de liquidación."""

        params = self.params_loader.load_params(self.config.params_year)
        parsed_data = self.input_parser.parse(payload)

        session_id = str(uuid.uuid4())
        start_time = time.time()

        self._log_audit_start(session_id, parsed_data, params)

        workflow = WorkflowOrchestrator(params)
        workflow_result = workflow.execute(parsed_data)

        input_hash = _safe_hash(parsed_data)
        compliance_report = self._run_compliance(
            parsed_data, params, workflow_result.compliance_payload, input_hash
        )
        compliance_report = self._apply_compliance_policy(
            parsed_data, compliance_report
        )

        enforce = parsed_data.get("enforce_compliance", True)
        if compliance_report["compliance_status"] == "NO_GO" and enforce:
            self._log_audit_complete(
                session_id, compliance_report, start_time, blocked=True
            )
            compliance_report["input_hash"] = f"sha256:{input_hash}"
            return {
                "meta": {
                    "modo": parsed_data.get("modo"),
                    "params_version": params.get("version"),
                    "input_hash": f"sha256:{input_hash}",
                },
                "compliance_report": compliance_report,
            }

        calc_results = deepcopy(workflow_result.calculation_results)
        alerts = dict(workflow_result.validaciones_y_alertas)
        calc_results["validaciones_y_alertas"] = alerts
        calc_results["normas_aplicadas"] = workflow_result.normas_aplicadas

        # --- 2.X (Fase 2-bis): indexación IPC si hay periodos_no_pagados ---
        periodos_indexados = self._procesar_periodos_no_pagados(
            parsed_data, calc_results, alerts
        )
        if periodos_indexados:
            # Sumar los VA al total y exponer en calc_results para que
            # el JSONGenerator los incluya en desglose.
            calc_results["periodos_indexados"] = periodos_indexados

        # --- 2.B-ter (Fase 2): vacaciones compensadas en finiquito ---
        if parsed_data.get("modo") == "FINIQUITO":
            self._calcular_vacaciones_si_finiquito(
                parsed_data, params, calc_results, alerts
            )

        # --- 2.B-cuater (Fase 2, S30): indemnizacion preaviso Art. 46 ---
        if parsed_data.get("modo") == "FINIQUITO":
            self._calcular_preaviso_si_fijo_vencido(
                parsed_data, params, calc_results, alerts
            )

        # 1.D — delegamos al JSONGenerator con el dict unificado y los
        # params que el engine ya cargó (ParamsLoader -> dict). El
        # generador no necesita hardcodear valores ni re-leer disco.
        self.json_generator.params = params
        output = self.json_generator.generate_output(
            {
                "input_data": parsed_data,
                "calculation_results": calc_results,
                "compliance_report": compliance_report,
                "validaciones_y_alertas": alerts,
                "normas_aplicadas": workflow_result.normas_aplicadas,
            }
        )

        # Actualizar hashes de compliance
        output_hash = output["meta"]["output_hash"]
        compliance_report["input_hash"] = output["meta"]["input_hash"]
        compliance_report["output_hash"] = output_hash
        compliance_report["params_version"] = params.get("version")

        self._log_audit_complete(session_id, compliance_report, start_time)
        self._persist_trail(session_id, parsed_data, output, compliance_report)

        return output

    def compliance_check(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        params = self.params_loader.load_params(self.config.params_year)
        parsed_data = self.input_parser.parse(payload)
        workflow = WorkflowOrchestrator(params)
        workflow_result = workflow.execute(parsed_data)
        input_hash = _safe_hash(parsed_data)
        return self._run_compliance(
            parsed_data, params, workflow_result.compliance_payload, input_hash
        )

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------
    def _run_compliance(
        self,
        input_data: Dict[str, Any],
        params: Dict[str, Any],
        compliance_payload: Dict[str, Any],
        input_hash: str,
    ) -> Dict[str, Any]:
        return self.compliance_engine.run(
            input_data,
            params,
            calculation_result=compliance_payload,
            input_hash=f"sha256:{input_hash}",
        )

    def _apply_compliance_policy(
        self, input_data: Dict[str, Any], report: Dict[str, Any]
    ) -> Dict[str, Any]:
        policy = str(input_data.get("compliance_policy", "standard")).lower()
        if policy == "strict" and report["summary"].get("warnings", 0) > 0:
            report["compliance_status"] = "NO_GO"
            if "WARNINGS_POLICY" not in report["blocking_failures"]:
                report["blocking_failures"].append("WARNINGS_POLICY")
        return report

    def _load_audit_utilities(self) -> None:
        try:
            from liquidator.audit import AuditLogger, AuditEventType, TrailGenerator

            self._audit_logger = AuditLogger()
            self._audit_event_type = AuditEventType
            self._audit_trail = TrailGenerator()
        except Exception:  # pragma: no cover - auditoría opcional
            self._audit_logger = None
            self._audit_trail = None
            self._audit_event_type = None

    def _log_audit_start(
        self, session_id: str, input_data: Dict[str, Any], params: Dict[str, Any]
    ) -> None:
        if not self._audit_logger:
            return
        self._audit_logger.log_calculation_start(
            session_id=session_id,
            input_data=input_data,
            params_version=params.get("version", "unknown"),
        )

    def _log_audit_complete(
        self,
        session_id: str,
        compliance_report: Dict[str, Any],
        start_time: float,
        *,
        blocked: bool = False,
    ) -> None:
        if not self._audit_logger:
            return
        duration = max(time.time() - start_time, 0.0)
        self._audit_logger.log_calculation_complete(
            session_id=session_id,
            output_hash=compliance_report.get("output_hash", ""),
            compliance_status=(
                "NO_GO"
                if blocked
                else compliance_report.get("compliance_status", "UNKNOWN")
            ),
            duration_seconds=duration,
        )

    def _persist_trail(
        self,
        session_id: str,
        input_data: Dict[str, Any],
        output: Dict[str, Any],
        compliance_report: Dict[str, Any],
    ) -> None:
        if not self._audit_trail:
            return
        try:
            if hasattr(self._audit_trail, "generate_audit_trail"):
                audit_trail = self._audit_trail.generate_audit_trail(
                    session_id=session_id,
                    input_data=input_data,
                    output_data=output,
                    compliance_report=compliance_report,
                    execution_logs=[],
                    override_records=[],
                    params_version=output["meta"].get("params_version", "unknown"),
                    generator_version=output["meta"].get("generator_version", "1.0.0"),
                )
                if hasattr(self._audit_trail, "save_audit_trail"):
                    self._audit_trail.save_audit_trail(audit_trail)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # 2.X (Fase 2-bis) — Indexación IPC para periodos_no_pagados
    # ------------------------------------------------------------------
    def _procesar_periodos_no_pagados(
        self,
        parsed_data: Dict[str, Any],
        calc_results: Dict[str, Any],
        alerts: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        """Si el input declara ``periodos_no_pagados``, calcula VA indexada
        para cada uno, validando prescripción (Art. 488 CST).

        Returns
        -------
        list[dict]
            Lista de renglones `<concepto>_indexado` listos para agregarse
            al desglose y al total. Lista vacía si el input no tiene
            `periodos_no_pagados` o si todos están prescritos.

        Side effects
        ------------
        - Suma los VA al ``calc_results["total"]`` (para que el
          JSONGenerator los incluya en ``total_liquidacion``).
        - Modifica ``alerts`` in-place con WARNINGs sobre prescripción.
        - Inyecta los renglones en ``calc_results["desglose"]`` con la
          forma que el JSONGenerator espera.
        """
        periodos = parsed_data.get("periodos_no_pagados")
        if not periodos:
            return []

        # Cargar IPCIndexador desde la fuente canonica
        repo_root = Path(__file__).resolve().parents[2]
        ipc_path = repo_root / "params" / "ipc_dane_mensual.json"
        if not ipc_path.exists():
            alerts["ipc_fuente_faltante"] = (
                f"No se encontro {ipc_path}. Indexacion IPC NO aplicada. "
                f"Ejecutar scripts/build_ipc_index.py para regenerar."
            )
            return []
        try:
            indexador = IPCIndexador.from_json(ipc_path, base_year=2010)
        except (ValueError, KeyError, FileNotFoundError) as exc:
            alerts["ipc_fuente_invalida"] = (
                f"Fuente IPC invalida: {exc}. Indexacion NO aplicada."
            )
            return []

        # Asegurar que calc_results tiene desglose y total
        if "desglose" not in calc_results:
            calc_results["desglose"] = {}
        total_actual = Decimal(str(calc_results.get("total", 0)))

        renglones: List[Dict[str, Any]] = []
        n_prescritos = 0
        n_indexados = 0

        for idx, p in enumerate(periodos, start=1):
            if not isinstance(p, dict):
                continue

            try:
                fecha_exig = date.fromisoformat(str(p["fecha_exigibilidad"]))
                fecha_ref = date.fromisoformat(
                    str(p["fecha_referencia_indexacion"])
                )
                fecha_caus = date.fromisoformat(str(p["fecha_causacion"]))
                valor_hist = Decimal(str(p["valor_historico"]))
                concepto = str(p["concepto"])
            except (ValueError, TypeError, KeyError) as exc:
                alerts[f"periodo_{idx}_invalido"] = (
                    f"periodos_no_pagados[{idx}] invalido: {exc}. Ignorado."
                )
                continue

            # Validar prescripcion Art. 488 CST
            if _esta_prescrito(fecha_exig, fecha_ref):
                n_prescritos += 1
                clave = f"{concepto}_indexado_prescrito"
                calc_results["desglose"][clave] = {
                    "valor": 0,
                    "concepto_original": concepto,
                    "valor_historico": int(valor_hist),
                    "fecha_causacion": fecha_caus.isoformat(),
                    "fecha_exigibilidad": fecha_exig.isoformat(),
                    "fecha_referencia_indexacion": fecha_ref.isoformat(),
                    "estado": "PRESCRITO",
                    "evidencia_legal": "SL2630-2024; Art. 488 CST",
                    "norma": "Art. 488 CST (prescripción 3 años)",
                    "nota": (
                        f"Periodo prescrito bajo Art. 488 CST "
                        f"({(fecha_ref - fecha_exig).days} dias > "
                        f"{_PRESCRIPCION_ANIOS * 365} dias). "
                        f"Verificar manualmente si aplica interrupcion "
                        f"de prescripcion."
                    ),
                }
                alerts[f"periodo_{concepto}_prescrito"] = (
                    f"{concepto} de {fecha_exig} esta prescrito "
                    f"(Art. 488 CST). No se indexa."
                )
                continue

            # Calcular VA con IPCIndexador
            try:
                va = indexador.indexar(valor_hist, fecha_caus, fecha_ref)
            except KeyError as exc:
                alerts[f"periodo_{concepto}_sin_ipc"] = (
                    f"{concepto} de {fecha_caus}: IPC no disponible "
                    f"({exc}). Verificar params/ipc_dane_mensual.json."
                )
                continue
            except Exception as exc:  # pragma: no cover (defensa)
                alerts[f"periodo_{concepto}_error"] = (
                    f"{concepto} de {fecha_caus}: error indexando: {exc}"
                )
                continue

            n_indexados += 1
            renglon = {
                "valor": int(va),
                "valor_historico": int(valor_hist),
                "concepto_original": concepto,
                "fecha_causacion": fecha_caus.isoformat(),
                "fecha_exigibilidad": fecha_exig.isoformat(),
                "fecha_referencia_indexacion": fecha_ref.isoformat(),
                "evidencia_legal": "SL2630-2024; Art. 488 CST",
                "formula": (
                    "VA = VH * (IPC_referencia / IPC_origen)"
                ),
                "norma": "SL2630-2024; Art. 488 CST",
                "nota": (
                    f"Indexado a {fecha_ref} con IPC DANE "
                    f"({fecha_caus} -> {fecha_ref})"
                ),
            }
            clave = f"{concepto}_indexado"
            calc_results["desglose"][clave] = renglon
            renglones.append(renglon)
            total_actual += Decimal(str(va))

        # Actualizar total y exponer resumen
        calc_results["total"] = int(total_actual)
        calc_results["total_liquidacion"] = int(total_actual)
        calc_results["indexacion_resumen"] = {
            "n_periodos_total": len(periodos) if isinstance(periodos, list) else 0,
            "n_indexados": n_indexados,
            "n_prescritos": n_prescritos,
            "fuente": "params/ipc_dane_mensual.json (DANE IPC)",
        }
        if n_indexados > 0 or n_prescritos > 0:
            alerts["indexacion_ipc_resumen"] = (
                f"IPC: {n_indexados} indexado(s), {n_prescritos} "
                f"prescrito(s) por Art. 488 CST"
            )
        return renglones

    # ------------------------------------------------------------------
    # 2.B-ter (Fase 2) — Vacaciones compensadas en finiquito
    # ------------------------------------------------------------------
    def _calcular_vacaciones_si_finiquito(
        self,
        parsed_data: Dict[str, Any],
        params: Dict[str, Any],
        calc_results: Dict[str, Any],
        alerts: Dict[str, str],
    ) -> None:
        """Hook de vacaciones compensadas en finiquito (Tarea 2.B-ter).

        Idempotente: si no aplica (modo PERIODICA, sin vacaciones,
        dias=0), no aade nada al desglose. Si aplica, aade un unico
        renglon de vacaciones compensadas con formula Art. 189-190 CST.
        """
        # OPT-IN: solo FINIQUITO con vacaciones pendientes
        vacaciones = parsed_data.get("vacaciones")
        if not isinstance(vacaciones, dict):
            return  # regla V_VACACIONES_DECLARADAS_FINIQUITO lo advertira (2.Z)
        dias_pendientes = vacaciones.get("dias_pendientes", 0)
        if not isinstance(dias_pendientes, (int, float, Decimal)):
            return
        dias_dec = Decimal(str(dias_pendientes))
        if dias_dec <= 0:
            logger.info("Finiquito sin vacaciones pendientes; nada que pagar")
            return

        # Obtener SBL desde el input (Forma 2 anidada o Forma 1 plana)
        salario_obj = parsed_data.get("salario", {})
        if isinstance(salario_obj, dict) and "SBL" in salario_obj:
            sbl = Decimal(str(salario_obj["SBL"]))
        else:
            sbl = Decimal(str(parsed_data.get("salario_mensual", 0)))
        if sbl <= 0:
            alerts["vacaciones_finiquito_sbl_invalido"] = (
                f"SBL invalido ({sbl}). No se pueden calcular vacaciones compensadas."
            )
            return

        prest_calc = PrestacionesCalculator(params)
        renglon = prest_calc.calculate_vacaciones_compensadas_finiquito(
            sbl=sbl, dias_pendientes=dias_dec
        )

        # Inyectar en desglose
        if "desglose" not in calc_results:
            calc_results["desglose"] = {}
        calc_results["desglose"]["vacaciones_compensadas_finiquito"] = renglon

        # Actualizar total
        valor_comp = renglon["valor"]
        total_actual = Decimal(str(calc_results.get("total", 0)))
        total_actual += Decimal(str(valor_comp))
        calc_results["total"] = int(total_actual)
        calc_results["total_liquidacion"] = int(total_actual)

        alerts["vacaciones_compensadas_finiquito"] = (
            f"Vacaciones compensadas en finiquito: {valor_comp:,} COP "
            f"({dias_pendientes} dias, SBL={int(sbl):,}) — Art. 189-190 CST"
        )

    # ------------------------------------------------------------------
    # 2.B-cuater (Fase 2, S30) — Indemnización preaviso Art. 46 CST
    # ------------------------------------------------------------------
    def _calcular_preaviso_si_fijo_vencido(
        self,
        parsed_data: Dict[str, Any],
        params: Dict[str, Any],
        calc_results: Dict[str, Any],
        alerts: Dict[str, str],
    ) -> None:
        """Hook de indemnización por preaviso insuficiente (Tarea 2.B-cuater).

        Solo aplica cuando:
        - modo == FINIQUITO
        - contrato.tipo == FIJO
        - motivo_terminacion == termino_fijo_vencido

        Fórmula: (SBL / 30) × dias_faltantes
        donde dias_faltantes = max(0, 30 - dias_preaviso_efectivos).

        Reparo (b): la indemnización por preaviso es un renglón SEPARADO
        de la indemnización por despido sin justa causa (Art. 64).
        NO se acumulan.
        """
        contrato = parsed_data.get("contrato", {})
        if not isinstance(contrato, dict):
            return

        tipo = str(contrato.get("tipo", "")).upper()
        motivo = str(contrato.get("motivo_terminacion", "")).lower()

        if tipo != "FIJO":
            return
        if motivo != "termino_fijo_vencido":
            return

        # Calcular dias_preaviso_efectivos
        dias_preaviso = contrato.get("dias_preaviso")
        if isinstance(dias_preaviso, (int, float)) and dias_preaviso >= 0:
            dias_efectivos = int(dias_preaviso)
        else:
            # Calcular desde fechas
            fecha_preaviso_str = contrato.get("fecha_preaviso")
            fecha_vencimiento = contrato.get("fecha_vencimiento_termino_fijo")
            fecha_terminacion = contrato.get("fecha_terminacion_real")

            fecha_ref_str = fecha_vencimiento or fecha_terminacion
            if not fecha_preaviso_str or not fecha_ref_str:
                alerts["preaviso_sin_fechas"] = (
                    "No se puede calcular indemnizacion por preaviso: "
                    "faltan fecha_preaviso y/o fecha_vencimiento_termino_fijo "
                    "(o fecha_terminacion_real)."
                )
                return

            try:
                fecha_prev = date.fromisoformat(str(fecha_preaviso_str))
                fecha_ref = date.fromisoformat(str(fecha_ref_str))
                dias_efectivos = (fecha_ref - fecha_prev).days
                if dias_efectivos < 0:
                    alerts["preaviso_fechas_invertidas"] = (
                        f"fecha_preaviso ({fecha_preaviso_str}) es posterior "
                        f"a fecha de referencia ({fecha_ref_str}). "
                        f"No se calcula indemnizacion."
                    )
                    return
            except (ValueError, TypeError) as exc:
                alerts["preaviso_error_fechas"] = (
                    f"Error calculando dias de preaviso: {exc}"
                )
                return

        # Obtener SBL
        salario_obj = parsed_data.get("salario", {})
        if isinstance(salario_obj, dict) and "SBL" in salario_obj:
            sbl = float(Decimal(str(salario_obj["SBL"])))
        else:
            sbl = float(Decimal(str(parsed_data.get("salario_mensual", 0))))
        if sbl <= 0:
            alerts["preaviso_sbl_invalido"] = (
                f"SBL invalido ({sbl}). No se puede calcular indemnizacion "
                f"por preaviso."
            )
            return

        # Calcular con IndemnizacionCalculator
        indemn_calc = IndemnizacionCalculator(params)
        renglon = indemn_calc.calculate_indemnizacion_preaviso(
            sbl=sbl,
            dias_preaviso_efectivos=dias_efectivos,
        )

        if not renglon.get("aplica"):
            alerts["preaviso_suficiente"] = (
                f"Preaviso fue suficiente ({dias_efectivos} >= 30 dias). "
                f"No hay indemnizacion por preaviso."
            )
            return

        # Inyectar en desglose como renglón SEPARADO
        if "desglose" not in calc_results:
            calc_results["desglose"] = {}
        calc_results["desglose"]["preaviso_indemnizacion"] = renglon

        # Actualizar total (SEPARADO de indemnizacion Art. 64)
        valor = renglon["valor"]
        total_actual = Decimal(str(calc_results.get("total", 0)))
        total_actual += Decimal(str(valor))
        calc_results["total"] = int(total_actual)
        calc_results["total_liquidacion"] = int(total_actual)

        logger.info(
            "Indemnizacion preaviso Art. 46 CST: %s COP "
            "(%d dias faltantes, SBL=%s)",
            f"{valor:,}",
            renglon["dias_faltantes"],
            f"{int(sbl):,}",
        )

        alerts["indemnizacion_preaviso"] = (
            f"Indemnizacion preaviso Art. 46 CST: {valor:,} COP "
            f"({renglon['dias_faltantes']} dias faltantes, "
            f"SBL={int(sbl):,}) — renglon separado de Art. 64."
        )
