"""
Módulo de gestión de overrides humanos para el sistema de cumplimiento legal.
Permite bypass de validaciones críticas con registro de auditoría completo.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class OverrideRecord:
    """Registro de override humano para auditoría."""

    override_id: str
    timestamp: str
    operator_id: str
    justification: str
    compliance_checks_overridden: List[str]
    original_status: str
    new_status: str
    input_hash: str


class OverrideManager:
    """Gestor de autorizaciones de override humano."""

    def __init__(self):
        self.override_records: List[OverrideRecord] = []

    def validate_override_request(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida si una solicitud de override es válida.

        Args:
            input_data: Datos de entrada que pueden incluir override

        Returns:
            Dict con resultado de validación
        """
        result: Dict[str, Any] = {"is_valid": False, "errors": [], "warnings": []}

        # Verificar si se solicita override
        if not input_data.get("human_override", False):
            result["is_valid"] = False
            result["errors"].append("Override no solicitado")
            return result

        # Validar campos obligatorios
        required_fields = ["operator_id", "override_reason"]
        for field in required_fields:
            if not input_data.get(field):
                result["errors"].append(f"Campo requerido para override: {field}")

        # Validar formato de operator_id
        operator_id = input_data.get("operator_id")
        if operator_id and len(operator_id.strip()) < 3:
            result["errors"].append("operator_id debe tener al menos 3 caracteres")

        # Validar justificación
        justification = input_data.get("override_reason", "")
        if len(justification.strip()) < 10:
            result["warnings"].append(
                "Justificación muy corta, considere proporcionar más detalles"
            )

        result["is_valid"] = len(result["errors"]) == 0
        return result

    def create_override_record(
        self,
        operator_id: str,
        justification: str,
        checks_overridden: List[str],
        original_status: str,
        input_hash: str,
    ) -> OverrideRecord:
        """
        Crea un registro de override para auditoría.

        Args:
            operator_id: Identificador del operador
            justification: Justificación del override
            checks_overridden: Lista de checks sobre los que se aplica override
            original_status: Estado original de compliance
            input_hash: Hash del input para trazabilidad

        Returns:
            OverrideRecord creado
        """
        override_record = OverrideRecord(
            override_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            operator_id=operator_id,
            justification=justification,
            compliance_checks_overridden=checks_overridden,
            original_status=original_status,
            new_status="OVERRIDE_APPROVED",
            input_hash=input_hash,
        )

        self.override_records.append(override_record)
        return override_record

    def apply_override_to_compliance_report(
        self, compliance_report: Dict[str, Any], override_record: OverrideRecord
    ) -> Dict[str, Any]:
        """
        Aplica override al reporte de cumplimiento.

        Args:
            compliance_report: Reporte original de cumplimiento
            override_record: Registro de override aplicado

        Returns:
            Reporte de cumplimiento actualizado
        """
        # Crear copia del reporte
        updated_report = compliance_report.copy()

        # Actualizar estado general
        updated_report["compliance_status"] = "OVERRIDE_APPROVED"

        # Agregar sección de override
        updated_report["override_action"] = {
            "action": "human_override",
            "timestamp": override_record.timestamp,
            "operator_id": override_record.operator_id,
            "justification": override_record.justification,
            "override_id": override_record.override_id,
            "checks_overridden": override_record.compliance_checks_overridden,
        }

        # Actualizar checks individuales
        for check in updated_report.get("checks", []):
            if check["id"] in override_record.compliance_checks_overridden:
                check["result"] = "OVERRIDDEN"
                check["override_applied"] = True
                check["override_operator"] = override_record.operator_id
                check["override_timestamp"] = override_record.timestamp

        return updated_report

    def get_override_history(
        self, operator_id: Optional[str] = None, date_range: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene historial de overrides con filtros opcionales.

        Args:
            operator_id: Filtrar por operador específico
            date_range: Tupla (start_date, end_date) para filtrar por fecha

        Returns:
            Lista de registros de override
        """
        filtered_records = self.override_records

        if operator_id:
            filtered_records = [
                r for r in filtered_records if r.operator_id == operator_id
            ]

        if date_range:
            start_date, end_date = date_range
            filtered_records = [
                r for r in filtered_records if start_date <= r.timestamp <= end_date
            ]

        return [asdict(record) for record in filtered_records]

    def generate_override_report(self) -> Dict[str, Any]:
        """
        Genera reporte estadístico de overrides.

        Returns:
            Dict con estadísticas de overrides
        """
        if not self.override_records:
            return {"total_overrides": 0}

        # Estadísticas por operador
        operator_stats = {}
        for record in self.override_records:
            op_id = record.operator_id
            if op_id not in operator_stats:
                operator_stats[op_id] = 0
            operator_stats[op_id] += 1

        # Estadísticas por tipo de check
        check_stats = {}
        for record in self.override_records:
            for check_id in record.compliance_checks_overridden:
                if check_id not in check_stats:
                    check_stats[check_id] = 0
                check_stats[check_id] += 1

        return {
            "total_overrides": len(self.override_records),
            "date_range": {
                "first_override": min(r.timestamp for r in self.override_records),
                "last_override": max(r.timestamp for r in self.override_records),
            },
            "operator_statistics": operator_stats,
            "check_statistics": check_stats,
            "most_overridden_checks": sorted(
                check_stats.items(), key=lambda x: x[1], reverse=True
            )[:5],
        }
