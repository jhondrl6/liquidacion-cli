"""
Sistema de logging de auditoría para trazabilidad completa de ejecuciones.
"""

import json
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class AuditEventType(Enum):
    """Tipos de eventos de auditoría."""

    CALCULATION_STARTED = "calculation_started"
    CALCULATION_COMPLETED = "calculation_completed"
    COMPLIANCE_CHECK_STARTED = "compliance_check_started"
    COMPLIANCE_CHECK_COMPLETED = "compliance_check_completed"
    OVERRIDE_APPLIED = "override_applied"
    ERROR_OCCURRED = "error_occurred"
    OUTPUT_GENERATED = "output_generated"


class AuditLogger:
    """Logger estructurado para auditoría del sistema."""

    def __init__(self, log_directory: str = "audit/logs"):
        """
        Inicializa el logger de auditoría.

        Args:
            log_directory: Directorio donde se guardarán los logs
        """
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)

        # Configurar logging estructurado
        self.setup_structured_logging()

    def setup_structured_logging(self):
        """Configura el sistema de logging estructurado."""
        # Crear logger principal
        self.logger = logging.getLogger("liquidator_audit")
        self.logger.setLevel(logging.INFO)

        # Evitar propagación al root logger
        self.logger.propagate = False

        # Formato estructurado JSON
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "level": record.levelname,
                    "session_id": getattr(record, "session_id", "unknown"),
                    "event_type": getattr(record, "event_type", "unknown"),
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                }

                # Agregar campos adicionales si existen
                extra_data = getattr(record, "extra_data", {})
                log_entry.update(extra_data)

                return json.dumps(log_entry, ensure_ascii=False)

        # Handler para archivo
        log_file = self.log_directory / f"audit_{datetime.now().strftime('%Y%m')}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(JSONFormatter())

        self.logger.addHandler(file_handler)

    def log_event(
        self,
        event_type: AuditEventType,
        session_id: str,
        message: str,
        extra_data: dict[str, Any] | None = None,
    ):
        """
        Registra un evento de auditoría.

        Args:
            event_type: Tipo de evento
            session_id: ID de la sesión
            message: Mensaje descriptivo
            extra_data: Datos adicionales para el log
        """
        log_data = {
            "session_id": session_id,
            "event_type": event_type.value,
            "extra_data": extra_data or {},
        }

        # Nivel de log según tipo de evento
        if event_type in [AuditEventType.ERROR_OCCURRED]:
            log_level = logging.ERROR
        elif event_type in [AuditEventType.OVERRIDE_APPLIED]:
            log_level = logging.WARNING
        else:
            log_level = logging.INFO

        self.logger.log(log_level, message, extra=log_data)

    def log_calculation_start(
        self, session_id: str, input_data: dict[str, Any], params_version: str
    ):
        """Registra inicio de cálculo."""
        self.log_event(
            AuditEventType.CALCULATION_STARTED,
            session_id,
            "Inicio de cálculo de liquidación",
            {
                "input_summary": self._summarize_input(input_data),
                "params_version": params_version,
                "timestamp_start": datetime.now().isoformat(),
            },
        )

    def log_calculation_complete(
        self,
        session_id: str,
        output_hash: str,
        compliance_status: str,
        duration_seconds: float,
    ):
        """Registra finalización de cálculo."""
        self.log_event(
            AuditEventType.CALCULATION_COMPLETED,
            session_id,
            "Cálculo de liquidación completado",
            {
                "output_hash": output_hash,
                "compliance_status": compliance_status,
                "duration_seconds": duration_seconds,
                "timestamp_end": datetime.now().isoformat(),
            },
        )

    def log_override(
        self,
        session_id: str,
        operator_id: str,
        checks_overridden: list[str],
        justification: str,
    ):
        """Registra aplicación de override."""
        self.log_event(
            AuditEventType.OVERRIDE_APPLIED,
            session_id,
            "Override humano aplicado",
            {
                "operator_id": operator_id,
                "checks_overridden": checks_overridden,
                "justification": justification,
                "override_timestamp": datetime.now().isoformat(),
            },
        )

    def log_error(
        self,
        session_id: str,
        error_type: str,
        error_message: str,
        stack_trace: str | None = None,
    ):
        """Registra error en el sistema."""
        self.log_event(
            AuditEventType.ERROR_OCCURRED,
            session_id,
            f"Error en ejecución: {error_type}",
            {
                "error_type": error_type,
                "error_message": error_message,
                "stack_trace": stack_trace,
            },
        )

    def _summarize_input(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Crea resumen seguro del input para logging."""
        summary = {
            "modo": input_data.get("modo"),
            "fecha_ingreso": input_data.get("fecha_ingreso"),
            "fecha_corte": input_data.get("fecha_corte"),
            "tipo_contrato": input_data.get("tipo_contrato"),
            "reside_en_lugar_trabajo": input_data.get("reside_en_lugar_trabajo"),
            "enforce_compliance": input_data.get("enforce_compliance"),
            "human_override": input_data.get("human_override"),
        }

        # Excluir datos sensibles
        sensitive_fields = ["nombre", "documento", "operator_id"]
        for field in sensitive_fields:
            if field in input_data:
                summary[field] = "***REDACTED***"

        return summary

    def get_session_logs(self, session_id: str) -> list[dict[str, Any]]:
        """
        Obtiene todos los logs de una sesión específica.

        Args:
            session_id: ID de la sesión

        Returns:
            Lista de logs de la sesión
        """
        session_logs = []

        # Buscar en todos los archivos de log del mes actual
        log_file = self.log_directory / f"audit_{datetime.now().strftime('%Y%m')}.log"

        if log_file.exists():
            with open(log_file, encoding="utf-8") as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        if log_entry.get("session_id") == session_id:
                            session_logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue

        return sorted(session_logs, key=lambda x: x["timestamp"])
