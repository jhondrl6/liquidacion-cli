"""
Tests para el módulo de trail generator.
"""

import json
import tempfile
from pathlib import Path

from liquidator.audit.trail_generator import AuditTrail, TrailGenerator


class TestTrailGenerator:
    """Tests para TrailGenerator."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.trail_generator = TrailGenerator(trail_directory=self.temp_dir)
        self.session_id = "test_session_001"

    def test_create_audit_trail(self):
        """Test creación de audit trail."""
        input_data = {
            "modo": "PERIÓDICA",
            "fecha_ingreso": "2024-01-01",
            "fecha_corte": "2025-01-01",
        }
        trail = self.trail_generator.create_audit_trail(
            self.session_id, input_data
        )
        assert trail.session_id == self.session_id
        assert trail.input_data == input_data
        assert trail.output_data is None

    def test_complete_audit_trail(self):
        """Test completar audit trail con resultados."""
        trail = AuditTrail(self.session_id)
        output_data = {"desglose": {"cesantias": {"valor": 1000000}}}
        compliance_report = {"compliance_status": "GO", "checks": []}

        self.trail_generator.complete_audit_trail(
            trail, output_data, compliance_report
        )
        assert trail.output_data == output_data
        assert trail.compliance_report == compliance_report
        assert trail.version_info is not None
        assert "params_version" in trail.version_info
        assert "generator_version" in trail.version_info

    def test_save_audit_trail(self):
        """Test guardado de audit trail a disco."""
        trail = self.trail_generator.create_audit_trail(
            self.session_id, {"modo": "PERIÓDICA"}
        )
        self.trail_generator.complete_audit_trail(
            trail,
            {"desglose": {}},
            {"compliance_status": "GO"},
        )
        filepath = self.trail_generator.save_audit_trail(trail)
        assert Path(filepath).exists()

        # Verificar que el JSON es válido
        with open(filepath) as f:
            data = json.load(f)
        assert data["session_id"] == self.session_id

    def test_generate_and_save_trail(self):
        """Test pipeline completo: crear, completar y guardar."""
        filepath = self.trail_generator.generate_and_save_trail(
            input_data={"modo": "PERIÓDICA"},
            output_data={"desglose": {}},
            compliance_report={"compliance_status": "GO"},
        )
        assert Path(filepath).exists()

    def test_trail_directory_created(self):
        """Test que el directorio se crea si no existe."""
        new_dir = Path(self.temp_dir) / "nested" / "trails"
        TrailGenerator(trail_directory=str(new_dir))
        assert new_dir.exists()


class TestAuditTrail:
    """Tests para la clase AuditTrail."""

    def test_audit_trail_init(self):
        """Test inicialización de AuditTrail."""
        trail = AuditTrail("session_001")
        assert trail.session_id == "session_001"
        assert trail.timestamp is not None
        assert trail.input_data is None
        assert trail.output_data is None
        assert trail.compliance_report is None
        assert trail.version_info is None
