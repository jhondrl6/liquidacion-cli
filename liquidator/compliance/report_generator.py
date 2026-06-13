"""
Ensambla el compliance_report final a partir
de los resultados individuales de cada regla.
"""

from datetime import datetime, timezone
from typing import List, Dict, Optional


class ComplianceReportGenerator:
    @staticmethod
    def build(
        rules: List[Dict],
        input_data: Dict,
        calculation_result: Optional[Dict],
        params: Dict,
    ) -> Dict:
        """Genera el reporte consolidado de cumplimiento."""

        summary = {"passed": 0, "warnings": 0, "failures": 0}
        checks = []
        blocking = []

        calculation_result = calculation_result or {}

        for rule in rules:
            evaluator = rule["evaluator"]
            evaluation = evaluator(input_data, calculation_result, params)
            result_value = evaluation["result"].upper()

            if result_value == "PASS":
                summary["passed"] += 1
            elif result_value == "WARN":
                summary["warnings"] += 1
            else:
                summary["failures"] += 1

            checks.append(
                {
                    "id": rule["id"],
                    "description": rule["description"],
                    "result": result_value,
                    "evidence": evaluation.get("evidence", ""),
                    "rule_ref": rule.get("rule_ref", []),
                }
            )

            if (
                result_value == "FAIL"
                and rule.get("severity", "").upper() == "CRITICAL"
            ):
                blocking.append(rule["id"])

        compliance_status = "GO" if not blocking else "NO_GO"

        return {
            "compliance_status": compliance_status,
            "summary": summary,
            "checks": checks,
            "blocking_failures": blocking,
            "params_version": params.get("version"),
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "input_hash": "",
            "output_hash": "",
            "operator_action": {
                "action": "auto",
                "operator_id": None,
                "justification": None,
            },
        }
