"""Compliance Engine for the Liquidation System - Implements V001-V010 compliance checks"""

from pathlib import Path
from typing import Dict, Any, Optional
from liquidator.compliance.rule_evaluator import RuleEvaluator
from liquidator.compliance.checklist_loader import ChecklistLoader
from liquidator.compliance.report_generator import ComplianceReportGenerator


class ComplianceEngine:
    def __init__(self, checklist_path: Optional[Path] = None):
        self.checklist_loader = ChecklistLoader(checklist_path)
        self.report_generator = ComplianceReportGenerator()
        
    def run(self, input_data: Dict[str, Any], params: Dict[str, Any], calculation_result: Optional[Dict[str, Any]] = None, input_hash: Optional[str] = None):
        """Execute all compliance checks and generate report."""
        checklist = self.checklist_loader.load()
        report = {
            "compliance_status": "GO",
            "summary": {"passed": 0, "warnings": 0, "failures": 0},
            "checks": [],
            "blocking_failures": [],
            "input_hash": input_hash or "",
            "output_hash": "",
            "params_version": params.get("version", "")
        }
        
        # Run each compliance check
        for rule_info in checklist:
            rule_id = rule_info["id"]
            evaluator_func = RuleEvaluator.build(rule_id, rule_info)
            evaluation_result = evaluator_func(input_data, calculation_result or {}, params)
            
            check_result = {
                "id": rule_id,
                "description": rule_info["description"],
                "result": evaluation_result["result"],
                "blocking": rule_info.get("blocking", False),
                "evidence": evaluation_result["evidence"],
                "norma": rule_info.get("norma", "")
            }
            
            report["checks"].append(check_result)
            
            # Update summary statistics
            if check_result["result"] == "PASS":
                report["summary"]["passed"] += 1
            elif check_result["result"] == "WARN":
                report["summary"]["warnings"] += 1
            elif check_result["result"] == "FAIL":
                report["summary"]["failures"] += 1
                if check_result["blocking"]:
                    report["blocking_failures"].append(rule_id)
                    
        # Determine compliance status based on results
        if report["summary"]["failures"] > 0 and report["blocking_failures"]:
            report["compliance_status"] = "NO_GO"
        elif report["summary"]["warnings"] > 0:
            report["compliance_status"] = "WARN"
            
        return report
