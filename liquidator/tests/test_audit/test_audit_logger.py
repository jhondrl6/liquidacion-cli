"""
Tests para el módulo de audit logger.
"""

import pytest
import tempfile
import json
from pathlib import Path
from liquidator.audit.audit_logger import AuditLogger, AuditEventType


class TestAuditLogger:
    """Tests para AuditLogger."""

    def setup_method(self):
        """Configuración antes de cada test."""
        self.temp_dir = tempfile.mkdtemp()
        self.audit_logger = AuditLogger(log_directory=self.temp_dir)
        self.session_id = "test_session_001"

    def test_log_event(self):
        """Test registro básico de evento."""
        self.audit_logger.log_event(
            event_type=AuditEventType.CALCULATION_STARTED,
            session_id=self.session_id,
            message="Test event message",
            extra_data={"test_field": "test_value"},
        )

        # Verificar que se creó el archivo de log
        log_files = list(Path(self.temp_dir).glob("*.log"))
        assert len(log_files) == 1

        # Verificar contenido del log
        with open(log_files[0], "r", encoding="utf-8") as f:
            log_lines = f.readlines()

        assert len(log_lines) == 1

        log_entry = json.loads(log_lines[0])
        assert log_entry["session_id"] == self.session_id
        assert log_entry["event_type"] == "calculation_started"
        assert log_entry["message"] == "Test event message"
        assert log_entry["test_field"] == "test_value"

    def test_log_calculation_start(self):
        """Test registro de inicio de cálculo."""
        input_data = {
            "modo": "PERIÓDICA",
            "fecha_ingreso": "2024-01-01",
            "fecha_corte": "2025-01-01",
            "salario_mensual": 2000000,
        }

        self.audit_logger.log_calculation_start(
            session_id=self.session_id,
            input_data=input_data,
            params_version="2025-01-01",
        )

        log_files = list(Path(self.temp_dir).glob("*.log"))
        with open(log_files[0], "r", encoding="utf-8") as f:
            log_entry = json.loads(f.readlines()[0])

        assert log_entry["event_type"] == "calculation_started"
        assert "input_summary" in log_entry
        assert log_entry["input_summary"]["modo"] == "PERIÓDICA"
        assert "params_version" in log_entry

    def test_log_override(self):
        """Test registro de override."""
        self.audit_logger.log_override(
            session_id=self.session_id,
            operator_id="OP001",
            checks_overridden=["V001", "V002"],
            justification="Testing override",
        )

        log_files = list(Path(self.temp_dir).glob("*.log"))
        with open(log_files[0], "r", encoding="utf-8") as f:
            log_entry = json.loads(f.readlines()[0])

        assert log_entry["event_type"] == "override_applied"
        assert log_entry["operator_id"] == "OP001"
        assert log_entry["checks_overridden"] == ["V001", "V002"]
        assert log_entry["justification"] == "Testing override"

    def test_log_error(self):
        """Test registro de error."""
        self.audit_logger.log_error(
            session_id=self.session_id,
            error_type="ValidationError",
            error_message="Test error message",
            stack_trace="Traceback...\nError details",
        )

        log_files = list(Path(self.temp_dir).glob("*.log"))
        with open(log_files[0], "r", encoding="utf-8") as f:
            log_entry = json.loads(f.readlines()[0])

        assert log_entry["event_type"] == "error_occurred"
        assert log_entry["error_type"] == "ValidationError"
        assert log_entry["error_message"] == "Test error message"
        assert "stack_trace" in log_entry

    def test_get_session_logs(self):
        """Test obtención de logs por sesión."""
        # Crear múltiples logs
        for i in range(3):
            self.audit_logger.log_event(
                event_type=AuditEventType.CALCULATION_STARTED,
                session_id=f"session_{i}",
                message=f"Test message {i}",
            )

        session_logs = self.audit_logger.get_session_logs("session_1")

        assert len(session_logs) == 1
        assert session_logs[0]["session_id"] == "session_1"
        assert "Test message 1" in session_logs[0]["message"]

    def test_input_summarization(self):
        """Test de resumen seguro de input."""
        sensitive_input = {
            "nombre": "Juan Pérez",
            "documento": "123456789",
            "modo": "PERIÓDICA",
            "salario_mensual": 2000000,
            "operator_id": "OP001",
        }

        self.audit_logger.log_calculation_start(
            session_id=self.session_id,
            input_data=sensitive_input,
            params_version="2025-01-01",
        )

        log_files = list(Path(self.temp_dir).glob("*.log"))
        with open(log_files[0], "r", encoding="utf-8") as f:
            log_entry = json.loads(f.readlines()[0])

        summary = log_entry["input_summary"]

        # Verificar que datos sensibles fueron redactados
        assert summary["nombre"] == "***REDACTED***"
        assert summary["documento"] == "***REDACTED***"
        # Verificar que datos no sensibles se mantienen
        assert summary["modo"] == "PERIÓDICA"
