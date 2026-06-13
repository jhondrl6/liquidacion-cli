"""Motor principal de orquestación de la liquidación."""

from __future__ import annotations

import json
import time
import uuid
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from liquidator.params.params_loader import ParamsLoader
from liquidator.output.json_generator import JSONGenerator
from liquidator.compliance.compliance_engine import ComplianceEngine

from .input_parser import InputParser
from .workflow_orchestrator import WorkflowOrchestrator


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
