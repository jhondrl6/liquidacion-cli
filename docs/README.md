# Tests - Sistema de Liquidacion de Nomina

## Estructura de Tests

```
liquidator/tests/
├── __init__.py
├── README.md
├── fixtures/               # Datos de prueba compartidos
│   └── params_test.json   # Parametros de prueba
└── test_params/           # Tests del modulo de parametros
    ├── __init__.py
    ├── test_loader.py     # Tests de ParamsLoader
    ├── test_validator.py  # Tests de ParamsValidator
    └── test_versioning.py # Tests de ParamsVersioning
```

## Ejecutar Tests

### Instalar dependencias de testing

```powershell
pip install pytest pytest-cov jsonschema
```

### Ejecutar todos los tests

```powershell
# Desde el directorio raiz del proyecto
pytest liquidator/tests/

# Con output verbose
pytest liquidator/tests/ -v

# Con coverage
pytest liquidator/tests/ --cov=liquidator.params --cov-report=html
```

### Ejecutar tests especificos

```powershell
# Solo tests de params
pytest liquidator/tests/test_params/

# Solo test_loader
pytest liquidator/tests/test_params/test_loader.py

# Test especifico
pytest liquidator/tests/test_params/test_loader.py::TestLoad::test_load_without_validation
```

## Cobertura de Tests - Sesion 1

### Modulo: liquidator.params

- **ParamsLoader**: Carga de parametros desde JSON
  - Inicializacion con/sin validator
  - Resolucion de paths
  - Carga de archivos
  - Manejo de errores (archivo no encontrado, JSON invalido)
  - Carga con validacion opcional

- **ParamsValidator**: Validacion de parametros contra schema
  - Validacion con jsonschema (si esta instalado)
  - Carga de schema desde archivo
  - Manejo de errores de validacion
  - Graceful degradation sin jsonschema

- **ParamsVersioning**: Versionamiento y trazabilidad
  - Calculo de hashes SHA256 (archivos y datos)
  - Registro de versiones
  - Verificacion de integridad
  - Serializacion a diccionario

## Fixtures de Prueba

### params_test.json
Parametros de prueba basicos para testing unitario:
- SMMLV 2025: $1,423,500
- Auxilio transporte: $200,000
- Tasa interes cesantias: 12%
- Topes y limites configurados

## Criterios de Aceptacion - Sesion 1.5

- [ ] Todos los tests de params pasan
- [ ] Coverage > 85% en modulo params
- [ ] Tests verifican carga correcta de parametros 2025
- [ ] Tests verifican validacion de schema funcional
- [ ] Tests verifican manejo de errores
- [ ] Tests verifican calculo de hashes

## Proximos Tests (Sesiones Futuras)

- **test_validators/**: Tests de validadores de entrada (Sesion 2)
- **test_utils/**: Tests de utilidades (Sesion 2)
- **test_legal/**: Tests del modulo legal (Sesion 3)
- **test_calculators/**: Tests de calculadores (Sesiones 4-6)
- **test_compliance/**: Tests de cumplimiento legal (Sesiones 7-8)
- **test_core/**: Tests del motor principal (Sesion 10)
- **test_output/**: Tests de generadores de salida (Sesiones 11-12)
- **test_audit/**: Tests de auditoria (Sesion 9)
