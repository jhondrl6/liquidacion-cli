"""
Enhanced Input Validator - Security-focused validation and sanitization.
Protects against injection, data exfiltration, and malformed inputs.
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class InputValidationError(Exception):
    """Raised when input validation fails."""
    pass


class InputValidator:
    """Enhanced security-focused input validator."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.max_input_size = self.config.get('max_input_size_bytes', 1024 * 1024)  # 1MB
        self.max_string_length = self.config.get('max_string_length', 1000)
        self.blocked_patterns = self._load_blocked_patterns()
        self.allowed_file_extensions = {'.json', '.yaml', '.yml', '.md'}
        
    def _load_blocked_patterns(self) -> List[re.Pattern]:
        """Load regex patterns for blocking malicious inputs."""
        patterns = [
            # SQL injection patterns
            re.compile(r"('|(\\')|(;|(\s+(select|insert|update|delete|drop|create|alter)))|(union|exec|script))", re.IGNORECASE),
            # Script injection patterns
            re.compile(r"(<script|</script|javascript:|vbscript:|onload=|onerror=)", re.IGNORECASE),
            # Command injection patterns
            re.compile(r"(\|\||&&|;|[`'\"]|\$\(|\${|\(\())"),
            # Path traversal patterns
            re.compile(r"(\.\./|\.\.\|\\|\.\./\.\./)"),
            # Null bytes and control characters
            re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]"),
            # XML/XSS patterns
            re.compile(r"<!DOCTYPE|<!ENTITY|CDATA)")
        ]
        return patterns
        
    def validate_input_size(self, data: Any) -> None:
        """Validate input size to prevent DoS attacks."""
        if isinstance(data, str):
            if len(data.encode('utf-8')) > self.max_input_size:
                raise InputValidationError(f"Input size exceeds maximum allowed: {self.max_input_size} bytes")
        elif isinstance(data, dict):
            if len(json.dumps(data).encode('utf-8')) > self.max_input_size:
                raise InputValidationError(f"Input size exceeds maximum allowed: {self.max_input_size} bytes")
                
    def validate_string_length(self, value: str, field_name: str = "field") -> None:
        """Validate string length to prevent buffer overflow."""
        if len(value) > self.max_string_length:
            raise InputValidationError(f"Field '{field_name}' exceeds maximum length of {self.max_string_length} characters")
            
    def check_blocked_patterns(self, value: str, field_name: str = "field") -> None:
        """Check for malicious patterns in input."""
        for pattern in self.blocked_patterns:
            if pattern.search(value):
                raise InputValidationError(f"Field '{field_name}' contains potentially malicious content")
                
    def validate_file_path(self, file_path: str) -> None:
        """Validate file path to prevent path traversal attacks."""
        try:
            # Normalize path and resolve
            path_obj = Path(file_path).resolve()
            if '..' in str(path_obj):
                raise InputValidationError("Path traversal attempt detected")
                
            # Check if path is within allowed directories
            allowed_dirs = ['params/', 'config/', 'templates/', 'audit/', 'output/', 'examples/']
            is_allowed = any(str(path_obj).startswith(allowed_dir) or 
                            str(path_obj).startswith('/' + allowed_dir) 
                            for allowed_dir in allowed_dirs)
            
            if not is_allowed and not str(path_obj).startswith('/tmp'):  # Allow temp directory
                raise InputValidationError(f"File path '{file_path}' is not in allowed directories")
                
            # Check file extension
            if not path_obj.suffix.lower() in self.allowed_file_extensions:
                raise InputValidationError(f"File extension '{path_obj.suffix}' is not allowed")
                
        except Exception as e:
            if isinstance(e, InputValidationError):
                raise
            raise InputValidationError(f"Invalid file path: {file_path}")
            
    def validate_date_format(self, date_str: str, field_name: str = "date") -> None:
        """Validate date format and range."""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Check reasonable date range (1900-2100)
            if date_obj.year < 1900 or date_obj.year > 2100:
                raise InputValidationError(f"Date '{date_str}' is outside valid range")
                
            # Check date is not too far in the future
            if date_obj > datetime.now() + timedelta(days=365):
                raise InputValidationError(f"Date '{date_str}' is too far in the future")
                
        except ValueError:
            raise InputValidationError(f"Invalid date format for '{field_name}': {date_str}")
            
    def validate_salary_amount(self, amount: int, field_name: str = "salary") -> None:
        """Validate salary amount for reasonableness."""
        if not isinstance(amount, (int, float)):
            raise InputValidationError(f"{field_name} must be a number")
            
        if amount < 0:
            raise InputValidationError(f"{field_name} cannot be negative")
            
        # Maximum salary limit (100 million COP)
        if amount > 100_000_000:
            raise InputValidationError(f"{field_name} exceeds reasonable maximum")
            
        # Check for suspicious decimal places
        if isinstance(amount, float):
            decimal_places = len(str(amount).split('.')[-1])
            if decimal_places > 2:
                raise InputValidationError(f"{field_name} has too many decimal places")
                
    def validate_id_numbers(self, document_id: str) -> None:
        """Validate document ID format."""
        # Remove common formatting
        clean_id = re.sub(r'[\s.-]', '', document_id)
        
        # Check length (Colombian IDs are 7-10 digits for cédula)
        if not (7 <= len(clean_id) <= 10):
            raise InputValidationError("Document ID length is invalid")
            
        # Check all digits
        if not clean_id.isdigit():
            raise InputValidationError("Document ID must contain only numbers")
            
    def validate_contract_type(self, contract_type: str) -> None:
        """Validate contract type enum."""
        valid_types = ['indefinido', 'fijo', 'obraLabor', 'tiempoDefinido', 'aprendizaje', 'prestacionServicios']
        if contract_type not in valid_types:
            raise InputValidationError(f"Invalid contract type: {contract_type}")
            
    def validate_settlement_mode(self, mode: str) -> None:
        """Validate settlement mode."""
        valid_modes = ['PERIODICA', 'FINIQUITO']
        if mode not in valid_modes:
            raise InputValidationError(f"Invalid settlement mode: {mode}")
            
    def validate_json_data(self, json_data: Any) -> Dict[str, Any]:
        """Comprehensive validation of JSON input data."""
        if not isinstance(json_data, dict):
            raise InputValidationError("Input must be a JSON object")
            
        self.validate_input_size(json_data)
        
        validated_data = {}
        
        # Validate required fields
        required_fields = ['modo', 'fecha_ingreso', 'fecha_corte', 'salario_mensual']
        for field in required_fields:
            if field not in json_data:
                raise InputValidationError(f"Missing required field: {field}")
                
            if json_data[field] is None or json_data[field] == "":
                raise InputValidationError(f"Field '{field}' cannot be empty")
                
        # Validate each field
        validated_data['modo'] = self._validate_field(json_data.get('modo'), 'modo', self.validate_settlement_mode)
        validated_data['fecha_ingreso'] = self._validate_field(json_data.get('fecha_ingreso'), 'fecha_ingreso', self.validate_date_format)
        validated_data['fecha_corte'] = self._validate_field(json_data.get('fecha_corte'), 'fecha_corte', self.validate_date_format)
        validated_data['salario_mensual'] = self._validate_field(json_data.get('salario_mensual'), 'salario_mensual', lambda x: self.validate_salary_amount(int(x)))
        
        # Validate optional fields
        optional_fields = {
            'comisiones_promedio_mensual': lambda x: self.validate_salary_amount(float(x)),
            'horas_extras_promedio_mensual': lambda x: self.validate_salary_amount(float(x)),
            'bonificaciones_promedio_mensual': lambda x: self.validate_salary_amount(float(x)),
            'auxilio_conectividad': lambda x: self.validate_salary_amount(int(x)),
            'dias_vacaciones_pendientes': lambda x: self._validate_positive_integer(x),
            'tipo_contrato': self.validate_contract_type,
            'reside_en_lugar_trabajo': lambda x: self._validate_boolean(x),
            'nombre_trabajador': lambda x: self.validate_string_length(str(x), 'nombre_trabajador'),
            'documento_trabajador': self.validate_id_numbers
        }
        
        for field, validator in optional_fields.items():
            if field in json_data and json_data[field] is not None:
                validated_data[field] = self._validate_field(json_data[field], field, validator)
                
        # Validate date consistency
        self._validate_date_consistency(validated_data['fecha_ingreso'], validated_data['fecha_corte'])
        
        return validated_data
        
    def _validate_field(self, value: Any, field_name: str, validator_func) -> Any:
        """Helper method to validate individual fields."""
        try:
            if isinstance(value, str):
                self.validate_string_length(value, field_name)
                self.check_blocked_patterns(value, field_name)
            validator_func(value)
            return value
        except Exception as e:
            if isinstance(e, InputValidationError):
                raise
            raise InputValidationError(f"Validation error for field '{field_name}': {e}")
            
    def _validate_positive_integer(self, value: Any) -> int:
        """Validate positive integer."""
        try:
            int_value = int(value)
            if int_value < 0:
                raise InputValidationError("Value must be non-negative")
            return int_value
        except (ValueError, TypeError):
            raise InputValidationError("Value must be a valid number")
            
    def _validate_boolean(self, value: Any) -> bool:
        """Validate boolean value."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes']
        if isinstance(value, (int, float)):
            return bool(value)
        raise InputValidationError("Value must be a boolean")
        
    def _validate_date_consistency(self, fecha_ingreso: str, fecha_corte: str) -> None:
        """Validate that dates make sense."""
        fecha_ingreso_dt = datetime.strptime(fecha_ingreso, '%Y-%m-%d')
        fecha_corte_dt = datetime.strptime(fecha_corte, '%Y-%m-%d')
        
        if fecha_ingreso_dt >= fecha_corte_dt:
            raise InputValidationError("Fecha de corte debe ser posterior a fecha de ingreso")
            
        # Check reasonable employment duration (max 50 years)
        if (fecha_corte_dt - fecha_ingreso_dt).days > 50 * 365:
            raise InputValidationError("Employment duration exceeds reasonable maximum")
            
    def validate_for_injection(self, input_str: str) -> bool:
        """Check if string contains injection patterns."""
        injection_patterns = [
            r"[;'\"]",           # SQL injection separators
            r"<script.*?/script>", # Script tags
            r"javascript:|vbscript:",  # Script protocols
            r"on\w+="             # Event handlers
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                return True
        return False
        
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for security."""
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Remove any leading dots or dashes
        sanitized = re.sub(r'^[.-]+', '', sanitized)
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:255-len(ext)] + ext
            
        return sanitized
