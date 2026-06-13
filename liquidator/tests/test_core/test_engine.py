from pathlib import Path

from liquidator.core.engine import LiquidacionEngine
from liquidator.core.input_parser import parse_input_file


EXAMPLES = Path(__file__).resolve().parents[3] / "examples"


def test_engine_process_input_generates_output():
    engine = LiquidacionEngine()
    input_data = parse_input_file(EXAMPLES / "example_finca_rural.json")

    output = engine.process_input(input_data)

    assert output["desglose"]["cesantias"]["valor"] > 0
    assert output["desglose"]["vacaciones"]["valor"] == 0
    assert output["meta"]["input_hash"].startswith("sha256:")
    assert output["compliance_report"]["compliance_status"] in {
        "GO",
        "NO_GO",
        "OVERRIDE_APPROVED",
    }
    assert "normas_aplicadas" in output and len(output["normas_aplicadas"]) >= 3
