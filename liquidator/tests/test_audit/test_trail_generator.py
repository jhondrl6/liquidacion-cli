"""
Tests para el módulo de trail generator.
"""

import tempfile
from pathlib import Path

from liquidator.audit.trail_generator import AuditTrail, TrailGenerator


class TestTrailGenerator:
    """Tests para TrailGenerator."""

    def setup_method(self):
        """Configuración antes de cada test."""
        self.temp_dir = tempfile.mkdtemp()
        self.trail_generator = TrailGenerator(trails_directory=self.temp_dir)
        self.session_id = "test_session_001"

    def create_test_audit_trail(self) -> AuditTrail:
        """Crea un audit trail de prueba."""
        input_data = {
            "modo": "PERIÓDICA",
            "fecha_ingreso": "2024-01-01",
            "fecha_corte": "2025-01-01",
        }

        output_data = {
            "meta": {"fecha_generacion": "2025-01-01T10:00:00"},
            "desglose": {"cesantias": {"valor": 1000000}},
        }

        compliance_report = {
            "compliance_status": "GO",
            "checks": [{"id": "V001", "result": "PASS"}],
        }

        execution_logs = [
            {
                "timestamp": "2025-01-01T09:00:00",
                "event_type": "calculation_started",
                "session_id": self.session_id,
            }
        ]

        override_records = []

        return self.trail_generator.generate_audit_trail(
            session_id=self.session_id,
            input_data=input_data,
            output_data=output_data,
            compliance_report=compliance_report,
            execution_logs=execution_logs,
            override_records=override_records,
            params_version="2025-01-01",
            generator_version="1.0.0",
        )

    def test_generate_audit_trail(self):
        """Test generación de audit trail."""
        audit_trail = self.create_test_audit_trail()

        assert audit_trail.session_id == self.session_id
        assert audit_trail.input_data["modo"] == "PERIÓDICA"
        assert audit_trail.output_data["desglose"]["cesantias"]["valor"] == 1000000
        assert audit_trail.compliance_report["compliance_status"] == "GO"
        assert audit_trail.params_version == "2025-01-01"
        assert audit_trail.generator_version == "1.0.0"
        assert audit_trail.input_hash.startswith("sha256:")
        assert audit_trail.output_hash.startswith("sha256:")

    def test_save_and_load_audit_trail(self):
        """Test guardado y carga de audit trail."""
        audit_trail = self.create_test_audit_trail()

        # Guardar trail
        file_path = self.trail_generator.save_audit_trail(audit_trail)
        assert Path(file_path).exists()

        # Cargar trail
        loaded_trail = self.trail_generator.load_audit_trail(file_path)

        assert loaded_trail.session_id == audit_trail.session_id
        assert loaded_trail.input_hash == audit_trail.input_hash
        assert loaded_trail.output_hash == audit_trail.output_hash

    def test_search_audit_trails(self):
        """Test búsqueda de audit trails."""
        # Crear y guardar múltiples trails
        for i in range(3):
            trail = self.create_test_audit_trail()
            trail.session_id = f"session_{i}"
            self.trail_generator.save_audit_trail(trail)

        # Buscar todos los trails
        all_trails = self.trail_generator.search_audit_trails()
        assert len(all_trails) == 3

        # Buscar por session_id
        session_1_trails = self.trail_generator.search_audit_trails(
            session_id="session_1"
        )
        assert len(session_1_trails) == 1
        assert session_1_trails[0]["session_id"] == "session_1"

    def test_generate_audit_summary_report(self):
        """Test generación de reporte resumen."""
        # Crear algunos trails de prueba
        for i in range(5):
            trail = self.create_test_audit_trail()
            trail.session_id = f"session_{i}"
            self.trail_generator.save_audit_trail(trail)

        summary_report = self.trail_generator.generate_audit_summary_report()

        assert summary_report["total_trails"] == 5
        assert "compliance_statistics" in summary_report
        assert "date_range" in summary_report
        assert len(summary_report["trail_files"]) == 5

    def test_search_with_date_range(self):
        """Test búsqueda con rango de fechas."""
        trail = self.create_test_audit_trail()
        self.trail_generator.save_audit_trail(trail)

        # Buscar con rango que incluye la fecha del trail
        start_date = "2024-12-01"
        end_date = "2025-12-31"

        trails_in_range = self.trail_generator.search_audit_trails(
            date_range=(start_date, end_date)
        )

        assert len(trails_in_range) >= 1

        # Buscar con rango que excluye la fecha del trail
        start_date = "2026-01-01"
        end_date = "2026-12-31"

        trails_out_range = self.trail_generator.search_audit_trails(
            date_range=(start_date, end_date)
        )

        assert len(trails_out_range) == 0
