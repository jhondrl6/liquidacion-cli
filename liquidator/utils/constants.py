"""
Constants and default values for the liquidation system.
Centralized to avoid hardcoded values throughout the codebase.
"""

# Legal constants for 2025
DEFAULT_SMMLV = 1423500
DEFAULT_AUXILIO_TRANS = 200000
DEFAULT_TOPE_INDEMNIZACION_SMMLV = 20
DEFAULT_TASA_INTERESES_CESANTIAS = 0.12
DEFAULT_DIAS_BASE = 360
DEFAULT_DIAS_BASE_VACACIONES = 720

# File path constants
PARAMS_FILE_2025 = "params/2025.json"

# Error messages
ERROR_MSG_PARAMS_MISSING = "Parámetros legales no disponibles"
ERROR_MSG_INVALID_DATE = "Formato de fecha inválido. Use YYYY-MM-DD"

# Compliance constants
COMPLIANCE_POLICY_STANDARD = "standard"
COMPLIANCE_POLICY_STRICT = "strict"
COMPLIANCE_POLICY_LENIENT = "lenient"

# Validation constants
MAX_LINE_LENGTH = 79
MAX_FUNCTION_LENGTH = 30
MAX_PARAMS_COUNT = 5
