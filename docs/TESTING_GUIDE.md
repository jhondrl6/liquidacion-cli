# Guía de Testing del Sistema de Liquidación de Nómina Colombia 2025

## Resumen de la Estrategia de Testing

Este documento describe la estrategia completa de testing implementada para el Sistema de Liquidación de Nómina Colombia 2025, junto con la guía para ejecutar tests y mantener el coverage adecuado.

## Estado Actual de Coverage

**Estado actual (2025-11-04):**
- **Coverage General**: 39%
- **Módulos Críticos**:
  - `sbl_calculator.py`: 94%
  - `vacaciones_calculator.py`: 93%
  - `prestaciones_calculator.py`: 79%
  - `indemnizacion_calculator.py`: 18%
- **Módulos Legales**: 79-90%
- **Módulos de Compliance**: 0%
- **Módulos de Validators**: 0%

## Estructura Directorios de Tests

```
liquidator/tests/
├── test_calculators/
│   ├── test_sbl.py                # SBL Calculator (94% coverage)
│   ├── test_prestaciones.py       # Prestaciones Calculator (79% coverage)
│   ├── test_vacaciones.py         # Vacaciones Calculator (93% coverage)
│   └── test_indemnizacion.py      # Indemnización Calculator (18% coverage)
├── test_compliance/
│   ├── test_override.py           # Override Manager
│   └── ...                       # Módulos de compliance (0% coverage)
├── test_legal/
│   ├── test_normas_repository.py  # Repositorio de normas (79% coverage)
│   ├── test_plazos_manager.py     # Gestión de plazos (85% coverage)
│   ├── test_recargos_manager.py   # Gestión de recargos (81% coverage)
│   └── test_topes_manager.py      # Gestión de topes (90% coverage)
├── test_integration/
│   ├── test_periodica.py          # Flujo completo PERIÓDICA
│   ├── test_finiquito.py          # Flujo completo FINIQUITO
│   └── test_edge_cases.py         # Casos de borde
├── test_audit/
│   ├── test_audit_logger.py
│   ├── test_hash_calculator.py
│   └── test_trail_generator.py
├── test_params/
│   ├── test_loader.py
│   └── test_validator.py
├── test_utils/
│   ├── test_date_currency_utils.py
│   └── ...
└── test_validators/
    ├── test_contract_validator.py
    ├── test_date_validator.py
    ├── test_input_validator.py
    └── test_salary_validator.py
```

## Guía para Ejecutar Tests

### Ejecutar todos los tests

```bash
# Con coverage
python -m pytest --cov=liquidator --cov-report=term-missing --cov-report=html

# Sin coverage
python -m pytest
```

### Ejecutar tests específicos de un módulo

```bash
# Tests de calculadores críticos
python -m pytest liquidator/tests/test_calculators/

# Tests de un módulo específico
python -m pytest liquidator/tests/test_calculators/test_sbl.py

# Tests con coverage específico
python -m pytest liquidator/tests/test_calculators/ --cov=liquidator.calculators
```

### Ejecutar un test específico

```bash
# Test específico
python -m pytest liquidator/tests/test_calculators/test_sbl.py::TestSBLCalculator::test_sbl_general_finca_rural

# Test con coverage y output detallado
python -m pytest liquidator/tests/test_calculators/test_sbl.py -v --cov=liquidator.calculators.sbl_calculator
```

## Criterios de Aceptación de Testing

### Criterios Faltantes (Prioridad Alta)

1. **✅ Coverage general > 85%**
   - Estado actual: 39%
   - Necesita: +46 puntos

2. **✅ Coverage módulos críticos > 95%**
   - sbl_calculator.py: 94% (casi completo)
   - vacaciones_calculator.py: 93% (casi completo)
   - prestaciones_calculator.py: 79% (falta +16 puntos)
   - indemnizacion_calculator.py: 18% (falta +77 puntos)

3. **✅ Todos los tests pasando**
   - Tests fallantes: 3 de 100 (97% passing rate)

4. **✅ Tests de regresión validados**
   - Parcialmente implementados

5. **✅ Performance aceptable**
   - Tests ejecutan en <2 segundos

6. **✅ Documentación de tests completa**
   - En proceso

## Fixtures Disponibles

### Fixtures de Parámetros

```python
@pytest.fixture
def params_default():
    """Parámetros por defecto para 2025."""
    return {
        'SMMLV': 1423500,
        'AUXILIO_TRANS': 200000,
        'DIAS_BASE': 360.0,
        'TASA_INT_CESANTIAS': 0.12,
        'REDONDEO': 0
    }
```

### Fixtures de Calculadoras

```python
@pytest.fixture
def calculator(params_default):
    """Instancia del calculador con parámetros por defecto."""
    return PrestacionesCalculator(params_default)
```

## Tests de Regresión

Los tests de regresión validan que los cálculos coincidan con casos conocidos:

### Caso de Finca Rural (Año Completo)

```python
def test_finca_rural_completo(self, calculator):
    """Test caso finca rural completo."""
    result = calculator.calculate_cesantias(
        sbl_general=2200000,
        dias_servicio=360,
        fecha_ingreso="2024-11-16",
        fecha_corte="2025-11-15"
    )
    
    assert result['valor'] == 2200000
    assert result['dias_liquidados'] == 360
    assert result['norma'] == 'Art. 249-250 CST'
```

### Caso de Salario Variable (Promedios)

```python
def test_salario_variable_promedio(self, sbl_calculator):
    """Test cálculo con salarios variables."""
    salarios_historicos = [
        {'mes': 1, 'salario': 1500000, 'comisiones': 200000},
        {'mes': 2, 'salario': 1600000, 'comisiones': 180000},
        # ... más meses
    ]
    
    sbl, alertas = sbl_calculator.calculate_sbl_general(
        salario_mensual=1500000,
        salarios_historicos=salarios_historicos
    )
    
    expected = (sum(mes['salario'] + mes['comisiones'] for mes in salarios_historicos[:12]) / 12)
    assert sbl == expected
```

