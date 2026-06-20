"""
Tests para el módulo de versioning manager.
"""

from liquidator.audit.versioning_manager import VersioningManager


class TestVersioningManager:
    """Tests para VersioningManager."""

    def setup_method(self):
        self.vm = VersioningManager()

    def test_get_current_params_version(self):
        """Test obtener versión de parámetros actual."""
        version = self.vm.get_current_params_version()
        assert isinstance(version, str)
        assert len(version) > 0

    def test_get_current_generator_version(self):
        """Test obtener versión del generador actual."""
        version = self.vm.get_current_generator_version()
        assert isinstance(version, str)
        assert version == "1.0.0"

    def test_validate_version_compatibility_valid(self):
        """Test validación de compatibilidad — versión válida (2025)."""
        assert self.vm.validate_version_compatibility("2025-01-01") is True
        assert self.vm.validate_version_compatibility("2025-10-31") is True

    def test_validate_version_compatibility_invalid(self):
        """Test validación de compatibilidad — versión inválida (pre-2025)."""
        assert self.vm.validate_version_compatibility("2024-01-01") is False

    def test_get_version_info(self):
        """Test obtener info completa de versiones."""
        info = self.vm.get_version_info()
        assert "generator_version" in info
        assert "params_version" in info
        assert "compatibility_check_date" in info
        assert info["generator_version"] == "1.0.0"

    def test_update_params_version_valid(self):
        """Test actualizar versión de parámetros (válida)."""
        self.vm.update_params_version("2025-06-01")
        assert self.vm.get_current_params_version() == "2025-06-01"

    def test_update_params_version_invalid_raises(self):
        """Test que versión inválida lanza ValueError."""
        try:
            self.vm.update_params_version("2024-01-01")
        except ValueError:
            pass
        else:
            raise AssertionError("Debería haber lanzado ValueError")

    def test_check_for_updates(self):
        """Test verificar actualizaciones (placeholder)."""
        result = self.vm.check_for_updates()
        assert "has_params_update" in result
        assert "has_generator_update" in result
        assert result["has_params_update"] is False
        assert result["has_generator_update"] is False
