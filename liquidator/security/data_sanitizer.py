"""
Data Sanitizer - Cleans and sanitizes data to prevent security issues.
Handles sensitive data masking and secure data handling.
"""

import re
import json
import base64
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DataSanitizer:
    """Sanitizes and masks sensitive data."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.sensitive_fields = [
            'contraseña', 'password', 'clave', 'secret', 'token', 'key',
            'documento_trabajador', 'cedula', 'identificacion',
            'telefono', 'celular', 'email',
            'cuenta_bancaria', 'cuenta', 'iban', 'swift'
        ]
        self.mask_char = '*'
        self.mask_length = 4
        self.sanitize_chars = ['<', '>', '&', '"', "'", '\\', '/', '\n', '\r', '\t']
        
    def sanitize_string(self, text: str) -> str:
        """Sanitize string by removing dangerous characters."""
        if not isinstance(text, str):
            return str(text)
            
        # Remove or replace dangerous characters
        sanitized = text
        for char in self.sanitize_chars:
            if char in ['\n', '\r', '\t']:
                sanitized = sanitized.replace(char, ' ')
            else:
                sanitized = sanitized.replace(char, '')
                
        # Remove extra whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        return sanitized
        
    def mask_sensitive_field(self, field_name: str, value: Union[str, int, float]) -> str:
        """Mask sensitive field values for logging/output."""
        if not isinstance(value, (str, int, float)):
            return str(value)
            
        field_name_lower = field_name.lower()
        
        # Check if field should be masked
        is_sensitive = any(sensitive in field_name_lower for sensitive in self.sensitive_fields)
        
        if not is_sensitive:
            return str(value)
            
        value_str = str(value)
        if len(value_str) <= self.mask_length:
            return self.mask_char * len(value_str)
            
        # Mask middle part, keep first and last characters
        keep_start = min(2, len(value_str) // 4)
        keep_end = min(2, len(value_str) // 4)
        mask_count = len(value_str) - keep_start - keep_end
        
        return (value_str[:keep_start] + 
                self.mask_char * mask_count + 
                value_str[-keep_end:])
                
    def mask_document_id(self, document_id: str) -> str:
        """Specialized masking for document IDs (Cédula, NIT, etc.)."""
        if len(document_id) <= 4:
            return self.mask_char * len(document_id)
        return document_id[:2] + self.mask_char * (len(document_id) - 4) + document_id[-2:]
        
    def mask_phone_number(self, phone: str) -> str:
        """Mask phone numbers appropriately."""
        phone_clean = re.sub(r'[^\d]', '', str(phone))
        if len(phone_clean) <= 4:
            return self.mask_char * len(phone_clean)
        return phone_clean[:3] + self.mask_char * (len(phone_clean) - 6) + phone_clean[-3:]
        
    def mask_email(self, email: str) -> str:
        """Mask email addresses."""
        if '@' not in str(email):
            return self.mask_char * len(str(email))
            
        local, domain = str(email).split('@', 1)
        if len(local) <= 2:
            local_masked = self.mask_char * len(local)
        else:
            local_masked = local[0] + self.mask_char * (len(local) - 2) + local[-1]
            
        return f"{local_masked}@{domain}"
        
    def mask_bank_account(self, account: str) -> str:
        """Mask bank account numbers."""
        account_clean = re.sub(r'[^\d]', '', str(account))
        if len(account_clean) <= 4:
            return self.mask_char * len(account_clean)
        return account_clean[:2] + self.mask_char * (len(account_clean) - 4) + account_clean[-2:]
        
    def sanitize_json_for_logging(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a sanitized version of JSON data suitable for logging."""
        if not isinstance(data, dict):
            return {'data': str(data)}
            
        sanitized_data = {}
        
        for key, value in data.items():
            if isinstance(value, dict):
                sanitized_data[key] = self.sanitize_json_for_logging(value)
            elif isinstance(value, list):
                sanitized_data[key] = [
                    self.sanitize_json_for_logging(item) if isinstance(item, dict) 
                    else str(item)[:100]  # Truncate long strings
                    for item in value
                ]
            else:
                # Apply appropriate masking
                key_lower = key.lower()
                if 'document' in key_lower or 'cedula' in key_lower:
                    sanitized_data[key] = self.mask_document_id(str(value))
                elif 'telefono' in key_lower or 'celular' in key_lower:
                    sanitized_data[key] = self.mask_phone_number(str(value))
                elif 'email' in key_lower:
                    sanitized_data[key] = self.mask_email(str(value))
                elif 'cuenta' in key_lower or 'account' in key_lower:
                    sanitized_data[key] = self.mask_bank_account(str(value))
                else:
                    sanitized_data[key] = self.mask_sensitive_field(key, value)
                    
        return sanitized_data
        
    def remove_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data entirely (not just masking)."""
        if not isinstance(data, dict):
            return data
            
        clean_data = {}
        
        for key, value in data.items():
            key_lower = key.lower()
            
            # Check if this is a sensitive field to remove
            if any(sensitive in key_lower for sensitive in self.sensitive_fields):
                clean_data[key] = '[REDACTED]'
            elif isinstance(value, dict):
                clean_data[key] = self.remove_sensitive_data(value)
            elif isinstance(value, list):
                clean_data[key] = [
                    self.remove_sensitive_data(item) if isinstance(item, dict) 
                    else '[REDACTED]' if any(sensitive in str(item).lower() for sensitive in self.sensitive_fields)
                    else item
                    for item in value
                ]
            else:
                clean_data[key] = value
                
        return clean_data
        
    def sanitize_filename_input(self, filename: str) -> str:
        """Sanitize user-provided filename for security."""
        if not isinstance(filename, str):
            return 'unknown'
            
        # Remove path traversal attempts
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')
        
        # Remove dangerous characters
        filename = re.sub(r'[<>"|:*\?]', '_', filename)
        
        # Remove any null bytes
        filename = filename.replace('\x00', '')
        
        # Limit length
        if len(filename) > 100:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:100-len(ext)-1] + ('.' + ext if ext else '')
            
        return filename
        
    def sanitize_output_text(self, text: str) -> str:
        """Sanitize text output to prevent injection."""
        if not isinstance(text, str):
            return str(text)
            
        # Escape HTML entities
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#x27;')
        
        return text
        
    def create_secure_hash_data(self, data: Dict[str, Any]) -> str:
        """Create hash data excluding sensitive information."""
        # Remove sensitive data before hashing
        clean_data = self.remove_sensitive_data(data)
        
        # Sort keys for consistent hashing
        json_str = json.dumps(clean_data, sort_keys=True, separators=(',', ':'))
        
        # Return base64 encoded representation
        return base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        
    def validate_and_sanitize_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize input data comprehensively."""
        if not isinstance(input_data, dict):
            raise ValueError("Input must be a dictionary")
            
        sanitized = {}
        
        for key, value in input_data.items():
            key_sanitized = self.sanitize_string(key)
            
            if isinstance(value, str):
                sanitized[key_sanitized] = self.sanitize_string(value)
            elif isinstance(value, (int, float, bool)):
                sanitized[key_sanitized] = value
            elif isinstance(value, dict):
                sanitized[key_sanitized] = self.validate_and_sanitize_input(value)
            elif isinstance(value, list):
                sanitized[key_sanitized] = [
                    self.sanitize_string(str(item)) if isinstance(item, str)
                    else self.validate_and_sanitize_input(item) if isinstance(item, dict)
                    else str(item)
                    for item in value
                ]
            else:
                sanitized[key_sanitized] = str(value)
                
        return sanitized
        
    def create_audit_safe_copy(self, original_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create audit-safe copy of data with sensitive information masked."""
        audit_copy = json.loads(json.dumps(original_data))  # Deep copy
        
        # Apply masking to sensitive fields
        audit_copy = self.sanitize_json_for_logging(audit_copy)
        
        # Add metadata about sanitization
        audit_copy['_sanitization_info'] = {
            'sanitized': True,
            'sensitive_fields_masked': len([k for k in original_data.keys() 
                                          if any(sens in k.lower() for sens in self.sensitive_fields)]),
            'timestamp': json.dumps({"timestamp": "REPLACED_IN_LOGGING"})  # Placeholder
        }
        
        return audit_copy
