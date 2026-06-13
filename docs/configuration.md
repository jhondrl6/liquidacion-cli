# Documentación de Configuración
## Sistema de Liquidación de Nómina Colombia 2025

### Versión: 1.0.0
### Fecha: 2025-11-04

---

## Tabla de Contenidos

1. [Configuración General del Sistema](#1-configuración-general-del-sistema)
2. [Políticas de Cumplimiento Legal](#2-políticas-de-cumplimiento-legal)
3. [Configuración de Logging](#3-configuración-de-logging)
4. [Configuración de Performance](#4-configuración-de-performance)
5. [Configuración de Seguridad](#5-configuración-de-seguridad)
6. [Configuración de Integración](#6-configuración-de-integración)
7. [Configuración de Monitorización](#7-configuración-de-monitorización)
8. [Variables de Entorno](#8-variables-de-entorno)
9. [Configuración por Entorno](#9-configuración-por-entorno)
10. [Troubleshooting de Configuración](#10-troubleshooting-de-configuración)

---

## 1. Configuración General del Sistema

### 1.1 Archivo de Configuración Principal

El sistema utiliza `config/default_config.yaml` como configuración principal:

```yaml
# config/default_config.yaml
system:
  version: "1.0.0"
  environment: "production"
  timezone: "America/Bogota"
  encoding: "UTF-8"
  
params:
  year: 2025
  auto_update: false
  backup_previous_versions: true
  
compliance:
  enforce_by_default: true
  default_policy: "standard"
  allow_overrides: true
```

### 1.2 Estructura de Configuración

#### Componentes Principales
- **system**: Configuración básica del sistema y runtime
- **params**: Gestión de parámetros legales y normatividad
- **compliance**: Configuración del motor de cumplimiento legal
- **output**: Formatos y configuración de documentos generados
- **audit**: Trazabilidad y auditoría de ejecuciones
- **logging**: Configuración de logs y monitoreo
- **performance**: Optimización y caching
- **security**: Seguridad y validaciones
- **integration**: Conexiones con sistemas externos

### 1.3 Carga de Configuración

El sistema carga la configuración con el siguiente orden de precedencia:

1. **Variables de entorno** (mayor prioridad)
2. **Archivo YAML del entorno actual** (`config/{environment}.yaml`)
3. **Archivo YAML por defecto** (`config/default_config.yaml`)
4. **Valores hardcodeados** (menor prioridad)

#### Implementación de Carga
```python
# liquidator/utils/config_loader.py
class ConfigLoader:
    def __init__(self, environment: str = None):
        self.environment = environment or self._detect_environment()
        self.config = self._load_base_config()
        self._apply_environment_overrides()
        self._apply_environment_variables()
    
    def _detect_environment(self) -> str:
        """Detecta entorno actual"""
        env = os.getenv('LIQUIDACION_ENV', 'development')
        return env
    
    def _load_base_config(self) -> dict:
        """Carga configuración base desde YAML"""
        loader = yaml.SafeLoader
        with open('config/default_config.yaml', 'r', encoding='utf-8') as f:
            return yaml.load(f, Loader=loader)
    
    def _apply_environment_overrides(self):
        """Aplica overrides específicos del entorno"""
        env_file = f'config/{self.environment}.yaml'
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                env_config = yaml.safe_load(f)
                self._deep_update(self.config, env_config)
    
    def _apply_environment_variables(self):
        """Aplica variables de entorno como overrides"""
        env_mappings = {
            'LIQUIDACION_LOG_LEVEL': 'logging.level',
            'LIQUIDACION_AUDIT_PATH': 'audit.storage.base_path',
            'LIQUIDACION_COMPLIANCE_POLICY': 'compliance.default_policy'
        }
        
        for env_var, config_path in env_mappings.items():
            if env_var in os.environ:
                self._set_nested_value(self.config, config_path, os.getenv(env_var))
    
    def get(self, path: str, default=None):
        """Obtiene valor usando notación de punto (ej: 'system.version')"""
        return self._get_nested_value(self.config, path, default)
```

---

## 2. Políticas de Cumplimiento Legal

### 2.1 Visión General de Políticas (Compliance Policies)

El sistema implementa tres políticas de cumplimiento con diferentes niveles de restricción:

#### 2.1.1 Política Lenient (Permisiva)

**Uso recomendado:** Desarrollo, testing, escenarios de baja criticidad

**Características:**
- Acepta advertencias sin bloqueo
- No requiere aprobación overrides
- Permitiría continuar ejecución con validaciones no críticas

**Configuración:**
```yaml
complianse_policies:
  lenient:
    severity_levels:
      critical: { action: "BLOCK", requires_override: false }
      high: { action: "WARN", requires_override: false }
      medium: { action: "INFO", requires_override: false }
      low: { action: "IGNORE", requires_override: false }
```

**Ventajas:**
- Mayor operatividad
- Menos fricción en desarrollo
- Adecuado para pruebas internas

**Desventajas:**
- Riesgo legal para producción
- No recomendada para uso real
- Posible inconsistencia de resultados

#### 2.1.2 Política Standard (Estándar)

**Uso recomendado:** Producción estándar, balance compliance vs operatividad

**Características:**
- Bloquea fallos críticos y de alta severidad
- Permite advertencias de severidad media/baja pero registra
- Requiere aprobación para overrides importantes

**Configuración:**
```yaml
compliance_policies:
  standard:
    severity_levels:
      critical: { action: "BLOCK", requires_override: true }
      high: { action: "BLOCK", requires_override: true }
      medium: { action: "WARN", requires_override: false }
      low: { action: "WARN", requires_override: false }
```

**Ventajas:**
- Balance óptimo seguridad vs operatividad
- Aprobación legal estándar
- Manejo de edge cases razonable

**Desventajas:**
- Requiere procesamiento de overrides
- Mayor overhead administrativo

#### 2.1.3 Política Strict (Estricta)

**Uso recomendado:** Entornos regulados, alta criticidad, auditorías estrictas

**Características:**
- Bloquea cualquier desviación significativa
- Requiere aprobación múltiple y documentada
- Auditoría completa de cada paso

**Configuración:**
```yaml
compliance_policies:
  strict:
    severity_levels:
      critical: { action: "BLOCK", requires_override: true }
      high: { action: "BLOCK", requires_override: true }
      medium: { action: "BLOCK", requires_override: true }
      low: { action: "WARN", requires_override: false }
```

**Ventajas:**
- Máxima seguridad legal
- Aprobación para entornos regulados
- Cumplimiento exhaustivo

**Desventajas:**
- Alto overhead administrativo
- Potencialmente restrictivo
- Requiere personal senior para approvals

### 2.2 Mapeo de Reglas a Políticas

| Regla ID | Regla | Lenient | Standard | Strict |
|-----------|---------|----------|----------|--------|
| V001 | Parámetros oficiales 2025 | WARN | **BLOCK** | **BLOCK** |
| V002 | Tipo de contrato válido | **BLOCK** | **BLOCK** | **BLOCK** |
| V003 | Auxilio transporte | INFO | WARN | **BLOCK** |
| V004 | Fórmulas cesantías | WARN | **BLOCK** | **BLOCK** |
| V005 | Intereses tasa | WARN | **BLOCK** | **BLOCK** |
| V006 | Prima semestre | WARN | WARN | **BLOCK** |

### 2.3 Configuración de Overrides

#### Override Configuration por Política
```yaml
override_configurations:
  # Lenient: Override sin restricciones
  lenient:
    allow_self_approval: true
    require_reasoning: false
    auto_approve_timeout_minutes: 0
    max_overrides_per_session: 10
  
  # Standard: Override supervisado
  standard:
    allow_self_approval: false
    require_reasoning: true
    auto_approve_timeout_minutes: 30
    max_overrides_per_session: 5
    notify_approvers: ["supervisor_nomina@empresa.com"]
  
  # Strict: Override aprobación legal
  strict:
    allow_self_approval: false
    require_reasoning: true
    auto_approve_timeout_minutes: 60
    max_overrides_per_session: 2
    notify_approvers: [
      "supervisor_nomina@empresa.com",
      "dept_legal@empresa.com"
    ]
    require_2fa_approval: true
```

### 2.4 Workflow Settings por Política

```yaml
workflow_settings:
  lenient:
    auto_proceed_after_validation: true
    require_human_review: false
    allow_parallel_execution: true
    max_timeout_minutes: 30
    
  standard:
    auto_proceed_after_validation: false
    require_human_review: false
    allow_parallel_execution: true
    max_timeout_minutes: 15
    
  strict:
    auto_proceed_after_validation: false
    require_human_review: true
    allow_parallel_execution: false
    max_timeout_minutes: 5
```

---

## 3. Configuración de Logging

### 3.1 Estructura de Configuración de Logging

### 3.1.1 Formatters (formatos de mensajes)

El sistema define múltiples formattters para diferentes propósitos:

```yaml
formatters:
  # Formato estándar para producción
  production:
    format: '%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] (%(threadName)s) %(message)s'
    datefmt: '%Y-%m-%d %H:%M:%S'
  
  # Formato detallado para debugging
  detailed:
    format: '%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] (%(threadName)s) PID:%(process)d %(funcName)s() - %(message)s'
    datefmt: '%Y-%m-%d %H:%M:%S'
  
  # Formato para auditoría (CSV-like)
  audit:
    format: '%(asctime)s;%(levelname)s;%(name)s;%(message)s'
    datefmt: '%Y-%m-%d %H:%M:%S'
```

### 3.1.2 Handlers (destinos de logs)

#### Handler Principal (console y archivo)
```yaml
handlers:
  # Consola para desarrollo/monitoreo
  console_handler:
    class: logging.StreamHandler
    level: INFO
    formatter: console
    stream: ext://sys.stderr
  
  # Archivo rotating principal
  main_file_handler:
    class: logging.handlers.RotatingFileHandler
    level: DEBUG
    formatter: production
    filename: logs/liquidacion.log
    maxBytes: 10485760  # 10MB
    backupCount: 10
    encoding: utf-8
```

#### Handler Específico para Auditoría
```yaml
  # Trail de auditoría con rotación diaria
  audit_file_handler:
    class: logging.handlers.TimedRotatingFileHandler
    level: DEBUG
    formatter: audit
    filename: audit/audit_trails.log
    when: midnight
    interval: 1
    backupCount: 365  # Mantener logs por año
    encoding: utf-8
    atTime: datetime.time(0, 0, 0)
```

#### Handler para Compliance Legal
```yaml
  # Logs específicos de compliance
  compliance_file_handler:
    class: logging.handlers.TimedRotatingFileHandler
    level: INFO
    formatter: audit
    filename: audit/compliance_logs.log
    when: W0  # Rotación semanal (lunes)
    interval: 1
    backupCount: 104  # 2 años de logs semanales
    encoding: utf-8
```

### 3.2 Loggers por Módulo

El sistema configura loggers específicos para diferentes componentes:

#### Logger Principal
```yaml
loggers:
  liquidator:
    level: INFO
    propagate: False
    handlers: [console_handler, main_file_handler]
```

#### Logger para Calculadores (detalle intermedio)
```yaml
  liquidator.calculators:
    level: DEBUG
    propagate: False
    handlers: [main_file_handler]
    extra:
      log_intermediate_calculations: true
      log_formula_steps: true
```

#### Logger para Compliance (critical data)
```yaml
  liquidator.compliance:
    level: INFO
    propagate: False
    handlers: [compliance_file_handler, main_file_handler]
    extra:
      log_validation_results: true
      log_override_requests: true
```

#### Logger para Auditoría
```yaml
  liquidator.audit:
    level: DEBUG
    propagate: False
    handlers: [audit_file_handler]
    extra:
      log_all_events: true
      include_hashes: true
```

### 3.3 Logging Contextual

El sistema puede incluir información contextual en cada log:

```yaml
contextual_logging:
  # Variables del sistema
  system_context:
    include_session_id: true
    include_thread_id: true
    include_function_name: true
    include_line_number: true
  
  # Variables negocio
  business_context:
    include_liquidation_id: false
    include_compliance_status: true
    include_validation_id: true
```

### 3.4 Configuración por Politi­ca

La configuración de logging se ajusta según la policy de compliance:

```yaml
policy_adjustments:
  lenient:
    base_level: "INFO"
    detail_level: "INFO"
    audit_level: "WARNING"
    
  standard:
    base_level: "INFO"
    detail_level: "DEBUG"
    audit_level: "INFO"
    
  strict:
    base_level: "DEBUG"
    detail_level: "DEBUG"
    audit_level: "DEBUG"
```

### 3.5 Filtros Personalizados

Se pueden configurar filtros para manejar información sensible:

```yaml
custom_filters:
  # Filtrar información sensible
  sensitive_data_filter:
    pattern: '(password|secret|token|key|credential)'
    replacement: '[REDACTED_SENSITIVE]'
    enabled: true
  
  # Filtrar PII (desactivado por defecto)
  pii_filter:
    pattern: '(cedula|documento|identificacion)'
    replacement: '[PII_DATA]'
    enabled: false
  
  # Filtrar montos (desactivado por defecto)
  financial_filter:
    pattern: '\b[0-9]{6,}\b'
    replacement: '[AMOUNT]'
    enabled: false
```

---

## 4. Configuración de Performance

### 4.1 Caching de Parámetros

Para mejorar performance, el sistema implementa caching de parámetros legales:

```yaml
performance:
  cache:
    enabled: true
    ttl_seconds: 3600    # 1 hora
    max_entries: 1000
    backend: "memory"     # memory | redis | memcached
```

#### Implementación de Caching
```python
# liquidator/params/cached_loader.py
class CachedParamsLoader:
    def __init__(self, config: dict):
        self.cache_config = config['performance']['cache']
        self.ttl = self.cache_config['ttl_seconds']
        self.cache = {}
        self._lock = threading.Lock()
    
    def get_params(self, year: int = 2025) -> dict:
        cache_key = f'params_{year}'
        
        with self._lock:
            # Check cache
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                if time.time() - entry['timestamp'] < self.ttl:
                    return entry['params']
            
            # Load from disk
            params = self._load_from_disk(year)
            
            # Update cache
            self.cache[cache_key] = {
                'params': params,
                'timestamp': time.time()
            }
            
            return params
```

### 4.2 Procesamiento en Lote

Para procesamiento de múltiples liquidaciones:

```yaml
performance:
  batch_processing:
    enabled: true
    max_workers: 4
    batch_size: 100
    timeout_seconds: 300
```

#### Implementación de Batch Processing
```python
# liquidator/core/batch_processor.py
class BatchProcessor:
    def __init__(self, config: dict):
        self.config = config['performance']['batch_processing']
        self.max_workers = self.config['max_workers']
    
    def process_batch(self, cases: List[dict]) -> List[dict]:
        """Procesa múltiples casos en paralelo"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._process_case, case): case 
                for case in cases
            }
            
            results = []
            for future in as_completed(futures):
                case = futures[future]
                try:
                    result = future.result(timeout=self.config['timeout_seconds'])
                    results.append({"case": case, "result": result, "status": "SUCCESS"})
                except Exception as e:
                    results.append({"case": case, "error": str(e), "status": "ERROR"})
            
            return results
```

---

## 5. Configuración de Seguridad

### 5.1 Encriptación y Protección de Datos

```yaml
security:
  # Encriptación de datos sensibles
  encrypt_sensitive_data: false
encryption:
  algorithm: "AES256"
  key_source: "environment"  # environment | file | kms
  
  # Keys específicas
  api_keys:
    encryption_key: "LIQUIDACION_ENCRYPTION_KEY"
    signing_key: "LIQUIDACION_SIGNING_KEY"
    audit_key: "LIQUIDACION_AUDIT_KEY"
```

### 5.2 Validación y Sanitización de Inputs

```yaml
security:
  input_validation:
    strict_schema_validation: true
    sanitize_inputs: true
    max_input_size: "1MB"
    
    # Validaciones específicas
    validations:
      date_format: "YYYY-MM-DD"
      salary_ranges: "positive_integer"
      text_fields: "no_special_chars_allowed"
      file_uploads: "allowed_extensions: json,csv,xlsx"
```

### 5.3 Control de Acceso y Autorización

```yaml
security:
  access_control:
    require_authentication: false
    session_timeout: 3600  # 1 hora
    max_concurrent_requests: 100
    
    rate_limiting:
      enabled: false
      requests_per_minute: 100
      burst_size: 200
```

---

## 6. Configuración de Integración

### 6.1 Integración con Base de Datos (opcional)

```yaml
integration:
  database:
    enabled: false
    engine: "sqlite"  # sqlite | postgres | mysql
    connection_string: "sqlite:///liquidacion.db"
    
    # Pool connections
    pool:
      min_connections: 1
      max_connections: 10
      connection_timeout: 30
    
    # Retention policies
    retention:
      audit_trails: "10 years"
      logs: "2 years"
      calculations: "5 years"
```

### 6.2 Integración con API Externa (opcional)

```yaml
integration:
  external_api:
    enabled: false
    base_url: "https://api.empresa.com"
    timeout_seconds: 30
    retry_attempts: 3
    
    authentication:
      type: "bearer"  # bearer | basic | api_key
      credentials_env: "LIQUIDACION_API_TOKEN"
    
    endpoints:
      validate_employee: "/v1/employees/{id}/validate"
      historical_data: "/v1/companies/{id}/salaries"
```

---

## 7. Configuración de Monitorización

### 7.1 Health Checks

```yaml
monitoring:
  health_check:
    enabled: false
    endpoint: "/health"
    interval_seconds: 30
    
    checks:
      params_file_accessible: true
      disk_space_minimum: "500MB"
      memory_maximum: "80%"
      response_time_maximum: "2s"
```

### 7.2 Métricas y Performance

```yaml
monitoring:
  metrics:
    enabled: false
    endpoint: "/metrics"
    collection_interval_seconds: 60
    
    metrics_tracked:
      - "liquidation_requests_total"
      - "liquidation_success_ratio"
      - "compliance_status_distribution"
      - "calculation_timing_histogram"
```

### 7.3 Alerts

```yaml
monitoring:
  alerts:
    enabled: false
    
    # Alert conditions
    conditions:
      error_rate_threshold: 0.05  # 5%
      critical_rate_threshold: 0.01  # 1%
      response_time_threshold: "5s"
      
    # Delivery methods
    delivery:
      email:
        enabled: false
        recipients: ["admin@empresa.com"]
        smtp_config_env: "LIQUIDATION_SMTP_CONFIG"
        
      webhook:
        enabled: false
        url_env: "LIQUIDATION_WEBHOOK_URL"
        timeout: 5
```

---

## 8. Variables de Entorno

### 8.1 Variables Generales

```bash
# Sistema
LIQUIDACION_ENV=production|staging|development
LIQUIDATION_LOG_LEVEL=DEBUG|INFO|WARNING|ERROR
LIQUIDATION_TIMEZONE=America/Bogota

# Directorios
LIQUIDATION_LOG_DIR=/var/log/liquidacion
LIQUIDATION_AUDIT_DIR=/var/audit/liquidacion
LIQUIDATION_PARAMS_DIR=/etc/liquidacion/params

# Compliance
LIQUIDATION_COMPLIANCE_POLICY=lenient|standard|strict
LIQUIDATION_ENFORCE_COMPLIANCE=true|false
LIQUIDATION_MAX_OVERRIDES_PER_SESSION=5
```

### 8.2 Variables de Seguridad

```bash
# Encripción
LIQUIDACION_ENCRYPTION_KEY=base64_key_here
LIQUIDACION_SIGNING_KEY=base64_key_here

# API tokens (si aplica)
LIQUIDACION_API_TOKEN=bearer_token_here
LIQUIDATION_WEBHOOK_SECRET=webhook_secret_here
```

### 8.3 Variables de Integración

```bash
# Base de datos
LIQUIDACION_DB_URL=sqlite:///liquidacion.db
LIQUIDACION_DB_POOL_SIZE=10

# External API
LIQUIDACION_EXTERNAL_API_URL=https://api.empresa.com
LIQUIDACION_EXTERNAL_API_TIMEOUT=30
```

---

## 9. Configuración por Entorno

### 9.1 Environment: Development

Archivo: `config/development.yaml`

```yaml
logging:
  level: DEBUG
  handlers:
    - console_handler
    - main_file_handler
  
compliance:
  default_policy: lenient
  allow_overrides: true
  
performance:
  cache:
    ttl_seconds: 300  # 5 min para desarrollo
  
security:
  input_validation:
    strict_schema_validation: false
    
monitoring:
  enabled: false
```

### 9.2 Environment: Staging

Archivo: `config/staging.yaml`

```yaml
logging:
  level: INFO
  handlers:
    - main_file_handler
    - audit_file_handler
    
compliance:
  default_policy: standard
  allow_overrides: true
  
performance:
  batch_processing:
    max_workers: 2
    
security:
  input_validation:
    strict_schema_validation: true
    
monitoring:
  enabled: true
  health_check:
    enabled: true
```

### 9.3 Environment: Production

Archivo: `config/production.yaml`

```yaml
logging:
  level: INFO
  handlers:
    - main_file_handler
    - audit_file_handler
    - error_file_handler
    
compliance:
  default_policy: standard
  allow_overrides: true
  
performance:
  cache:
    ttl_seconds: 3600
  batch_processing:
    max_workers: 8
    
security:
  input_validation:
    strict_schema_validation: true
    sanitize_inputs: true
    max_input_size: "1MB"
    
monitoring:
  enabled: true
  health_check:
    enabled: true
  metrics:
    enabled: true
  alerts:
    enabled: true
```

---

## 10. Troubleshooting de Configuración

### 10.1 Problemas Comunes de Configuración

#### Error: Configuration file not found
```
Error: No se pudo encontrar archivo de configuración config/default_config.yaml
```

**Solución:**
```bash
# Verificar archivo existe
ls -la config/default_config.yaml

# Recrear si no existe
cp config/default_config.yaml.example config/default_config.yaml
```

#### Error: Invalid YAML syntax
```
Error: Failed to load configuration - Invalid YAML syntax: ...
```

**Solución:**
```bash
# Validar sintaxis YAML
python -c "import yaml; yaml.safe_load(open('config/default_config.yaml'))"

# Identificar y corregir línea con error
# - Revisar identación (2 espacios, no tabs)
# - Revisar formato de listas y diccionarios
# - Validar quotes y escapes
```

#### Error: Missing required configuration keys
```
Error: La configuración requiere la clave 'system.version'
```

**Solución:**
```bash
# Completar configuración faltante
vim config/default_config.yaml

# Revisar archivo de plantilla para todas las claves requeridas
cat config/default_config.yaml.example
```

### 10.2 Depuración de Configuración

#### Verificar Configuración Cargada
```python
# Debug script para verificar configuración
from liquidator.utils.config_loader import ConfigLoader

loader = ConfigLoader()

# Mostrar toda configuración
import pprint
pprint.pprint(loader.config)

# Verificar configuración específica
print(f"Log level: {loader.get('logging.level')}")
print(f"Compliance policy: {loader.get('compliance.default_policy')}")
```

#### Verificar Loggers Configurados
```python
# Verificar loggers configurados
import logging

# Mostrar todos los loggers configurados
for name in logging.Logger.manager.loggerDict:
    logger = logging.getLogger(name)
    print(f"Logger: {name}, Level: {logger.level}, Handlers: {len(logger.handlers)}")
```

### 10.3 Validación de Configuración

#### Script de Validación
```python
# scripts/validate_config.py
#!/usr/bin/env python3

import sys
import yaml
from pathlib import Path

def validate_config():
    errors = []
    warnings = []
    
    # Config files existe
    config_files = [
        'config/default_config.yaml',
        'config/compliance_policies.yaml',
        'config/logging_config.yaml'
    ]
    
    for config_file in config_files:
        if not Path(config_file).exists():
            errors.append(f"Archivo de configuración faltante: {config_file}")
        else:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    yaml.safe_load(f)
            except yaml.YAMLError as e:
                errors.append(f"Error YAML en {config_file}: {e}")
    
    # Required directories existe
    required_dirs = ['logs', 'audit', 'params']
    
    for directory in required_dirs:
        if not Path(directory).exists():
            warnings.append(f"Directorio faltante: {directory}")
    
    # Validación específica de sección compliance policies
    try:
        with open('config/compliance_policies.yaml') as f:
            compliance_config = yaml.safe_load(f)
        
        required_policies = ['lenient', 'standard', 'strict']
        for policy in required_policies:
            if policy not in compliance_config:
                errors.append(f"Policy faltante en compliance_policies.yaml: {policy}")
    
    except Exception as e:
        errors.append(f"Error validando compliance policies: {e}")
    
    return errors, warnings

if __name__ == '__main__':
    errors, warnings = validate_config()
    
    if errors:
        print("ERRORES encontrados:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    if warnings:
        print("ADVERTENCIAS encontradas:")
        for warning in warnings:
            print(f"  - {warning}")
    
    print("Configuración válida ✓")
```

### 10.4 Performance de Configuración

#### Carga Diferida
Para optimizar startup time, implementar carga diferida de configuraciones:

```python
# liquidator/utils/lazy_config.py
class LazyConfig:
    def __init__(self):
        self._config = None
        self._config_loader = ConfigLoader()
    
    @property
    def config(self):
        if self._config is None:
            self._config = self._config_loader.load()
        return self._config
    
    def get(self, path: str, default=None):
        return self.config.get(path, default)
```

#### Configuración de Logging Tardía
Para evitar problemas de logging temprano antes de configuración completa:

```python
# liquidator/utils/early_logging.py
import logging
import sys

def setup_early_logging(level=logging.INFO):
    """Configura logging básico antes de carga completa de configuración"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        stream=sys.stderr
    )
    
# Llamar temprano en el proceso
setup_early_logging()
```

---

## 11. Buenas Prácticas de Configuración

### 11.1 Principios

1. **Separación de Entornos**: Configuración específica por ambiente
2. **Valores por Defecto Siempre**: Evitar valores hardcodeados
3. **Validación de Schema**: Validar configuración al cargar
4. **Logging de Configuración**: Loggear configuración cargada con nivel DEBUG
5. **Versionamiento**: Versionar cambios en configuración

### 11.2 Scripts de Mantenimiento

#### Script de Backup de Configuración
```bash
#!/bin/bash
# scripts/backup_config.sh

CONFIG_DIR="config"
BACKUP_DIR="backups/config"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

mkdir -p "$BACKUP_DIR"

# Backup archivos de configuración
cp -r "$CONFIG_DIR" "$BACKUP_DIR/config_$TIMESTAMP"

# Backup archivos de parámetros (si aplica)
if [ -d "params" ]; then
    cp -r params "$BACKUP_DIR/params_$TIMESTAMP"
fi

echo "Configuración backed up a $BACKUP_DIR/config_$TIMESTAMP"
```

#### Script de Validación Automática
```python
# scripts/validate_and_rollback.py
#!/usr/bin/env python3

def validate_and_rollback_if_needed():
    """Valida configuración y hace rollback si hay problemas"""
    
    try:
        # Intentar cargar configuración
        loader = ConfigLoader()
        config = loader.config
        
        # Validaciones específicas
        if not validate_compliance_policies_config(config):
            raise ValueError("Configuración de políticas inválida")
        
        if not validate_logging_config(config):
            raise ValueError("Configuración de logging inválida")
        
        print("Configuración validada correctamente ✓")
        
    except Exception as e:
        print(f"Error en configuración: {e}")
        print("Haciendo rollback a configuración anterior...")
        
        # Lógica de rollback aquí
        rollback_to_previous_config()
        raise
```

---

## 12. Conclusión

Una configuración adecuada es fundamental para:
- Seguridad y cumplimiento legal
- Performance y escalabilidad
- Mantenimiento y debugging
- Adaptación a diferentes ambientes

Los administradores del sistema deben:
1. Revisar configuración según entorno específico
2. Establecer políticas de compliance apropiadas
3. Configurar logging y auditoría segun necesidades
4. Validar configuración en deploy
5. Mantener documentación actualizada

Para soporte adicional sobre configuración, contactar a:
- Equipo técnico: technical-support@empresa.com
- Equipo legal: compliance@empresa.com
- Administradores de sistemas: sysadmins@empresa.com
