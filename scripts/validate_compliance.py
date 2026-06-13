#!/usr/bin/env python3
"""
Independent script for legal compliance validation.
Can be executed without performing complete settlement calculations.

Author: Development Team
Date: 2025-11-04
Version: 1.0.0
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from liquidator.compliance.compliance_engine import ComplianceEngine
from liquidator.core.input_parser import InputParser
from liquidator.params.params_loader import ParamsLoader
from liquidator.output.json_generator import write_json_file
from liquidator.utils.file_utils import read_json_file


def load_test_case(file_path: str) -> Dict[str, Any]:
    """Loads a test case from a JSON file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Test case file not found: {file_path}")
    
    return read_json_file(file_path)


def generate_compliance_report(input_data: Dict[str, Any], 
                               params: Dict[str, Any],
                               output_path: Optional[str] = None) -> Dict[str, Any]:
    """Generates a compliance report for the provided data."""
    # Initialize compliance engine
    compliance_engine = ComplianceEngine(params)
    
    # Run validations
    compliance_report = compliance_engine.run_compliance_check(input_data)
    
    # Prepare full report
    report = {
        "timestamp": datetime.now().isoformat(),
        "input_data_hash": hash(str(input_data)),
        "compliance_status": compliance_report["compliance_status"],
        "summary": compliance_report["summary"],
        "checks": compliance_report["checks"],
        "blocking_failures": compliance_report["blocking_failures"],
        "recommendations": generate_recommendations(compliance_report)
    }
    
    # Save report if a path is specified
    if output_path:
        write_json_file(report, output_path)
    
    return report


def generate_recommendations(compliance_report: Dict[str, Any]) -> list:
    """Generates recommendations based on the compliance report."""
    recommendations = []
    
    # Analyze critical failures
    for check in compliance_report["checks"]:
        if check["result"] == "FAIL" and check["blocking"]:
            recommendation = {
                "rule_id": check["id"],
                "description": f"Fix critical non-compliance: {check['description']}",
                "action": get_remediation_action(check["id"], check["evidence"])
            }
            recommendations.append(recommendation)
    
    # Analyze warnings
    warning_count = compliance_report["summary"]["warnings"]
    if warning_count > 0:
        recommendations.append({
            "rule_id": "GENERAL",
            "description": f"Review {warning_count} warnings in the report",
            "action": "Analyze warnings and determine if they require correction before processing"
        })
    
    # If there are many issues, suggest legal review
    total_issues = len(compliance_report["blocking_failures"]) + warning_count
    if total_issues > 3:
        recommendations.append({
            "rule_id": "LEGAL_REVIEW",
            "description": "Request complete legal review",
            "action": "Given the number of non-compliances detected, it is recommended to consult with legal expert before continuing"
        })
    
    return recommendations


def get_remediation_action(rule_id: str, evidence: list) -> str:
    """Returns a specific remediation action for each rule."""
    remediation_actions = {
        "V001": "Verify that official parameters are correct for the current year",
        "V002": "Confirm that the contract type is legally recognized for benefit settlements",
        "V003": "Review transportation allowance application conditions based on worker residence",
        "V004": "Verify formula used for severance calculation against current regulation",
        "V005": "Confirm that interest rate for severance is 12% annually as established by law",
        "V006": "Review proportional calculation of service bonus for the current semester",
        "V007": "Confirm that vacations are not included in periodic settlements",
        "V008": "Document legal payment deadlines for each concept",
        "V009": "Ensure that each calculation includes complete regulatory references",
        "V010": "Verify that the system generates hashes and maintains appropriate versioning"
    }
    
    return remediation_actions.get(rule_id, "Consult legal documentation for specific remediation")


def display_report(report: Dict[str, Any]):
    """Displays the compliance report in a readable format."""
    print("\n" + "="*60)
    print("LEGAL COMPLIANCE REPORT")
    print("="*60)
    print(f"Date and time: {report['timestamp']}")
    print(f"General status: {report['compliance_status']}")
    print("-"*60)
    
    # Summary
    summary = report['summary']
    print(f"\nSUMMARY:")
    print(f"PASS: {summary['passed']}")
    print(f"WARNINGS: {summary['warnings']}")
    print(f"FAILURES: {summary['failures']}")
    
    # Show failed and warning checks
    if report['blocking_failures'] or any(c["result"] in ["WARN", "FAIL"] for c in report['checks']):
        print("\nNON-COMPLIANCE DETAILS:")
        print("-"*60)
        
        for check in report['checks']:
            if check["result"] in ["WARN", "FAIL"]:
                print(f"\n{check['id']}: {check['description']}")
                print(f"   Result: {check['result']}")
                print(f"   Evidence:")
                for evidence in check["evidence"]:
                    print(f"   - {evidence}")
    
    # Show recommendations
    if report['recommendations']:
        print("\n" + "-"*60)
        print("RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"\n- {rec['description']}")
            print(f"  Action: {rec['action']}")
    
    print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(description='Independent legal compliance validator')
    parser.add_argument('--input', required=True,
                        help='JSON file with input data for validation')
    parser.add_argument('--output', 
                        help='Output file to save the report (JSON)')
    parser.add_argument('--silent', action='store_true',
                        help='Do not show results in console, only save to file')
    parser.add_argument('--year', type=int, default=2025,
                        help='Year of parameters to use (default: 2025)')
    parser.add_argument('--policy', choices=['lenient', 'standard', 'strict'],
                        default='standard',
                        help='Compliance policy to apply (default: standard)')
    
    args = parser.parse_args()
    
    # Configure paths
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    try:
        # Load input data
        input_data = load_test_case(args.input)
        print(f"[SUCCESS] Loaded test case: {args.input}")
        
        # Load parameters
        params_loader = ParamsLoader()
        params = params_loader.load_params(args.year)
        print(f"[SUCCESS] Loaded parameters for year {args.year}")
        
        # Configure compliance policy
        params['compliance_policy'] = args.policy
        print(f"[SUCCESS] Configured compliance policy: {args.policy}")
        
        # Generate compliance report
        print("Running compliance validations...")
        report = generate_compliance_report(
            input_data=input_data,
            params=params,
            output_path=args.output
        )
        
        # Display results
        if not args.silent:
            display_report(report)
        
        # Save report if specified
        if args.output:
            print(f"[INFO] Report saved to: {args.output}")
        
        # Exit with error code if there are blocking failures
        if report['compliance_status'] == "NO_GO":
            print("\n[ERROR] The test case DOES NOT COMPLY with minimum legal requirements.")
            return 1
        
        print("\n[SUCCESS] The test case complies with legal requirements.")
        return 0
        
    except Exception as e:
        print(f"[ERROR] Error during validation: {e}")
        return 1


if __name__ == "__main__":
    exit(main())