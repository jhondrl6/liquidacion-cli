import json
from pathlib import Path

import pytest

from liquidator.params.params_loader import ParamsError, ParamsLoader, ParamsSource
from liquidator.params.params_validator import ParamsValidator


@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def params_dir():
    return Path(__file__).parent.parent.parent.parent / "params"


@pytest.fixture
def loader_without_validator(fixtures_dir):
    return ParamsLoader(base_dir=fixtures_dir, validator=None)


@pytest.fixture
def loader_with_validator(fixtures_dir):
    validator = ParamsValidator()
    return ParamsLoader(base_dir=fixtures_dir, validator=validator)


class TestParamsSource:
    def test_params_source_creation(self):
        source = ParamsSource(year=2025, path=Path("test.json"))
        assert source.year == 2025
        assert source.path == Path("test.json")
        assert source.schema_path is None

    def test_params_source_with_schema(self):
        source = ParamsSource(
            year=2025, path=Path("test.json"), schema_path=Path("schema.json")
        )
        assert source.schema_path == Path("schema.json")


class TestParamsLoaderInitialization:
    def test_init_with_string_path(self):
        loader = ParamsLoader(base_dir="params")
        assert loader.base_dir == Path("params")

    def test_init_with_path_object(self):
        loader = ParamsLoader(base_dir=Path("params"))
        assert loader.base_dir == Path("params")

    def test_init_without_validator(self):
        loader = ParamsLoader(base_dir="params")
        assert loader.validator is None

    def test_init_with_validator(self):
        validator = ParamsValidator()
        loader = ParamsLoader(base_dir="params", validator=validator)
        assert loader.validator is validator


class TestResolvePaths:
    def test_resolve_paths_default(self, loader_without_validator):
        source = loader_without_validator.resolve_paths(year=2025)
        assert source.year == 2025
        assert source.path.name == "2025.json"
        assert source.schema_path.name == "schema.json"

    def test_resolve_paths_explicit(self, loader_without_validator):
        source = loader_without_validator.resolve_paths(
            year=2025, explicit_path="custom.json", schema_path="custom_schema.json"
        )
        assert source.path == Path("custom.json")
        assert source.schema_path == Path("custom_schema.json")


class TestLoadRaw:
    def test_load_raw_success(self, loader_without_validator, fixtures_dir):
        source = ParamsSource(year=2025, path=fixtures_dir / "params_test.json")
        data = loader_without_validator.load_raw(source)
        assert isinstance(data, dict)
        assert data["year"] == 2025
        assert data["salario_minimo"] == 1423500

    def test_load_raw_file_not_found(self, loader_without_validator):
        source = ParamsSource(year=2025, path=Path("nonexistent.json"))
        with pytest.raises(ParamsError, match="No se encontró el archivo"):
            loader_without_validator.load_raw(source)

    def test_load_raw_invalid_json(self, tmp_path):
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{invalid json", encoding="utf-8")
        loader = ParamsLoader(base_dir=tmp_path)
        source = ParamsSource(year=2025, path=invalid_file)
        with pytest.raises(ParamsError, match="JSON inválido"):
            loader.load_raw(source)


class TestLoad:
    def test_load_without_validation(self, loader_without_validator):
        data = loader_without_validator.load(
            year=2025,
            path=loader_without_validator.base_dir / "params_test.json",
            validate=False,
        )
        assert data["year"] == 2025
        assert "salario_minimo" in data

    def test_load_with_validation_no_validator(self, loader_without_validator):
        data = loader_without_validator.load(
            year=2025,
            path=loader_without_validator.base_dir / "params_test.json",
            validate=True,
        )
        assert data["year"] == 2025

    def test_load_with_explicit_path(self, loader_without_validator, fixtures_dir):
        data = loader_without_validator.load(
            year=2025, path=fixtures_dir / "params_test.json", validate=False
        )
        assert (
            data["metadata"]["descripcion"]
            == "Parametros de prueba para tests unitarios"
        )


class TestLoadRealParams:
    def test_load_2025_params(self, params_dir):
        loader = ParamsLoader(base_dir=params_dir)
        data = loader.load(year=2025, validate=False)
        assert isinstance(data, dict)
        assert "SMMLV" in data or "version" in data


class TestEdgeCases:
    def test_load_with_unicode(self, tmp_path):
        unicode_file = tmp_path / "unicode.json"
        test_data = {"descripción": "Parámetros con acentos", "año": 2025}
        unicode_file.write_text(
            json.dumps(test_data, ensure_ascii=False), encoding="utf-8"
        )
        loader = ParamsLoader(base_dir=tmp_path)
        data = loader.load(year=2025, path=unicode_file, validate=False)
        assert data["descripción"] == "Parámetros con acentos"
        assert data["año"] == 2025
