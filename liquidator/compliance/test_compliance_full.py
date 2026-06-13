"""
Test integrado V001…V010 – SESIONES 7 y 8
"""

import json
from pathlib import Path
from liquidator.compliance.compliance_engine import ComplianceEngine

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_finca_caso_cumple():
    input_path = FIXTURES / "example_finca_input.json"
    params_path = FIXTURES / "params_2025.json"
    checklist_path = FIXTURES / "checklist.json"

    input_data = json.loads(input_path.read_text())
    params = json.loads(params_path.read_text())

    engine = ComplianceEngine(checklist_path)
    report = engine.run(input_data, params)

    assert report["compliance_status"] == "GO"
    assert report["summary"]["failures"] == 0
    assert any(c["id"] == "V003" and c["result"] == "PASS" for c in report["checks"])
