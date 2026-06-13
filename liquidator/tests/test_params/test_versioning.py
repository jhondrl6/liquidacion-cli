import json
import pytest
from pathlib import Path
from liquidator.params.params_versioning import ParamsVersioning, VersionInfo


@pytest.fixture
def versioning():
    return ParamsVersioning()


@pytest.fixture
def sample_params_file(tmp_path):
    file_path = tmp_path / "2025.json"
    data = {
        "version": "1.0",
        "year": 2025,
        "salario_minimo": 1423500,
        "metadata": {"source": "test"},
    }
    file_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return file_path


class TestVersionInfo:
    def test_version_info_creation(self):
        info = VersionInfo(
            year=2025,
            version="1.0",
            hash_sha256="abc123",
            fecha_carga="2025-01-01T00:00:00Z",
        )
        assert info.year == 2025
        assert info.version == "1.0"
        assert info.hash_sha256 == "abc123"
        assert info.fecha_carga == "2025-01-01T00:00:00Z"
        assert info.metadata is None

    def test_version_info_with_metadata(self):
        info = VersionInfo(
            year=2025,
            version="1.0",
            hash_sha256="abc123",
            fecha_carga="2025-01-01T00:00:00Z",
            metadata={"source": "oficial"},
        )
        assert info.metadata == {"source": "oficial"}


class TestCalculateFileHash:
    def test_calculate_file_hash(self, versioning, sample_params_file):
        hash1 = versioning.calculate_file_hash(sample_params_file)
        assert isinstance(hash1, str)
        assert len(hash1) == 64

    def test_calculate_file_hash_deterministic(self, versioning, sample_params_file):
        hash1 = versioning.calculate_file_hash(sample_params_file)
        hash2 = versioning.calculate_file_hash(sample_params_file)
        assert hash1 == hash2

    def test_calculate_file_hash_different_files(self, versioning, tmp_path):
        file1 = tmp_path / "file1.json"
        file2 = tmp_path / "file2.json"
        file1.write_text('{"a": 1}', encoding="utf-8")
        file2.write_text('{"a": 2}', encoding="utf-8")
        hash1 = versioning.calculate_file_hash(file1)
        hash2 = versioning.calculate_file_hash(file2)
        assert hash1 != hash2


class TestCalculateDataHash:
    def test_calculate_data_hash(self, versioning):
        data = {"year": 2025, "salario_minimo": 1423500}
        hash_val = versioning.calculate_data_hash(data)
        assert isinstance(hash_val, str)
        assert len(hash_val) == 64

    def test_calculate_data_hash_deterministic(self, versioning):
        data = {"year": 2025, "salario_minimo": 1423500}
        hash1 = versioning.calculate_data_hash(data)
        hash2 = versioning.calculate_data_hash(data)
        assert hash1 == hash2

    def test_calculate_data_hash_order_independent(self, versioning):
        data1 = {"year": 2025, "salario_minimo": 1423500}
        data2 = {"salario_minimo": 1423500, "year": 2025}
        hash1 = versioning.calculate_data_hash(data1)
        hash2 = versioning.calculate_data_hash(data2)
        assert hash1 == hash2

    def test_calculate_data_hash_with_unicode(self, versioning):
        data = {"descripción": "Parámetros 2025"}
        hash_val = versioning.calculate_data_hash(data)
        assert isinstance(hash_val, str)
        assert len(hash_val) == 64


class TestRegisterVersion:
    def test_register_version_basic(self, versioning, sample_params_file):
        info = versioning.register_version(year=2025, path=sample_params_file)
        assert info.year == 2025
        assert info.version == "1.0"
        assert len(info.hash_sha256) == 64
        assert "T" in info.fecha_carga

    def test_register_version_with_data(self, versioning, sample_params_file):
        data = {"version": "2.0", "metadata": {"source": "oficial"}}
        info = versioning.register_version(
            year=2025, path=sample_params_file, data=data
        )
        assert info.version == "2.0"
        assert info.metadata == {"source": "oficial"}

    def test_register_version_stores_in_dict(self, versioning, sample_params_file):
        info = versioning.register_version(year=2025, path=sample_params_file)
        stored = versioning._versions.get(2025)
        assert stored is info


class TestGetVersion:
    def test_get_version_exists(self, versioning, sample_params_file):
        registered = versioning.register_version(year=2025, path=sample_params_file)
        retrieved = versioning.get_version(year=2025)
        assert retrieved == registered

    def test_get_version_not_exists(self, versioning):
        retrieved = versioning.get_version(year=2024)
        assert retrieved is None


class TestVerifyIntegrity:
    def test_verify_integrity_success(self, versioning, sample_params_file):
        versioning.register_version(year=2025, path=sample_params_file)
        is_valid = versioning.verify_integrity(
            year=2025, current_path=sample_params_file
        )
        assert is_valid is True

    def test_verify_integrity_file_modified(self, versioning, tmp_path):
        file_path = tmp_path / "params.json"
        file_path.write_text('{"version": "1.0"}', encoding="utf-8")
        versioning.register_version(year=2025, path=file_path)
        file_path.write_text('{"version": "2.0"}', encoding="utf-8")
        is_valid = versioning.verify_integrity(year=2025, current_path=file_path)
        assert is_valid is False

    def test_verify_integrity_not_registered(self, versioning, sample_params_file):
        is_valid = versioning.verify_integrity(
            year=2025, current_path=sample_params_file
        )
        assert is_valid is False


class TestToDict:
    def test_to_dict_empty(self, versioning):
        result = versioning.to_dict()
        assert result == {}

    def test_to_dict_single_version(self, versioning, sample_params_file):
        versioning.register_version(year=2025, path=sample_params_file)
        result = versioning.to_dict()
        assert 2025 in result
        assert result[2025]["year"] == 2025
        assert "hash_sha256" in result[2025]
        assert "fecha_carga" in result[2025]

    def test_to_dict_multiple_versions(self, versioning, tmp_path):
        file2025 = tmp_path / "2025.json"
        file2024 = tmp_path / "2024.json"
        file2025.write_text('{"year": 2025}', encoding="utf-8")
        file2024.write_text('{"year": 2024}', encoding="utf-8")
        versioning.register_version(year=2025, path=file2025)
        versioning.register_version(year=2024, path=file2024)
        result = versioning.to_dict()
        assert len(result) == 2
        assert 2025 in result
        assert 2024 in result


class TestIntegration:
    def test_full_workflow(self, versioning, tmp_path):
        file_path = tmp_path / "2025.json"
        data = {
            "version": "1.0",
            "year": 2025,
            "salario_minimo": 1423500,
            "metadata": {"source": "test"},
        }
        file_path.write_text(json.dumps(data), encoding="utf-8")
        info = versioning.register_version(year=2025, path=file_path, data=data)
        assert versioning.verify_integrity(year=2025, current_path=file_path)
        retrieved = versioning.get_version(year=2025)
        assert retrieved.hash_sha256 == info.hash_sha256
        as_dict = versioning.to_dict()
        assert as_dict[2025]["version"] == "1.0"
