import os
from pathlib import Path

from liquidator.core.input_parser import InputParser, parse_input_file
from liquidator.params.params_loader import ParamsLoader


FIXTURES_DIR = Path(__file__).resolve().parents[3] / "examples"


def test_parse_input_file_normalizes_fields():
    example_path = FIXTURES_DIR / "example_finca_rural.json"
    data = parse_input_file(example_path)

    assert data["modo"] == "PERIÓDICA"
    assert data["moneda"] == "COP"
    assert data["enforce_compliance"] is True
    assert data["auxilio_conectividad_pactado"] is True


def test_input_parser_applies_validation():
    params = ParamsLoader().load(2025)
    parser = InputParser()
    payload = parse_input_file(FIXTURES_DIR / "example_finca_rural.json")

    parsed = parser.parse_payload(payload, params=params)

    assert parsed.data["modo"] == "PERIÓDICA"
    assert isinstance(parsed.warnings, list)