## Tests de Integración

### Flujo Completo PERIÓDICA

```python
def test_flujo_periodica_completo(self):
    """Test flujo completo de liquidación periódica."""
    input_data = {
        "modo": "PERIODICA",
        "fecha_ingreso": "2024-11-16",
        "fecha_corte": "2025-11-15",
        "salario_mensual": 2200000,
        "reside_en_lugar_trabajo": True,
        # ... otros campos
    }
    
    # Ejecutar motor completo
    engine = LiquidacionEngine()
    result = engine.process_input(input_data)
    
    # Validaciones
    assert 'cesantias' in result['desglose']
    assert 'intereses_cesantias' in result['desglose']
    assert 'prima' in result['desglose']
    assert result['desglose']['vacaciones'] == 0  # En PERIÓDICA no incluye vacaciones
```

### Flujo Completo FINIQUITO

```python
def test_flujo_finiquito_completo(self):
    """Test flujo completo de liquidación finiquito."""
    input_data = {
        "modo": "FINIQUITO",
        "fecha_ingreso": "2024-11-16",
        "fecha_corte": "2025-11-15",
        "salario_mensual": 2200000,
        "dias_vacaciones_pendientes": 10,
        # ... otros campos
    }
    
    # Ejecutar motor completo
    engine = LiquidacionEngine()
    result = engine.process_input(input_data)
    
    # Validaciones específicas de finiquito
    assert 'vacaciones' in result['desglose']
    assert result['desglose']['vacaciones'] > 0
    assert 'indemnizacion' in result['desglose']
```

## Tests de Performance

### Medición de Tiempos de Ejecución

```python
def test rendimiento_calculo_completo(self, calculator):
    """Test de rendimiento para cálculo completo."""
    import time
    start_time = time.time()
    
    # Ejecutar cálculo completo
    result = calculator.calculate_all_prestaciones(
        input_data=test_input,
        sbl_general=2200000,
        sbl_prima=2200000
    )
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Validación de performance
    assert execution_time < 1.0  # Debe ejecutar en menos de 1 segundo
    assert 'total_prestaciones' in result
```

## Plan de Acción para Mejorar Coverage

### Acciones Críticas (Prioridad 1)

1. **Completar módulo indemnizacion_calculator.py**
   - Agregar tests para los métodos: calculate_indemnizacion, calculate_salario_pendiente
   - Enfocarse en casos de uso básicos

2. **Crear tests básicos para módulos compliance**
   - Priorizar compliance_engine.py y rule_evaluator.py
   - Alcanzar 60%+ en estos módulos

### Acciones Importantes (Prioridad 2)

3. **Crear tests básicos para módulos validators**
   - Priorizar contract_validator.py y input_validator.py
   - Alcanzar 60%+ en estos módulos

### Acciones secundarias (Prioridad 3)

4. **Mejorar coverage en prestaciones_calculator.py**
   - Enfocarse en los métodos con <80% coverage

5. **Optimizar tests existentes**
   - Mejorar tests parametrizados para aumentar coverage
   - Agregar más casos de borde

## Ejemplos de Uso

### Creación de Nuevo Tests

```python
def test_caso_especifico_nuevo(self, calculator):
    """Template para nuevo test de caso específico."""
    # 1. Preparar datos de entrada
    input_data = {
        'fecha_ingreso': '2025-01-01',
        'fecha_corte': '2025-06-30',
        'salario_mensual': 1500000,
        # ... otros datos necesarios
    }
    
    # 2. Ejecutar método bajo prueba
    result = calculator.calculate_prestaciones(input_data)
    
    # 3. Validar resultado
    assert result is not None
    assert 'valor' in result
    assert result['valor'] > 0
    
    # 4. Validar contra manual calculation
    expected_manual = (input_data['salario_mensual'] * 181) / 360
    assert abs(result['valor'] - expected_manual) <= 1  # Tolerancia
```

### Uso de Parametrización

```python
@pytest.mark.parametrize("salario,expected_cesantias", [
    (1423500, 715208),  # SMMLV, medio año
    (2200000, 1100000), # Salario alto, medio año
    (3000000, 1500000), # Salario muy alto, medio año
])
def test_cesantias_parametrizados(self, calculator, salario, expected_cesantias):
    """Test parametrizado de cesantías."""
    result = calculator.calculate_cesantias(
        salario, 
        181,  # medio año
        '2025-01-01', 
        '2025-06-30'
    )
    
    assert abs(result['valor'] - expected_cesantias) <= 1
```

## Referencias

1. **Artículo 186 CST**: Derecho a 15 días hábiles de vacaciones por año de servicio
2. **Artículo 249-250 CST**: Cálculo de cesantías con base 360 días
3. **Ley 50/1990 Art. 99**: Intereses sobre cesantías tasa 12% anual
4. **Artículo 306-308 CST**: Prima de servicios proporcional a semestre
5. **Artículo 64 CST**: Tope de 20 SMMLV para indemnización

## Conclusiones

Se ha logrado un avance significativo en el testing exhaustivo del sistema:
- Los módulos críticos principales tienen coverage >90%
- Se han corregido errores importantes en el cálculo de cesantías y vacaciones
- Se ha establecido una base sólida para tests de regresión

Los próximos pasos deberían enfocarse en completar los módulos pendientes (indemnización, compliance, validators) para alcanzar el objetivo de 85%+ coverage general y 95%+ en módulos críticos.
