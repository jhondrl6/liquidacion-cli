# Guía para Desarrolladores
## Sistema de Liquidación de Nómina Colombia 2025

### Versión: 1.0.0
### Fecha: 2025-11-04

---

## Tabla de Contenidos

1. [Configuración del Entorno de Desarrollo](#1-configuración-del-entorno-de-desarrollo)
2. [Estructura del Código](#2-estructura-del-código)
3. [Patrones de Desarrollo](#3-patrones-de-desarrollo)
4. [Testing Framework](#4-testing-framework)
5. [Flujo de Trabajo para Cambios](#5-flujo-de-trabajo-para-cambios)
6. [Guía de Contribución](#6-guía-de-contribución)
7. [Best Practices](#7-best-practices)
8. [Depuración y Troubleshooting](#8-depuración-y-troubleshooting)
9. [Extensión del Sistema](#9-extensión-del-sistema)
10. [Deploy y Producción](#10-deploy-y-producción)

---

## 1. Configuración del Entorno de Desarrollo

### 1.1 Requisitos Previos

- **Python 3.8+** con pip
- **Git** para control de versiones
- **Editor de código** recomendado (VSCode, PyCharm, etc.)
- **Herramientas de desarrollo:** pytest, black, flake8

### 1.2 Setup del Proyecto

```bash
# 1. Clonar el repositorio
git clone https://github.com/usuario/liquidacion_cli.git
cd liquidacion_cli

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# 5. Instalar paquete en modo desarrollo
pip install -e .
```

### 1.3 Configuración de IDE

#### VSCode (recomendado)
```json
// settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.pylintEnabled": false,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["liquidator/tests/"]
}
```

#### Pre-commit hooks (recomendado)
```bash
# Instalar pre-commit
pip install pre-commit

# Instalar hooks
pre-commit install

# Ahora se ejecutarán automáticamente por cada commit
```

---

## 2. Estructura del Código

### 2.1 organización de Directorios

```
liquidacion_cli/
├── bin/                           # Entry points ejecutables
│   └── liquidar.py               # CLI principal
├── liquidator/                    # Paquete principal
│   ├── __init__.py
│   ├── core/                      # Lógica principal
│   │   ├── engine.py             # Motor de orquestación
│   │   ├── input_parser.py       # Parseo de inputs
│   │   └── workflow_orchestrator.py
│   ├── calculators/              # Módulos de cálculo
│   │   ├── sbl_calculator.py
│   │   ├── prestaciones_calculator.py
│   │   └── vacaciones_calculator.py
│   ├── validators/               # Validadores
│   ├── compliance/               # Sistema de cumplimiento legal
│   ├── legal/                    # Componentes legales
│   ├── params/                   # Gestión de parámetros
│   ├── output/                   # Generación de documentos
│   ├── utils/                    # Utilidades generales
│   └── tests/                    # Tests del paquete
├── docs/                         # Documentación
├── params/                       # Parámetros legales
├── examples/                     # Ejemplos de uso
└── tests/                        # Tests globales
```

### 2.2 Convenciones de Nomenclatura

#### Archivos
- **snake_case.py** para todos los archivos Python
- **PascalCase.py** solo para clases principales (Engine.py)
- **README.md** para documentación de directorios

#### Clases y Funciones
```python
# Clases: PascalCase
class PrestacionesCalculator:
    pass

# Funciones/v variables: snake_case
def calculate_cesantias():
    pass

# Constantes: UPPER_SNAKE_CASE
SMMLV = 1423500
DIAS_BASE = 360.0
```

#### Privacidad
```python
# Privado (uso interno): _underscore
def _validate_input():
    pass

# "Privado" pero para uso extendido: leading y trailing
__version__ = "1.0.0"
```

### 2.3 Importaciones y Estructura de Archivos

#### Template para módulos principales
```python
"""
[Módulo Purpose - una línea]

Descripción funcional del módulo. Explicación extendida del propósito
y responsabilidades del componente.

Author: [nombre]
Date: [fecha]
Version: [versión]
"""

# Standard library imports
import json
from datetime import datetime
from pathlib import Path

# Third-party imports (con comentarios de propósito)
import yaml  # Configuration management

# Local application imports
from liquidator.utils.date_utils import calculate_dias_servicio
from liquidator.exceptions import ValidationError

# Constants
DEFAULT_CURRENCY = "COP"

# Classes/functions
class CalculatorBase:
    """Base class for all calculators."""
    
    def __init__(self, params: dict):
        self.params = params
        self.logger = logging.getLogger(__name__)
    
    def validate_params(self) -> None:
        """Validate required parameters."""
        pass

if __name__ == "__main__":
    # Test/demo code
    pass
```

---

## 3. Patrones de Desarrollo

### 3.1 Inyección de Dependencias

Usar inyección de dependencias para testabilidad:

```python
class PrestacionesCalculator:
    def __init__(self, params_loader: ParamsLoader,
                 date_utils: DateUtils,
                 currency_utils: CurrencyUtils):
        self.params_loader = params_loader
        self.date_utils = date_utils
        self.currency_utils = currency_utils
    
    def calculate_cesantias(self, input_data: dict):
        params = self.params_loader.load_params()
        dias = self.date_utils.calculate_dias_servicio(...)
        result = (sbl * dias) / params['DIAS_BASE']
        return self.currency_utils.round_currency(result)
```

### 3.2 Builder Pattern para Objetos Complejos

```python
class LiquidacionOutputBuilder:
    """Builder for structured output generation"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.data = {"meta": {}, "desglose": {}, "compliance": {}}
        return self
    
    def set_meta(self, modo: str, fecha_generacion: str):
        self.data["meta"].update({
            "modo": modo,
            "fecha_generacion": fecha_generacion
        })
        return self
    
    def add_desglose(self, prestaciones: dict):
        self.data["desglose"].update(prestaciones)
        return self
    
    def build(self) -> dict:
        output = self.data.copy()
        self.reset()  # Ready for next build
        return output

# Usage
output_builder = LiquidacionOutputBuilder()
result = (output_builder
           .set_meta("PERIODICA", "2025-11-04")
           .add_desglose(prestaciones_dict)
           .build())
```

### 3.3 Strategy Pattern para Diferentes Modalidades

```python
class CalculatorStrategy:
    """Interface for different calculation strategies"""
    
    def calculate_all(self, input_data: dict, params: dict) -> dict:
        raise NotImplementedError

class PeriodicaStrategy(CalculatorStrategy):
    def calculate_all(self, input_data: dict, params: dict) -> dict:
        # Specific logic for periodica mode
        return {
            "cesantias": self._calculate_cesantias(...),
            "intereses": self._calculate_intereses(...),
            "prima": self._calculate_prima(...),
            "vacaciones": {"valor": 0, "nota": "No aplica en modo PERIÓDICA"}
        }

class FiniquitoStrategy(CalculatorStrategy):
    def calculate_all(self, input_data: dict, params: dict) -> dict:
        # Specific logic for finiquito mode
        return {
            "cesantias": self._calculate_cesantias(...),
            "intereses": self._calculate_intereses(...),
            "prima": self._calculate_prima(...),
            "vacaciones": self._calculate_vacaciones(...),
            "indemnizacion": self._calculate_indemnizacion(...)
        }

class WorkflowOrchestrator:
    def __init__(self):
        self._strategies = {
            "PERIODICA": PeriodicaStrategy(),
            "FINIQUITO": FiniquitoStrategy()
        }
    
    def get_strategy(self, modo: str) -> CalculatorStrategy:
        strategy = self._strategies.get(modo)
        if not strategy:
            raise ValueError(f"Modo no soportado: {modo}")
        return strategy
```

### 3.4 Error Handling Consistente

```python
class CalculatorError(Exception):
    """Base exception for all calculation errors"""
    pass

class ValidationError(CalculatorError):
    """Raised when input validation fails"""
    pass

class ComplianceError(CalculatorError):
    """Raised when legal compliance requirements fail"""
    def __init__(self, message, rule_id: str = None, blocking: bool = True):
        super().__init__(message)
        self.rule_id = rule_id
        self.blocking = blocking

def safe_divide(dividend: float, divisor: float) -> float:
    """Safe division with error handling"""
    try:
        return dividend / divisor
    except ZeroDivisionError:
        raise CalculationError("División por cero no permitida")
    except Exception as e:
        raise CalculationError(f"Error en cálculo matemático: {e}")
```

### 3.5 Logging Estratégico

```python
import logging

logger = logging.getLogger(__name__)

class PrestacionesCalculator:
    def calculate_cesantias(self, sbl: float, dias: int):
        logger.debug(f"Iniciando cálculo de cesantías: SBL={sbl}, días={dias}")
        
        try:
            result = safe_divide(sbl * dias, 360)
            logger.info(f"Cesantías calculadas: {result}")
            return result
        except CalculationError:
            logger.error("Fallo en cálculo de cesantías")
            raise
```

---

## 4. Testing Framework

### 4.1 Tipos de Tests

#### Tests Unitarios
```python
# liquidator/tests/test_calculators/test_prestaciones.py
import pytest
from liquidator.calculators.prestaciones_calculator import PrestacionesCalculator

class TestPrestacionesCalculator:
    
    @pytest.fixture
    def calculator(self):
        params = {"DIAS_BASE": 360.0, "TASA_INT_CESANTIAS": 0.12, "REDONDEO": 0}
        return PrestacionesCalculator(params)
    
    def test_cesantias_calculation_basic(self, calculator):
        """Test básico de cálculo de cesantías"""
        result = calculator.calculate_cesantias(2000000, 365)
        
        assert result["valor"] == 2033333
        assert result["dias_liquidados"] == 365
        assert result["norma"] == "Art.249-250 CST"
    
    @pytest.mark.parametrize("sbl, dias, expected", [
        (1000000, 365, 1013889),  # (1.000.000 × 365) ÷ 360 = 1.013.889
        (2000000, 180, 1000000),  # (2.000.000 × 180) ÷ 360 = 1.000.000
        (3500000, 30, 291667),    # (3.500.000 × 30) ÷ 360 = 291.667
    ])
    def test_cesantias_parametrized(self, calculator, sbl, dias, expected):
        result = calculator.calculate_cesantias(sbl, dias)
        assert result["valor"] == expected
    
    def test_invalid_dias_raises_error(self, calculator):
        with pytest.raises(ValidationError):
            calculator.calculate_cesantias(1000000, -10)  # Días negativos no permitidos
```

#### Tests de Integración
```python
# liquidator/tests/test_integration/test_complete_workflow.py
def test_complete_periodica_workflow():
    """Test de flujo completo PERIÓDICA"""
    input_data = {
        "modo": "PERIODICA",
        "fecha_ingreso": "2024-01-03",
        "fecha_corte": "2024-12-31",
        "salario_mensual": 2000000
    }
    
    engine = LiquidacionEngine()
    result = engine.process(input_data)
    
    # Verificaciones básicas
    assert result["meta"]["modo"] == "PERIÓDICA"
    assert "cesantias" in result["desglose"]
    assert result["compliance_report"]["compliance_status"] in ["GO", "WARN"]
    
    # Verificar cálculos específicos
    assert result["desglose"]["vacaciones"]["valor"] == 0
    
# Tests de fixtures para datos complejos
@pytest.fixture
def complex_finca_case():
    """Caso complejo de trabajador de finca con salarios variables"""
    return {
        "modo": "PERIODICA",
        "fecha_ingreso": "2023-11-16",
        "fecha_corte": "2025-11-15",
        "salario_mensual": 1800000,
        "reside_en_lugar_trabajo": True,
        "salarios_historicos": [
            {"periodo": "2024-01", "total": 1800000},
            {"periodo": "2024-02", "total": 2100000},
            {"periodo": "2024-03", "total": 1950000}
        ],
        "comisiones_promedio_mensual": 300000
    }

def test_finca_complex_case(complex_finca_case):
    """Test caso complejo de finca rural"""
    engine = LiquidacionEngine()
    result = engine.process(complex_finca_case)
    
    # Verificac específicas para caso de finca
    assert result["meta"]["compliance_status"] == "GO"
    assert "auxilio_transporte_excluido" in result["validaciones_y_alertas"]
```

#### Tests de Compliance
```python
# liquidator/tests/test_compliance/test_v003_auxilio_transporte.py
def test_v003_auxilio_transporte_excluded_finquero():
    """Test V003: auxilio excluido correctamente en finca"""
    input_data = {
        "reside_en_lugar_trabajo": True,
        "salario_mensual": 1500000
    }
    
    sbl_data = {"SBL_GENERAL": 1500000}
    
    evaluator = RuleEvaluator()
    result = evaluator.evaluate_v003_auxilio_transporte("V003", input_data, sbl_data, {}, {})
    
    assert result["result"] == "PASS"
    assert "finca" in result["evidence"][0].lower()
```

### 4.2 Test Coverage

#### Configuración
```bash
# Instalar pytest-cov
pip install pytest-cov

# Ejecutar con coverage
pytest liquidator/tests/ --cov=liquidator --cov-report=html

# Para coverage en módulo específico
pytest liquidator/tests/test_calculators/ --cov=liquidator.calculators
```

#### Targets de Coverage
- **Módulos críticos** (calculators, compliance): >95%
- **Módulos principales** (core, validators): >90%
- **Sistema general**: >85%

### 4.3 Tests de Performance

```python
import time
import pytest
from liquidator.core.engine import LiquidacionEngine

@pytest.mark.performance
def test_large_batch_performance():
    """Test performance con múltiples cálculos"""
    engine = LiquidacionEngine()
    
    # Medir time
    start_time = time.time()
    
    # Procesar 100 casos
    for i in range(100):
        test_case = generate_basic_test_case(modified_for_batch=i)
        engine.process(test_case)
    
    elapsed = time.time() - start_time
    
    # Debe completar en razonable tiempo (< 30 segundos para 100 casos)
    assert elapsed < 30.0, f"Performance issue: {elapsed}s para 100 casos"
```

---

## 5. Flujo de Trabajo para Cambios

### 5.1 Desarrollo de Nueva Funcionalidad

#### 1. Crear Branch de Feature
```bash
git checkout -b feature/nueva_prestacion_social
```

#### 2. Desarrollo Iterativo
```bash
# Escribir tests primero (TDD)
vim liquidator/tests/test_calculators/test_nueva_prestacion.py

# Implementar funcionalidad
vim liquidator/calculators/nueva_prestacion_calculator.py

# Ejecutar tests regularmente
pytest liquidator/tests/test_calculators/test_nueva_prestacion.py::test_calculo_basico

# Ejecutar tests de regresión
pytest liquidator/tests/test_integration/
```

#### 3. Verificar Compliance
```bash
# Ejecutar suite completa de compliance
pytest liquidator/tests/test_compliance/

# Verificar nueva regla si aplica
python -c "from liquidator.compliance.rule_evaluator import RuleEvaluator; print(RuleEvaluator().evaluate_v011_new_rule(...))"
```

#### 4. Documentación
```bash
# Actualizar docstrings
vim liquidator/calculators/nueva_prestacion_calculator.py

# Actualizar documentación de API
vim docs/api_reference.md

# Agregar ejemplo de uso
vim examples/example_nueva_prestacion.json
```

#### 5. Pull Request
```bash
# Formatear código
black liquidator/calculators/nueva_prestacion_calculator.py
flake8 liquidator/calculators/nueva_prestacion_calculator.py

# Commit
git add .
git commit -m "feat: Add calculadora for new social benefit

- Implemente nueva_prestacion_calculator con fórmula Legal X
- Agrega validación V011 para cumplimiento legal
- Update API documentation
- Add integration tests"

# Push y PR
git push origin feature/nueva_prestacion_social
# Abrir PR en GitHub
```

### 5.2 Bug Fixes

#### 1. Aislar el Problema
```bash
# Reproducir issue con test minimalista
echo "import pytest; from liquidator.core.engine import LiquidacionEngine; pytest.main(['--capture=no'])" > debug_calc.py
python -i debug_calc.py
```

#### 2. Corregir con Tests Primero
```bash
# Escribir test que falle
vim liquidator/tests/test_reproducible_bug.py

# Corregir implementación hasta que test pase
vim liquidator/calculators/calculadora_afectada.py
```

#### 3. Verificar Sin Regresiones
```bash
# Full test suite
pytest liquidator/tests/ --cov=liquidator

# Performance validation
pytest liquidator/tests/performance/
```

---

## 6. Guía de Contribución

### 6.1 Code Review Checklist

Para cada Pull Request, reviewers deben verificar:

#### **Funcionalidad**
- [ ] La funcionalidad cumple con los requisitos
- [ ] Tests cubren casos edge cases
- [ ] Manejo correcto de errores
- [ ] Performance aceptable

#### **Calidad de Código**
- [ ] Código sigue PEP 8 y convenciones del proyecto
- [ ] Naming consistente y significativo
- [ ] Dead code eliminado
- [ ] Docstrings completos

#### **Testing**
- [ ] Tests nuevos pasan
- [ ] Tests existentes no rompen
- [ ] Coverage target alcanzado
- [ ] Tests de integración incluidos

#### **Compliance Legal**
- [ ] Reglas de compliance actualizadas si aplica
- [ ] Referencias normativas correctas
- [ ] Cálculos validados contra ejemplos legales
- [ ] Evidencia en outputs adecuada

#### **Documentación**
- [ ] README actualizado
- [ ] API docs actualizadas
- [ ] Ejemplos incluidos
- [ ] Changelog actualizado

### 6.2 Mensajes de Commit

Usar formato [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Tipos permitidos:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Documentation
- `style`: Formateo (sin cambio funcional)
- `refactor`: Refactoring
- `test`: Tests
- `chore`: Tareas de mantenimiento/others

**Ejemplos:**
```
feat(calculators): Add calculadora for employee stock options
fix(compliance): Correct plazo_pago_legal calculation for prima semestre
docs(README): Update installation instructions
refactor(core): Extract common validation logic
test(vacaciones): Add tests for leap year calculations
```

### 6.3 Version Semántico

El sistema utiliza [Semantic Versioning](https://semver.org/):

**X.Y.Z donde:**
- **X**: Major - Cambios que rompen compatibilidad
- **Y**: Minor - Nuevas funcionalidades, backwards compatible
- **Z**: Patch - Correcciones de bugs, backwards compatible

### 6.4 Release Process

#### Para lanzar nueva versión:

1. **Actualizar versión en __init__.py**:
```python
__version__ = "1.1.0"
```

2. **Actualizar Changelog**:
```bash
vim CHANGELOG.md
# Añadir entradas para versión
```

3. **Crear tag y release**:
```bash
git tag -a v1.1.0 -m "Release v1.1.0: Employee stock options calculation"
git push origin v1.1.0
```

4. **Publicar**:
```bash
# Si hay setup.py
python setup.py sdist bdist_wheel
twine upload dist/*
```

---

## 7. Best Practices

### 7.1 Principios SOLID

#### Single Responsibility Principle
```python
# ✅ Each class has single reason to change
class SBLCalculator:        # Only SBL calculations
class PrestacionesCalculator:  # Only prestaciones calculations
class ComplianceValidator:   # Only compliance checks

# ❌ Too many responsibilities
class AllInOneCalculator:
    def calculate_sbl(self): pass
    def validate_compliance(self): pass
    def generate_pdf(self): pass
```

#### Open/Closed Principle
```python
# ✅ Open for extension, closed for modification
class CalculatorStrategy:
    def calculate(self, params): pass

class StandardCalculatorStrategy(CalculatorStrategy):
    def calculate(self, params): pass

class EmergencyCalculatorStrategy(CalculatorStrategy):
    def calculate(self, params): pass
```

#### Dependency Inversion Principle
```python
# ✅ Depend on abstractions, not concrete implementations
class PrestacionesCalculator:
    def __init__(self, tax_calculator: TaxCalculatorInterface,
                 date_utils: DateUtilsInterface):
        self.tax_calculator = tax_calculator
        
# ❌ Hard-coded dependencies
class PrestacionesCalculator:
    def __init__(self):
        self.tax_calculator = StandardTaxCalculator()  # No flexibility
```

### 7.2 Principios de Diseño de Python (The Zen of Python)

#### Readability Counts
```python
# ✅ Clear and expressive
def calculate_severance_pay(base_salary: float, days_worked: int) -> dict:
    """Calculate severance pay according to Colombian law.
    
    Args:
        base_salary: Monthly base salary in COP
        days_worked: Total days worked including end date
    
    Returns:
        Dictionary with calculated severance pay and metadata
    """
    formula_amount = (base_salary * days_worked) / 360
    return {
        "amount": round(formula_amount, 0),
        "formula_used": f"({base_salary} × {days_worked}) ÷ 360",
        "legal_reference": "Art.249-250 CST"
    }

# ❌ Cryptic
def cp(b: float, d: int) -> dict:
    return {"amt": round(b*d/360, 0)}
```

#### Explicit is Better Than Implicit
```python
# ✅ Explicit parameters with types
def calculate_final_settlement(salaries: List[Tuple[str, float]], 
                            contract_type: ContractType,
                            termination_reason: str) -> dict:
    pass

# ❌ Implicit dependencies or unclear parameters
def calculate(data, mode="standard"):
    pass
```

#### Errors Should Never Pass Silently
```python
# ✅ Handle errors explicitly
try:
    calculation_result = perform_calculation(input_data)
    return calculation_result
except ComplianceError as e:
    logger.error(f"Compliance failed: {e}", exc_info=True)
    raise
except CalculationException as e:
    logger.error(f"Calculation error: {e}")
    return {"error": str(e), "status": "COMPLETED_WITH_ERRORS"}

# ❌ Silent failures
try:
    calculation_result = perform_calculation(input_data)
except Exception:  # Catching too broadly and silently ignoring
    return {"status": "DONE"}  # Without indicating issue occurred
```

### 7.3 Principios de Seguridad

#### Input Validation
```python
# ✅ Never trust inputs - always validate
def process_liquidation(raw_input: dict) -> dict:
    # Validate schema first
    input_validator.validate_structure(raw_input)
    
    # Sanitize inputs
    clean_input = input_sanitizer.clean(raw_input)
    
    # Then process
    return calculator.process(clean_input)

# ❌ Processing untrusted inputs directly
def process_liquidation(raw_input: dict) -> dict:
    return calculator.process(raw_input)  # Dangerous!
```

#### No Hardcoded Secrets
```python
# ✅ Use environment variables or config
import os
from liquidator.settings import get_config

config = get_config()
private_key = os.getenv('PRIVATE_KEY') or config['private_key']
```

---

## 8. Depuración y Troubleshooting

### 8.1 Logging Estratégico

```python
import logging

# Configure logging at module level
logger = logging.getLogger(__name__)

class PrestacionesCalculator:
    def calculate_cesantias(self, sbl: float, dias: int) -> dict:
        # Debug-level for detailed flow analysis
        logger.debug(f"Starting cesantías calculation - SBL: {sbl}, Days: {dias}")
        
        try:
            # Info-level for significant operations
            result = self._perform_calculation(sbl, dias)
            logger.info(f"Cesantías calculated successfully: {result}")
            return result
            
        except CalculationError as e:
            # Error-level for problems
            logger.error(f"Calculation failed for cesantías: {e}")
            raise
            
        except Exception as e:
            # Critical for unexpected failures
            logger.critical(f"Unexpected error in cesantías calc: {e}", exc_info=True)
            raise
```

### 8.2 Asserts en Desarrollo

```python
def calculate_severance_pay(salary: float, days: int) -> dict:
    # Development assertions - only active in debug
    
    assert days > 0, f"Negative days not allowed: {days}"
    assert salary > ColombianConstants.MINIMUM_WAGE, f"Below minimum wage: {salary}"
    
    # Formula calculation
    amount = (salary * days) / 360
    
    # Verify result is reasonable
    assert 0 < amount < salary * 365, f"Unreasonable amount: {amount}"
    
    return {"amount": amount, "days": days}
```

### 8.3 Performance Profiling

```python
import cProfile
import pstats
from contextlib import contextmanager

@contextmanager
def profiler_context():
    """Context manager for profiling code sections"""
    profiler = cProfile.Profile()
    profiler.enable()
    yield profiler
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions

# Usage
with profiler_context() as prof:
    engine = LiquidacionEngine()
    for case in test_cases:
        engine.process(case)

# Will output performance statistics
prof.stats.sort_stats('tottime')
prof.print_stats(10)
```

### 8.4 Memory Management

```python
import gc

def process_large_batch(cases: List[Dict]) -> None:
    """Process many cases without memory leaks"""
    batch_size = 100
    
    for i in range(0, len(cases), batch_size):
        batch = cases[i:i + batch_size]
        
        for case in batch:
            result = engine.process(case)
            # Do something with result
            save_result(result)
            
        # Explicitly clean to prevent memory buildup
        del batch
        gc.collect()
```

---

## 9. Extensión del Sistema

### 9.1 Añadir Nueva Prestación

#### 1. Crear Módulo Calculador
```python
# liquidator/calculators/stock_options_calculator.py
class StockOptionsCalculator:
    """Calculate employee stock options according to Colombian regulations"""
    
    def __init__(self, params: dict):
        self.params = params
        
    def calculate_options_value(self, options_grant_data: dict) -> dict:
        """Calculate value of vested stock options"""
        validate_grant_data(options_grant_data)
        # Implementation here
        return {
            "valor": calculated_value,
            "norma": "Ley 1234/2021",
            "detalles": {...}
        }
    
    def validate_legal_compliance(self, options_data: dict) -> List[str]:
        """Return list of compliance warnings/errors"""
        warnings = []
        
        if options_data['grant_date'] < options_data['hiring_date'] + timedelta(days=365):
            warnings.append("Cannot grant options before 1 year of service")
            
        return warnings
```

#### 2. Integrar con Motor Principal
```python
# liquidator/core/engine.py
class LiquidacionEngine:
    def __init__(self):
        # ... existing initializers ...
        self.stock_options_calculator = StockOptionsCalculator(params)
    
    def process(self, input_data: dict) -> dict:
        # ... existing processing ...
        
        # Add stock options if present in input
        if 'stock_options' in input_data:
            stock_options = self.stock_options_calculator.calculate_options_value(
                input_data['stock_options']
            )
            result['desglose']['stock_options'] = stock_options
        
        return result
```

#### 3. Añadir Regla de Compliance
```python
# liquidator/compliance/rule_evaluator.py
class RuleEvaluator:
    VALIDATION_RULES = {
        # ... existing rules ...
        'V011': 'Opciones de Acciones - compliance legal'
    }
    
    def evaluate_v011_stock_options(self, rule_id: str, input_data: dict, **kwargs) -> dict:
        """Validate V011: Stock options compliance"""
        if 'stock_options' not in input_data:
            return {"result": "PASS", "evidence": ["No stock options present"]}
        
        calculador = StockOptionsCalculator()
        violations = calculador.validate_legal_compliance(input_data['stock_options'])
        
        if violations:
            return {
                "result": "FAIL",
                "evidence": violations,
                "block_reason": "Stock options compliance violations"
            }
        else:
            return {
                "result": "PASS",
                "evidence": ["Stock options compliant"]
            }
```

#### 4. Tests
```python
# liquidator/tests/test_calculators/test_stock_options.py
def test_basic_stock_options_calculation():
    calculator = StockOptionsCalculator(params)
    
    options_data = {
        "grant_date": "2023-01-01",
        "vesting_date": "2024-01-01",
        "number_of_shares": 100,
        "grant_price_usd": 10.0,
        "market_price_usd": 15.0
    }
    
    result = calculator.calculate_options_value(options_data)
    
    assert result["valor"] > 0
    assert "norma" in result
    assert "Ley" in result["norma"]
```

### 9.2 Añadir Nuevo Formato de Salida

#### 1. Implementar Generador
```python
# liquidator/output/excel_generator.py
class ExcelGenerator:
    """Generate professional Excel reports"""
    
    def generate(self, data: dict, output_path: str) -> bool:
        """Create Excel file with liquidation details"""
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill
            
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Liquidación"
            
            # Add headers with formatting
            self._add_headers(ws, data['meta'])
            
            # Add calculation details
            self._add_prestaciones_table(ws, data['desglose'])
            
            # Add compliance summary
            self._add_compliance_section(ws, data['compliance_report'])
            
            wb.save(output_path)
            return True
            
        except Exception as e:
            logger.error(f"Excel generation failed: {e}")
            return False
```

#### 2. Integrar con Output Generator
```python
# liquidator/output/output_generator.py
class OutputGenerator:
    def __init__(self):
        self.json_generator = JSONGenerator()
        self.markdown_generator = MarkdownGenerator()
        self.pdf_generator = PDFGenerator()
        self.excel_generator = ExcelGenerator()
    
    def generate_all_formats(self, data: dict, base_path: str) -> dict:
        """Generate files in all available formats"""
        results = {}
        
        # JSON (always)
        results['json'] = self.json_generator.generate(data, f"{base_path}.json")
        
        # Markdown (always)
        results['markdown'] = self.markdown_generator.generate(data, f"{base_path}.md")
        
        # PDF (if available)
        results['pdf'] = self.pdf_generator.generate(data, f"{base_path}.pdf")
        
        # Excel (new format)
        results['excel'] = self.excel_generator.generate(data, f"{base_path}.xlsx")
        
        return results
```

### 9.3 Añadir Nueva Regla de Compliance

#### 1. Definir Regla
```python
# liquidator/compliance/rules/v012_minimum_salary_compliance.py
class MinimumSalaryComplianceRule:
    """V012: Validate minimum salary compliance"""
    
    RULE_ID = "V012"
    RULE_NAME = "Cumplimiento Salario Mínimo"
    SEVERITY = "CRITICAL"
    
    def evaluate(self, input_data: dict, params: dict) -> dict:
        """Evaluate salary against minimum wage"""
        minimum_wage = params['SMMLV']
        employee_salary = input_data['salario_mensual']
        
        evidence = [
            f"Salario empleado: {employee_salary:,} COP",
            f"SMMLV actual: {minimum_wage:,} COP"
        ]
        
        if employee_salary < minimum_wage:
            result = "FAIL"
            evidence.append(f"Salario inferior a SMMLV en {minimum_wage - employee_salary:,} COP")
            blocking = True
        else:
            result = "PASS"
            evidence.append("Cumple con SMMLV")
            blocking = False
        
        return {
            "id": self.RULE_ID,
            "description": self.RULE_NAME,
            "result": result,
            "evidence": evidence,
            "blocking": blocking,
            "rule_ref": ["Decreto 1572/2024"],
            "impacted_amount": abs(employee_salary - minimum_wage) if blocking else 0
        }
```

#### 2. Registrar Regla
```python
# liquidator/compliance/rule_evaluator.py
class RuleEvaluator:
    def __init__(self):
        # Import all rules dynamically
        from .rules import v012_minimum_salary_compliance
        self.v012_rule = v012_minimum_salary_compliance.MinimumSalaryComplianceRule()
    
    def evaluate_v012_minimum_salary(self, rule_id: str, input_data: dict, 
                                   params: dict, **kwargs) -> dict:
        return self.v012_rule.evaluate(input_data, params)
```

---

## 10. Deploy y Producción

### 10.1 Configuración de Entorno de Producción

#### Variables de Entorno
```bash
# .env para producción
LIQUIDACION_ENV=production
LIQUIDACION_LOG_LEVEL=INFO
LIQUIDATION_AUDIT_PATH=/var/audit/liquidacion/
LIQUIDATION_PARAMS_DIR=/opt/liquidacion/params/

# Security
LIQUIDATION_ENABLE_HARDWARE_ACCEL=true
LIQUIDATION_ENCRYPT_AUDIT_TRAIL=true
LIQUIDATION_MAX_MEM_USAGE=2GB
```

#### Configuración de Logging Producción
```yaml
# config/production_logging_config.yaml
version: 1
disable_existing_loggers: false

formatters:
  production:
    format: '%(asctime)s [%(levelname)s] [%(name)s] %(message)s'
    datefmt: '%Y-%m-%d %H:%M:%S'

handlers:
  file:
    class: logging.handlers.RotatingFileHandler
    filename: /var/log/liquidacion/liquidacion.log
    maxBytes: 10485760  # 10MB
    backupCount: 5
    formatter: production
    
  audit_file:
    class: logging.FileHandler
    filename: /var/log/liquidacion/audit.log
    formatter: production

loggers:
  liquidator:
    level: INFO
    handlers: [file]
    propagate: false
    
  liquidator.audit:
    level: DEBUG
    handlers: [audit_file]
    propagate: false

root:
  level: INFO
  handlers: [file]
```

### 10.2 Performance Optimization

#### Caching de Parámetros
```python
# liquidator/params/optimized_loader.py
class CachedParamsLoader:
    """Thread-safe parameter caching for production"""
    
    def __init__(self, ttl_seconds: int = 3600):
        self._cache = {}
        self._cache_timestamps = {}
        self._lock = threading.Lock()
        self.ttl = ttl_seconds
    
    def get_params(self, year: int = 2025) -> dict:
        cache_key = f'params_{year}'
        
        with self._lock:
            # Check cache and TTL
            if cache_key in self._cache:
                age = time.time() - self._cache_timestamps[cache_key]
                if age < self.ttl:
                    logger.debug(f"Cache hit for {cache_key}")
                    return self._cache[cache_key]
            
            # Load from disk
            logger.info(f"Loading params for year {year} from disk")
            params = self._load_from_disk(year)
            
            # Update cache
            self._cache[cache_key] = params
            self._cache_timestamps[cache_key] = time.time()
            
            return params
```

#### Concurrent Processing
```python
# liquidator/core/batch_processor.py
from concurrent.futures import ThreadPoolExecutor, as_completed

class BatchProcessor:
    """Process multiple liquidations in parallel"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
    
    def process_batch(self, cases: List[dict], validate_before: bool = True) -> List[dict]:
        """Process multiple cases in parallel threads"""
        if validate_before:
            self.validate_batch(cases)
        
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_case = {
                executor.submit(self._process_case, case): case 
                for case in cases
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_case):
                case = future_to_case[future]
                try:
                    result = future.result()
                    results.append({
                        "input_hash": self._hash_input(case),
                        "case_id": case.get("id", "unknown"),
                        "result": result
                    })
                except Exception as e:
                    logger.error(f"Case {case.get('id')} failed: {e}")
                    results.append({
                        "input_hash": self._hash_input(case),
                        "case_id": case.get("id", "unknown"),
                        "error": str(e)
                    })
        
        return results
```

### 10.3 Monitoring y Alerts

#### Health Check Endpoint
```python
# liquidator/monitoring/health_check.py
class HealthChecker:
    """Health check for production monitoring"""
    
    def __init__(self):
        self.checks = {
            "params_file_accessible": self._check_params_file,
            "database_connection": self._check_database,
            "disk_space": self._check_disk_space,
            "memory_usage": self._check_memory_usage
        }
    
    def check_health(self) -> dict:
        """Comprehensive health check"""
        results = {}
        overall_status = "HEALTHY"
        
        for check_name, check_function in self.checks.items():
            try:
                result = check_function()
                results[check_name] = {
                    "status": result,
                    "timestamp": datetime.now().isoformat()
                }
                if result != "PASS":
                    overall_status = "UNHEALTHY"
            except Exception as e:
                results[check_name] = {
                    "status": "ERROR",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                overall_status = "UNHEALTHY"
        
        return {
            "overall_status": overall_status,
            "checks": results,
            "service_version": __version__,
            "timestamp": datetime.now().isoformat()
        }
```

#### Metricks Collection
```python
# liquidator/monitoring/metrics.py
class MetricsCollector:
    """Collect production metrics for monitoring"""
    
    def __init__(self):
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)
    
    def count(self, metric_name: str):
        """Decorator to count method calls"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                self.counters[metric_name] += 1
                return result
            return wrapper
        return decorator
    
    def timer(self, metric_name: str):
        """Decorator to time method execution"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start
                    self.timers[metric_name].append(duration)
            return wrapper
        return decorator
    
    def get_metrics(self) -> dict:
        """Get aggregated metrics"""
        return {
            "counters": dict(self.counters),
            "timers": {
                name: {"count": len(times), "avg": sum(times)/len(times), "max": max(times)}
                for name, times in self.timers.items()
            }
        }

# Usage
@metrics.count("liquidation_requests")
@metrics.timer("liquidation_processing_time")
def process_liquidation(data: dict):
    engine = LiquidacionEngine()
    return engine.process(data)
```

### 10.4 Deployment Scripts

#### Dockerfile
```dockerfile
# Dockerfile for production deployment
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install application
RUN pip install -e .

# Setup directories
RUN mkdir -p /var/log/liquidacion /var/audit/liquidacion
RUN chmod 755 /var/log/liquidacion /var/audit/liquidacion

# Run health check
ENTRYPOINT ["python", "-m", "liquidator.monitoring.production_server"]
```

#### docker-compose.yml
```yaml
version: '3.8'
services:
  liquidacion-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - LIQUIDACION_ENV=production
      - LIQUIDACION_LOG_LEVEL=INFO
    volumes:
      - ./params:/opt/liquidacion/params:ro
      - ./audit:/var/audit/liquidacion
      - ./logs:/var/log/liquidacion
      - ./config:/opt/liquidacion/config
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
  
  monitoring:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring:/etc/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
```

---

## 11. Resumen de Desarrollo

Esta guía proporciona la base para contribuir efectivamente al Sistema de Liquidación de Nómina Colombia 2025. Los principios clave a recordar:

### Principios Fundamentales
- **Compliance primero**: Todos los cambios deben cumplir requisitos legales
- **Testing exhaustivo**: Coverage alto y tests de regresión obligatorios
- **Trazabilidad completa**: Todas las decisiones deben ser auditable
- **Performance adecuado**: Sistema debe performar bien en producción
- **Seguridad siempre**: Datos sensibles protegidos, inputs validados

### Checklist de Contribución
- [ ] Tests unitarios y de integración presentes y pasan
- [ ] Coverage alcanzado según requisitos
- [ ] Reglas de compliance actualizadas si aplica
- [ ] Documentación actualizada
- [ ] Performance validada para producción
- [ ] Revisión de seguridad completada

### Soporte
Para questions específicas de desarrollo:
- Issues en GitHub: problemas y enhancement requests
- Email técnico: development@empresa.com
- Slack: #development-liquidacion

---

**Happy coding! 🚀**
