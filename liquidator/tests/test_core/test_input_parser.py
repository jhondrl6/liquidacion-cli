from pathlib import Path

from liquidator.core.input_parser import InputParser, parse_input_file
from liquidator.params.params_loader import ParamsLoader

FIXTURES_DIR = Path(__file__).resolve().parents[3] / "examples"


def test_parse_input_file_normalizes_fields():
    example_path = FIXTURES_DIR / "example_finca_rural.json"
    data = parse_input_file(example_path)

    assert data["modo"] == "PERIODICA"
    assert "fecha_ingreso" in data
    assert "fecha_corte" in data
    assert "salario_mensual" in data


def test_input_parser_applies_validation():
    params = ParamsLoader().load(2025)
    parser = InputParser()
    payload = parse_input_file(FIXTURES_DIR / "example_finca_rural.json")

    parsed = parser.parse(payload)

    assert parsed["modo"] == "PERIODICA"
    assert "salario_mensual" in parsed
