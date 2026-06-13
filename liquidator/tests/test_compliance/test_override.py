"""
Tests para el módulo de override manager.
"""

import datetime

import pytest

from liquidator.compliance.override_manager import OverrideManager, OverrideRecord


class TestOverrideManager:
    """Tests para OverrideManager."""

    def setup_method(self):
        """Configuración antes de cada test."""
        self.override_manager = OverrideManager()
        self.valid_override_data = {
            "human_override": True,
            "operator_id": "OP001",
            "override_reason": "Justificación válida para testing con más de 10 caracteres",
        }

    def test_validate_override_request_valid(self):
        """Test validación de override request válido."""
        result = self.override_manager.validate_override_request(
            self.valid_override_data
        )

        assert result["is_valid"] == True
        assert len(result["errors"]) == 0

    def test_validate_override_request_missing_fields(self):
        """Test validación con campos faltantes."""
        invalid_data = {"human_override": True}
        result = self.override_manager.validate_override_request(invalid_data)

        assert result["is_valid"] == False
        assert "operator_id" in str(result["errors"])
        assert "override_reason" in str(result["errors"])

    def test_validate_override_request_short_justification(self):
        """Test validación con justificación muy corta."""
        data = self.valid_override_data.copy()
        data["override_reason"] = "Corto"
        result = self.override_manager.validate_override_request(data)

        assert result["is_valid"] == True  # Solo warning, no error
        assert len(result["warnings"]) > 0

    def test_create_override_record(self):
        """Test creación de registro de override."""
        checks_overridden = ["V001", "V002"]
        original_status = "NO_GO"
        input_hash = "sha256:test123"

        record = self.override_manager.create_override_record(
            operator_id="OP001",
            justification="Testing override",
            checks_overridden=checks_overridden,
            original_status=original_status,
            input_hash=input_hash,
        )

        assert record.operator_id == "OP001"
        assert record.justification == "Testing override"
        assert record.compliance_checks_overridden == checks_overridden
        assert record.original_status == original_status
        assert record.input_hash == input_hash
        assert record.override_id is not None
        assert record.timestamp is not None

    def test_apply_override_to_compliance_report(self):
        """Test aplicación de override a reporte de cumplimiento."""
        compliance_report = {
            "compliance_status": "NO_GO",
            "checks": [
                {"id": "V001", "result": "FAIL", "description": "Test check 1"},
                {"id": "V002", "result": "FAIL", "description": "Test check 2"},
            ],
        }

        override_record = OverrideRecord(
            override_id="test_override_001",
            timestamp=datetime.now().isoformat(),
            operator_id="OP001",
            justification="Testing",
            compliance_checks_overridden=["V001"],
            original_status="NO_GO",
            new_status="OVERRIDE_APPROVED",
            input_hash="sha256:test",
        )

        updated_report = self.override_manager.apply_override_to_compliance_report(
            compliance_report, override_record
        )

        assert updated_report["compliance_status"] == "OVERRIDE_APPROVED"
        assert "override_action" in updated_report

        # Verificar que el check V001 fue marcado como overriden
        v001_check = next(c for c in updated_report["checks"] if c["id"] == "V001")
        assert v001_check["result"] == "OVERRIDDEN"
        assert v001_check["override_applied"] == True

    def test_get_override_history(self):
        """Test obtención de historial de overrides."""
        # Crear algunos registros de prueba
        self.override_manager.create_override_record(
            operator_id="OP001",
            justification="Test 1",
            checks_overridden=["V001"],
            original_status="NO_GO",
            input_hash="sha256:test1",
        )

        self.override_manager.create_override_record(
            operator_id="OP002",
            justification="Test 2",
            checks_overridden=["V002"],
            original_status="NO_GO",
            input_hash="sha256:test2",
        )

        # Filtrar por operador
        op001_history = self.override_manager.get_override_history(operator_id="OP001")
        assert len(op001_history) == 1
        assert op001_history[0]["operator_id"] == "OP001"

    def test_generate_override_report(self):
        """Test generación de reporte de overrides."""
        # Crear registros de prueba
        for i in range(3):
            self.override_manager.create_override_record(
                operator_id=f"OP00{i+1}",
                justification=f"Test {i+1}",
                checks_overridden=[f"V00{i+1}"],
                original_status="NO_GO",
                input_hash=f"sha256:test{i+1}",
            )

        report = self.override_manager.generate_override_report()

        assert report["total_overrides"] == 3
        assert "operator_statistics" in report
        assert "check_statistics" in report
        assert "most_overridden_checks" in report
