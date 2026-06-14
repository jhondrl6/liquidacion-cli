"""
Tests para el módulo de versioning manager.
"""

import tempfile
from pathlib import Path

from liquidator.audit.versioning_manager import VersioningManager


class TestVersioningManager:
    """Tests para VersioningManager."""

    def setup_method(self):
        """Configuración antes de cada test."""
        self.temp_dir = tempfile.mkdtemp()
        self.version_file = Path(self.temp_dir) / "version_control.json"
        self.version_manager = VersioningManager(version_file=str(self.version_file))

    def test_register_generator_version(self):
        """Test registro de versión de generador."""
        self.version_manager.register_generator_version(
            version="1.0.0",
            description="Versión inicial",
            checksum="sha256:abc123",
            dependencies={"python": "3.8+"},
        )

        current_versions = self.version_manager.get_current_versions()
        assert current_versions["generator"] == "1.0.0"

        generator_history = self.version_manager.get_version_history("generator")
        assert len(generator_history) == 1
        assert generator_history[0]["version"] == "1.0.0"
        assert generator_history[0]["description"] == "Versión inicial"

    def test_register_params_version(self):
        """Test registro de versión de parámetros."""
        self.version_manager.register_params_version(
            version="2025-01-01",
            description="Parámetros oficiales 2025",
            params_file="params/2025.json",
            checksum="sha256:def456",
        )

        current_versions = self.version_manager.get_current_versions()
        assert current_versions["params"] == "2025-01-01"

        params_history = self.version_manager.get_version_history("params")
        assert len(params_history) == 1
        assert params_history[0]["version"] == "2025-01-01"
        assert params_history[0]["description"] == "Parámetros oficiales 2025"

    def test_validate_version_compatibility_valid(self):
        """Test validación de compatibilidad de versiones válida."""
        # Registrar versiones compatibles
        self.version_manager.register_generator_version("1.0.0", "Test version")
        self.version_manager.register_params_version("2025-01-01", "Test params")

        result = self.version_manager.validate_version_compatibility(
            generator_version="1.0.0", params_version="2025-01-01"
        )

        assert result["is_compatible"] is True
        assert len(result["errors"]) == 0

    def test_validate_version_compatibility_invalid(self):
        """Test validación de compatibilidad de versiones inválida."""
        result = self.version_manager.validate_version_compatibility(
            generator_version="2.0.0", params_version="2024-01-01"  # No registrada
        )

        assert result["is_compatible"] is False
        assert len(result["errors"]) > 0

    def test_generate_version_report(self):
        """Test generación de reporte de versiones."""
        # Registrar algunas versiones
        for i in range(3):
            self.version_manager.register_generator_version(
                version=f"1.0.{i}", description=f"Version 1.0.{i}"
            )

        for i in range(2):
            self.version_manager.register_params_version(
                version=f"2025-01-0{i+1}", description=f"Params 2025-01-0{i+1}"
            )

        report = self.version_manager.generate_version_report()

        assert report["total_generator_versions"] == 3
        assert report["total_params_versions"] == 2
        assert "current_versions" in report
        assert "generator_history" in report
        assert "params_history" in report
        assert len(report["generator_history"]) == 3
        assert len(report["params_history"]) == 2

    def test_persistence(self):
        """Test que las versiones se persisten correctamente."""
        # Registrar versiones
        self.version_manager.register_generator_version("1.0.0", "Test version")
        self.version_manager.register_params_version("2025-01-01", "Test params")

        # Crear nuevo manager (simula reinicio)
        new_manager = VersioningManager(version_file=str(self.version_file))

        # Verificar que carga las versiones anteriores
        current_versions = new_manager.get_current_versions()
        assert current_versions["generator"] == "1.0.0"
        assert current_versions["params"] == "2025-01-01"

        generator_history = new_manager.get_version_history("generator")
        assert len(generator_history) == 1
        assert generator_history[0]["version"] == "1.0.0"
