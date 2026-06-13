import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from uuid import uuid4


class AuditTrail:
    """Represents a complete audit trail entry."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.timestamp = datetime.now().isoformat()
        self.input_data = None
        self.output_data = None
        self.compliance_report = None
        self.version_info = None


class TrailGenerator:
    """Generates and manages audit trails for liquidation calculations."""

    def __init__(self, trail_directory: str = "audit/trails"):
        self.trail_directory = Path(trail_directory)
        self.trail_directory.mkdir(parents=True, exist_ok=True)

    def create_audit_trail(
        self, session_id: str, input_data: Dict[str, Any]
    ) -> AuditTrail:
        """Create a new audit trail."""
        trail = AuditTrail(session_id)
        trail.input_data = input_data
        return trail

    def complete_audit_trail(
        self,
        trail: AuditTrail,
        output_data: Dict[str, Any],
        compliance_report: Dict[str, Any],
    ) -> None:
        """Complete an audit trail with execution results."""
        trail.output_data = output_data
        trail.compliance_report = compliance_report
        trail.version_info = {
            "params_version": "2025-10-31",
            "generator_version": "1.0.0",
        }

    def save_audit_trail(self, trail: AuditTrail) -> str:
        """Save audit trail to file and return filepath."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audit_trail_{trail.session_id}_{timestamp}.json"
        filepath = self.trail_directory / filename

        trail_data = {
            "session_id": trail.session_id,
            "timestamp": trail.timestamp,
            "input_data": trail.input_data,
            "output_data": trail.output_data,
            "compliance_report": trail.compliance_report,
            "version_info": trail.version_info,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(trail_data, f, indent=2, ensure_ascii=False, sort_keys=True)

        return str(filepath)

    def generate_and_save_trail(
        self,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        compliance_report: Dict[str, Any],
    ) -> str:
        """Full pipeline: create, complete and save audit trail."""
        session_id = str(uuid4())
        trail = self.create_audit_trail(session_id, input_data)
        self.complete_audit_trail(trail, output_data, compliance_report)
        return self.save_audit_trail(trail)
