from pathlib import Path

from liquidator.core.input_parser import parse_input_file
from liquidator.core.workflow_orchestrator import WorkflowOrchestrator
from liquidator.params.params_loader import ParamsLoader

EXAMPLES = Path(__file__).resolve().parents[3] / "examples"


def test_workflow_orchestrator_generates_expected_desglose():
    params = ParamsLoader().load(2025)
    orchestrator = WorkflowOrchestrator(params)
    input_data = parse_input_file(EXAMPLES / "example_finca_rural.json")

    result = orchestrator.execute(input_data)

    assert result.calculation_results["sbl_general"] >= 1500000
    assert result.calculation_results["vacaciones"] == 0
    assert "cesantias" in result.compliance_payload["desglose"]
    assert any("auxilio" in key for key in result.validaciones_y_alertas)
