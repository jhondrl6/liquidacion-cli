import json
from pathlib import Path

import pytest

from liquidator.params.params_validator import (
    HAS_JSONSCHEMA,
    ParamsValidator,
    ValidationError,
)


@pytest.fixture
def simple_schema():
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "year": {"type": "integer"},
            "salario_minimo": {"type": "integer", "minimum": 0},
        },
        "required": ["year", "salario_minimo"],
    }


@pytest.fixture
def valid_data():
    return {"year": 2025, "salario_minimo": 1423500}


@pytest.fixture
def invalid_data():
    return {"year": "2025", "salario_minimo": -100}


@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent.parent / "fixtures"


class TestParamsValidatorInit:
    def test_init_without_schema(self):
        validator = ParamsValidator()
        if HAS_JSONSCHEMA:
            assert validator._schema is None
            assert validator._validator is None
        else:
            assert validator._schema is None
            assert validator._validator is None

    def test_init_with_schema(self, simple_schema):
        validator = ParamsValidator(schema=simple_schema)
        if HAS_JSONSCHEMA:
            assert validator._schema == simple_schema
            assert validator._validator is not None
        else:
            assert validator._schema is None


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
class TestValidationWithJsonschema:
    def test_validate_valid_data(self, simple_schema, valid_data):
        validator = ParamsValidator(schema=simple_schema)
        result = validator.validate(valid_data)
        assert result is True
        assert validator.last_validation_message == "Validacion exitosa"

    def test_validate_invalid_data(self, simple_schema, invalid_data):
        validator = ParamsValidator(schema=simple_schema)
        with pytest.raises(ValidationError, match="Schema validation fallida"):
            validator.validate(invalid_data)

    def test_validate_missing_required_field(self, simple_schema):
        validator = ParamsValidator(schema=simple_schema)
        incomplete_data = {"year": 2025}
        with pytest.raises(ValidationError, match="salario_minimo"):
            validator.validate(incomplete_data)

    def test_load_schema_success(self, tmp_path, simple_schema):
        schema_file = tmp_path / "test_schema.json"
        schema_file.write_text(json.dumps(simple_schema), encoding="utf-8")
        validator = ParamsValidator()
        validator.load_schema(schema_file)
        assert validator._schema == simple_schema
        assert "Schema cargado" in validator.last_validation_message

    def test_load_schema_file_not_found(self):
        validator = ParamsValidator()
        with pytest.raises(ValidationError, match="Schema no encontrado"):
            validator.load_schema(Path("nonexistent.json"))

    def test_load_schema_invalid_json(self, tmp_path):
        schema_file = tmp_path / "invalid_schema.json"
        schema_file.write_text("{invalid json", encoding="utf-8")
        validator = ParamsValidator()
        with pytest.raises(ValidationError, match="Schema JSON invalido"):
            validator.load_schema(schema_file)

    def test_ensure_schema_loaded_without_path(self):
        validator = ParamsValidator()
        with pytest.raises(ValidationError, match="Schema path requerido"):
            validator.ensure_schema_loaded(None)

    def test_ensure_schema_loaded_already_loaded(self, simple_schema):
        validator = ParamsValidator(schema=simple_schema)
        validator.ensure_schema_loaded(Path("dummy.json"))
        assert validator._validator is not None

    def test_validate_multiple_errors(self, simple_schema):
        validator = ParamsValidator(schema=simple_schema)
        bad_data = {"year": "not_an_int", "salario_minimo": "also_not_an_int"}
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(bad_data)
        assert "year" in str(exc_info.value) or "salario_minimo" in str(exc_info.value)


class TestValidationWithoutJsonschema:
    def test_validate_without_jsonschema(self, monkeypatch, valid_data):
        monkeypatch.setattr("liquidator.params.params_validator.HAS_JSONSCHEMA", False)
        validator = ParamsValidator()
        result = validator.validate(valid_data)
        assert result is True
        assert "omitida" in validator.last_validation_message

    def test_load_schema_without_jsonschema(self, monkeypatch, tmp_path):
        monkeypatch.setattr("liquidator.params.params_validator.HAS_JSONSCHEMA", False)
        validator = ParamsValidator()
        schema_file = tmp_path / "schema.json"
        schema_file.write_text("{}", encoding="utf-8")
        validator.load_schema(schema_file)
        assert "jsonschema no instalado" in validator.last_validation_message
