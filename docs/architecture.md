# Documentación de Arquitectura
## Sistema de Liquidación de Nómina Colombia 2025

### Versión: 1.0.0
### Fecha: 2025-11-04

---

## 1. Visión General de la Arquitectura

El Sistema de Liquidación de Nómina Colombia 2025 implementa una arquitectura por capas modular y escalable diseñada específicamente para cumplir con los requisitos de precisión legal, trazabilidad y mantenibilidad en el cálculo de prestaciones sociales colombianas.

### 1.1 Principios de Diseño

- **Modularidad**: Cada componente tiene una responsabilidad única y bien definida
- **Separación de Preocupaciones**: Lógica de negocio separada de presentación y persistencia
- **Extensibilidad**: La arquitectura permite añadir nuevas prestaciones y normas sin modificar componentes existentes
- **Trazabilidad**: Cada cálculo y validación genera evidencia audititable
- **Testabilidad**: Cada módulo puede ser probado de forma aislada

---

## 2. Diagrama de Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLI LAYER                                   │
│                        (bin/liquidar.py)                                 │
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────────────┐
│                            CORE LAYER                                     │
│  ┌─────────────────────┬─────────────────────┬─────────────────────────┐
│  │   Input Parser       │ Liquidación Engine  │  Workflow Orchestrator  │
│  │                      │                     │                         │
│  │ • Parseo CLI/JSON    │ • Orquestación      │ • Flujo PERIÓDICA      │
│  │ • Validación inicial │ • Coordinación      │ • Flujo FINIQUITO       │
│  │ • Normalización      │ • Manejo errores    │ • Diferencias modo     │
│  └─────────────────────┴─────────────────────┴─────────────────────────┘
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────────────┐
│                         BUSINESS LOGIC LAYER                             │
│  ┌─────────────┬───────────────┬─────────────┬─────────────────────────┐
│  │  Calculators│  Validators   │   Legal     │   Compliance            │
│  │             │               │             │                         │
│  │ • SBL       │ • Input       │ • Normas    │ • Rules Engine          │
│  │ • Prestamos │ • Contract    │ • Plazos    │ • Validation Engine     │
│  │ • Vacaciones│ • Date        │ • Topes     │ • Override Manager      │
│  │ • Indemnizac│ • Salary      │ • Recargos  │ • Report Generator      │
│  └─────────────┴───────────────┴─────────────┴─────────────────────────┘
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────────────┐
│                      DATA & CONFIGURATION LAYER                           │
│  ┌─────────────┬───────────────┬─────────────┬─────────────────────────┐
│  │   Parameters│    Templates  │    Utils    │   Audit                 │
│  │             │               │             │                         │
│  │ • 2025.json │ • Markdown    │ • Date      │ • Hash Calculator       │
│  │ • normas    │ • PDF         │ • Currency  │ • Trail Generator       │
│  │ • plazos    │ • Styles      │ • File      │ • Audit Logger          │
│  │ • schema    │ • Partials    │ • Error     │ • Version Manager       │
│  └─────────────┴───────────────┴─────────────┴─────────────────────────┘
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────────────┐
│                         OUTPUT LAYER                                     │
│  ┌─────────────┬───────────────┬─────────────────────────────────────────┐
│  │   JSON Gen  │  Markdown Gen │          PDF Generator                  │
│  │             │               │                                         │
│  │ • Schema    │ • Templates   │ • WeasyPrint                          │
│  │ • Hash      │ • Rendering   │ • CSS Styling                        │
│  │ • Validation│ • Formatting  │ • Headers/Footers                     │
│  └─────────────┴───────────────┴─────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Arquitectura Detallada por Capas

### 3.1 Capa de Presentación (CLI Layer)

#### Componentes Principales

**bin/liquidar.py**
- Entry point principal del sistema
- Parseo de argumentos CLI con argparse
- Manejo de modos especiales (test-run, compliance-check-only)
- Presentación de resultados en consola

#### Patrones Utilizados

- **Command Pattern**: Cada modo de ejecución se implementa como un comando específico
- **Strategy Pattern**: Diferentes estrategias de procesamiento según el modo

#### Interacciones
- Recibe entrada mediante argumentos CLI o archivos JSON
- Invoca al motor principal del sistema
- Presenta resultados y maneja errores de forma user-friendly

---

### 3.2 Capa de Negocio (Core Layer)

#### Componentes Principales

**liquidator/core/engine.py**
```python
class LiquidacionEngine:
    """Motor principal de orquestación del sistema"""
    
    def __init__(self):
        self.params_loader = ParamsLoader()
        self.input_validator = InputValidator()
        self.sbl_calculator = SBLCalculator()
        self.prestaciones_calculator = PrestacionesCalculator()
        self.compliance_engine = ComplianceEngine()
        self.output_generator = OutputGenerator()
    
    def process(self, input_data: Dict) -> Dict:
        """Procesa una liquidación completa"""
        # 1. Cargar parámetros
        params = self.params_loader.load_params()
        
        # 2. Validar entrada
        self.input_validator.validate(input_data)
        
        # 3. Calcular SBLs
        sbls = self.sbl_calculator.calculate_all(input_data, params)
        
        # 4. Calcular prestaciones
        prestaciones = self.prestaciones_calculator.calculate_all(
            input_data, sbls, params
        )
        
        # 5. Ejecutar compliance
        compliance = self.compliance_engine.run_validations(
            input_data, sbls, prestaciones, params
        )
        
        # 6. Generar output
        return self.output_generator.generate(
            input_data, sbls, prestaciones, compliance
        )
```

**liquidator/core/input_parser.py**
- Parsea y normaliza datos de entrada
- Convierte argumentos CLI a formato interno
- Aplica valores por defecto

**liquidator/core/workflow_orchestrator.py**
```python
class WorkflowOrchestrator:
    """Gestiona flujos específicos según modo de liquidación"""
    
    def execute_periodica_workflow(self, input_data, params):
        """Flujo específico para liquidación periódica"""
        # 1. Calcular SBLs
        sbl_general = self.sbl_calculator.calculate_sbl_general(...)
        sbl_vacaciones = self.sbl_calculator.calculate_sbl_vacaciones(...)
        
        # 2. Calcular prestaciones
        cesantias = self.prestaciones_calculator.calculate_cesantias(...)
        intereses = self.prestaciones_calculator.calculate_intereses_cesantias(...)
        prima = self.prestaciones_calculator.calculate_prima(...)
        
        # 3. Excluir vacaciones en modo PERIÓDICA
        vacaciones = {"valor": 0, "nota": "No aplica en modo PERIÓDICA"}
        
        return {
            "cesantias": cesantias,
            "intereses": intereses,
            "prima": prima,
            "vacaciones": vacaciones
        }
```

#### Patrones Utilizados

- **Orchestrator Pattern**: Centraliza la coordinación de componentes
- **Template Method Pattern**: Define el flujo general con pasos variables
- **Factory Pattern**: Crea componentes según configuración

---

### 3.3 Capa de Lógica de Negocio (Business Logic Layer)

#### 3.3.1 Módulo Calculators

**liquidator/calculators/sbl_calculator.py**
```python
class SBLCalculator:
    """Calculador de Salario Base de Liquidación"""
    
    def calculate_sbl_general(self, input_data, params):
        """
        Calcula SBL para cesantías, intereses y prima
        
        Fórmula: Salario + Comisiones + Extras + Bonificaciones [+ Auxilio]
        """
        sbl = (
            input_data['salario_mensual'] +
            input_data.get('comisiones_promedio_mensual', 0) +
            input_data.get('horas_extras_promedio_mensual', 0) +
            input_data.get('bonificaciones_promedio_mensual', 0)
        )
        
        # Aplicar reglas de auxilio
        return self._apply_auxilio_rules(sbl, input_data, params)
    
    def calculate_sbl_vacaciones(self, input_data, params):
        """
        Calcula SBL para vacaciones
        
        Fórmula: Salario + Comisiones (excluye extras y auxilios)
        """
        return (
            input_data['salario_mensual'] +
            input_data.get('comisiones_promedio_mensual', 0)
        )
```

**liquidator/calculators/prestaciones_calculator.py**
```python
class PrestacionesCalculator:
    """Calculador de prestaciones sociales principales"""
    
    def calculate_cesantias(self, sbl_general, dias_servicio, params):
        """
        Cálculo de cesantías - Art. 249-250 CST
        
        Fórmula: (SBL_GENERAL × días) / 360
        """
        valor = (sbl_general * dias_servicio) / params['DIAS_BASE']
        
        return {
            'valor': round(valor, params['REDONDEO']),
            'dias_liquidados': dias_servicio,
            'formula': f'({sbl_general} × {dias_servicio}) / {params["DIAS_BASE"]}',
            'norma': 'Art.249-250 CST',
            'plazo_pago_legal': self._calcular_plazo_cesantias()
        }
    
    def calculate_intereses_cesantias(self, cesantias, dias_servicio, params):
        """
        Cálculo de intereses sobre cesantías - Ley 50/1990 Art.99
        
        Fórmula: (Cesantías × días × 0.12) / 360
        """
        valor = (cesantias * dias_servicio * params['TASA_INT_CESANTIAS']) / params['DIAS_BASE']
        
        return {
            'valor': round(valor, params['REDONDEO']),
            'dias_liquidados': dias_servicio,
            'tasa_aplicada': params['TASA_INT_CESANTIAS'],
            'formula': f'({cesantias} × {dias_servicio} × {params["TASA_INT_CESANTIAS"]}) / {params["DIAS_BASE"]}',
            'norma': 'Ley 50/1990 Art.99',
            'plazo_pago_legal': self._calcular_plazo_intereses()
        }
```

#### 3.3.2 Módulo Validators

**liquidator/validators/input_validator.py**
```python
class InputValidator:
    """Validador de datos de entrada"""
    
    def validate(self, input_data):
        """Valida estructura y valores básicos"""
        # Validar campos requeridos
        required_fields = [
            'modo', 'fecha_ingreso', 'fecha_corte', 
            'salario_mensual', 'reside_en_lugar_trabajo'
        ]
        
        for field in required_fields:
            if field not in input_data:
                raise ValidationError(f"Campo requerido faltante: {field}")
        
        # Validar modo
        if input_data['modo'] not in ['PERIODICA', 'FINIQUITO']:
            raise ValidationError("Modo inválido. Debe ser 'PERIODICA' o 'FINIQUITO'")
        
        # Validar fechas
        self._validate_dates(input_data['fecha_ingreso'], input_data['fecha_corte'])
        
        # Validar salario
        if input_data['salario_mensual'] <= 0:
            raise ValidationError("Salario mensual debe ser mayor a 0")
```

**liquidator/validators/contract_validator.py**
```python
class ContractValidator:
    """Validador de tipos de contrato"""
    
    def validate_contract_type(self, contract_type):
        """
        Art. 23 CST - Solo se liquidan prestaciones para contratos laborales
        """
        forbidden_types = ['prestacion_servicios', 'servicios_profesionales']
        
        if contract_type.lower() in forbidden_types:
            raise ComplianceError(
                "Contrato de prestación de servicios no aplica para liquidación de prestaciones",
                rule_ref="Art. 23 CST",
                blocking=True
            )
```

---

### 3.4 Capa de Cumplimiento Legal (Compliance Layer)

#### Componentes Principales

**liquidator/compliance/compliance_engine.py**
```python
class ComplianceEngine:
    """Motor de cumplimiento legal con evaluación de reglas"""
    
    VALIDATION_RULES = {
        'V001': 'Parámetros oficiales 2025',
        'V002': 'Contrato válido',
        'V003': 'Auxilio transporte aplicado correctamente',
        'V004': 'Fórmulas de cesantías correctas',
        'V005': 'Intereses de cesantías tasa correcta',
        'V006': 'Prima semestre proporcional',
        'V007': 'Vacaciones excluidas en periódica',
        'V008': 'Plazos de pago documentados',
        'V009': 'Sustento legal presente',
        'V010': 'Hashes y versionamiento'
    }
    
    def run_validations(self, input_data, sbls, prestaciones, params):
        """Ejecuta todas las validaciones de cumplimiento"""
        results = []
        
        for rule_id, rule_description in self.VALIDATION_RULES.items():
            result = self.rule_evaluator.evaluate(
                rule_id, input_data, sbls, prestaciones, params
            )
            results.append(result)
        
        # Determinar estado final
        compliance_status = self._determine_status(results)
        
        # Generar reporte
        report = self.report_generator.create_report(results, compliance_status)
        
        # Manejar bloqueos si aplica
        if compliance_status == 'NO_GO' and input_data.get('enforce-compliance', True):
            return self._handle_blocking_compliance(report, input_data)
        
        return report
```

**liquidator/compliance/rule_evaluator.py**
```python
class RuleEvaluator:
    """Evaluador individual de reglas de cumplimiento"""
    
    def evaluate(self, rule_id, input_data, sbls, prestaciones, params):
        """Evalúa una regla específica"""
        
        if rule_id == 'V001':
            return self._eval_params_2025(rule_id, params)
        elif rule_id == 'V002':
            return self._eval_contract_valid(rule_id, input_data)
        elif rule_id == 'V003':
            return self._eval_auxilio_transporte(rule_id, input_data, sbls)
        # ... más reglas
        
    def _eval_params_2025(self, rule_id, params):
        """V001: Parámetros oficiales 2025 presentes y consistentes"""
        
        expected_params = {
            'SMMLV': 1423500,
            'AUXILIO_TRANS': 200000,
            'TASA_INT_CESANTIAS': 0.12,
            'DIAS_BASE': 360.0
        }
        
        evidence = []
        check_status = 'PASS'
        
        for param, expected_value in expected_params.items():
            if params.get(param) != expected_value:
                check_status = 'FAIL'
                evidence.append(f"{param}: {params.get(param)} ≠ {expected_value}")
            else:
                evidence.append(f"{param}: {params.get(param)} = {expected_value}")
        
        return {
            'id': rule_id,
            'description': self.VALIDATION_RULES[rule_id],
            'result': check_status,
            'evidence': evidence,
            'rule_ref': ['Decreto 1572/2024', 'Decreto 1573/2024'],
            'details': 'Validación de parámetros oficiales para año 2025'
        }
```

---

### 3.5 Capa de Datos y Configuración

#### Componentes Principales

**liquidator/params/params_loader.py**
```python
class ParamsLoader:
    """Cargador de parámetros legales oficiales"""
    
    def load_params(self, year=2025):
        """Carga parámetros del año especificado"""
        params_file = f'params/{year}.json'
        
        if not os.path.exists(params_file):
            raise FileNotFoundError(f"Archivo de parámetros no encontrado: {params_file}")
        
        with open(params_file, 'r', encoding='utf-8') as f:
            params = json.load(f)
        
        # Validar schema
        self._validate_schema(params)
        
        return params
    
    def _validate_schema(self, params):
        """Valida schema de parámetros"""
        with open('params/schema.json', 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        jsonschema.validate(instance=params, schema=schema)
```

**liquidator/legal/normas_repository.py**
```python
class NormasRepository:
    """Repositorio de normas legales y referentes"""
    
    def __init__(self):
        self.normas = self._load_normas()
    
    def get_norma(self, norma_id):
        """Obtiene información de una norma por ID"""
        return self.normas.get(norma_id)
    
    def get_norma_text(self, norma_id):
        """Obtiene texto relevante de una norma"""
        norma = self.get_norma(norma_id)
        return norma.get('texto_relevante') if norma else None
    
    def search_by_keyword(self, keyword):
        """Busca normas por palabra clave"""
        results = []
        for norma_id, norma_data in self.normas.items():
            if keyword.lower() in norma_data.get('descripcion', '').lower():
                results.append({
                    'id': norma_id,
                    'nombre': norma_data.get('nombre'),
                    'descripcion': norma_data.get('descripcion')
                })
        return results
```

---

### 3.6 Capa de Auditoría

#### Componentes Principales

**liquidator/audit/trail_generator.py**
```python
class TrailGenerator:
    """Generador de audit trail completo para trazabilidad"""
    
    def generate_audit_trail(self, input_data, output_data, compliance_report):
        """Genera trail completo de auditoría"""
        
        trail = {
            'meta': {
                'timestamp': datetime.now().isoformat(),
                'generator_version': '1.0.0',
                'session_id': str(uuid.uuid4()),
                'execution_time_ms': self._measure_execution_time()
            },
            'integrity': {
                'input_hash': self.hash_calculator.calculate(input_data),
                'output_hash': self.hash_calculator.calculate(output_data),
                'algorithm': 'SHA256'
            },
            'params_version': {
                'version': '2025-10-31',
                'source': 'params/2025.json'
            },
            'compliance': {
                'status': compliance_report['compliance_status'],
                'summary': compliance_report['summary'],
                'rule_results': [r['id'] for r in compliance_report['checks']],
                'blocking_failures': compliance_report.get('blocking_failures', [])
            },
            'data_flow': {
                'input_structure': self._analyze_structure(input_data),
                'output_structure': self._analyze_structure(output_data),
                'transformation_steps': self._log_transformation_steps()
            }
        }
        
        # Guardar trail en directorio de auditoría
        self._save_trail(trail)
        
        return trail['meta']['session_id']
```

---

## 4. Flujo de Ejecución Detallado

### 4.1 Flujo Periódico (Modo PERIODICA)

```
1. INPUT PARSING
   └─ Parsear CLI/JSON → InputData structure

2. PARAMS LOADING
   └─ Cargar params/2025.json → Params structure

3. INPUT VALIDATION
   ├─ Validar estructura JSON
   ├─ Validar tipo de contrato
   ├─ Validar coherencia fechas
   └─ Validar rangos salariales

4. SBL CALCULATION
   ├─ Calcular SBL_GENERAL
   ├─ Calcular SBL_VACACIONES
   └─ Aplicar reglas auxilio transporte

5. PRESTACIONES CALCULATION
   ├─ Calcular días servicio
   ├─ Calcular cesantías
   ├─ Calcular intereses sobre cesantías
   └─ Calcular prima semestral

6. COMPLIANCE VALIDATION
   ├─ Ejecutar reglas V001-V010
   ├─ Generar evidence de cada validación
   └─ Determinar estado GO/NO_GO

7. DECISION POINT
   ├─ Si NO_GO + enforce-compliance = True → Abortar
   ├─ Si NO_GO + human-override = True → Continuar con warning
   └─ Si GO → Continuar

8. OUTPUT GENERATION
   ├─ Generar JSON estructurado
   ├─ Calcular hashes
   ├─ Generar Markdown
   └─ Generar PDF (opcional)

9. AUDIT TRAIL
   ├─ Generar trail completo
   ├─ Calcular hashes de input/output
   └─ Guardar en audit/trails/

10. CLI OUTPUT
    └─ Mostrar resumen y rutas de archivos
```

### 4.2 Flujo de Finiquito (Modo FINIQUITO)

Similar al flujo periódico pero con adiciones en:

- **Paso 5**: Incluir cálculo de vacaciones (compensación) e indemnización
- **Paso 7**: Validar pago inmediato (Art.65 CST)
- **Paso 8**: Incluir campos adicionales en output

---

## 5. Patrones de Diseño Utilizados

### 5.1 Patrones Creacionales

- **Factory Pattern**: Creación de calculadores según modo
- **Builder Pattern**: Construcción de outputs complejos (JSON, PDF)

### 5.2 Patrones Estructurales

- **Adapter Pattern**: Adaptación de diferentes formatos de entrada
- **Facade Pattern**: LiquidacionEngine como fachada del sistema

### 5.3 Patrones Comportamiento

- **Strategy Pattern**: Estrategias de cálculo según tipo de contrato
- **Command Pattern**: Modos especiales de CLI (test-run, compliance-check-only)
- **Observer Pattern**: Sistema de auditoría y logging
- **Template Method Pattern**: Flujo general con pasos específicos

---

## 6. Decisiones de Diseño Importantes

### 6.1 Separación de Lógica de Negocio

La lógica de cálculo está completamente separada de presentación y persistencia. Esto permite:
- Testing unitario aislado de cada componente
- Reutilización de componentes en diferentes contextos
- Mantenimiento simplificado de fórmulas legales

### 6.2 Sistema de Validación por Capas

Las validaciones se distribuyen en múltiples capas:
- **Input validators**: Validación básica de datos
- **Business validators**: Validación de reglas de negocio
- **Compliance validators**: Validación legal exhaustiva

### 6.3 Arquitectura Basada en Componentes

Cada módulo es un componente autocontenido con interfaces bien definidas:
- Dependencies Injection para testeabilidad
- Interfaces contractuales claras
- Implementaciones swappable cuando aplica

---

## 7. Extension Points y Extensibilidad

### 7.1 Nuevas Prestaciones

Para añadir nuevas prestaciones:

1. Extender `PrestacionesCalculator` con nuevo método
2. Añadir regla de compliance específica si aplica
3. Actualizar schema de output si necesario
4. Añadir tests unitarios

### 7.2 Nuevas Normas Legales

Para actualizar normativa:

1. Actualizar archivos en `params/` (2025.json, normas.json)
2. Validar contra schema existente
3. Añadir reglas de compliance si necesario
4. Actualizar referencia legal en calculadores

### 7.3 Nuevos Formatos de Salida

Para añadir nuevo formato:

1. Crear nuevo generador en `liquidator/output/`
2. Seguir patrón existente (Template Method)
3. Registrar en OutputGenerator
4. Añadir opción en CLI

---

## 8. Performance y Optimización

### 8.1 Caching de Parámetros

Los parámetros legales se cargan una vez por sesión y se cachean:

```python
class ParamsLoader:
    def __init__(self):
        self._cache = {}
    
    def load_params(self, year=2025):
        cache_key = f'params_{year}'
        if cache_key not in self._cache:
            self._cache[cache_key] = self._load_params(year)
        return self._cache[cache_key]
```

### 8.2 Lazy Loading

Componentes pesados (PDF generator) se cargan solo cuando se necesitan:

```python
class OutputGenerator:
    def generate_pdf(self, data):
        if not hasattr(self, '_pdf_generator'):
            from liquidator.output.pdf_generator import PDFGenerator
            self._pdf_generator = PDFGenerator()
        return self._pdf_generator.generate(data)
```

---

## 9. Manejo de Errores y Resiliencia

### 9.1 Jerarquía de Excepciones

```python
class LiquidacionError(Exception): pass
class ValidationError(LiquidacionError): pass
class ComplianceError(LiquidacionError): pass
class CalculationError(LiquidacionError): pass
class OutputGenerationError(LiquidacionError): pass
```

### 9.2 Estrategias de Recuperación

- **Validation Errors**: Terminar ejecución con mensaje descriptivo
- **Compliance Errors**: Generar reporte detallado y terminar según política
- **Calculation Errors**: Intentar recuperarse con valores por defecto si es seguro
- **Output Errors**: Generar JSON como fallback si PDF falla

---

## 10. Testing y Calidad

### 10.1 Estrategia de Testing

- **Unit Tests**: Cada módulo/probabilidad en aislamiento
- **Integration Tests**: Flujos completos end-to-end
- **Compliance Tests**: Cada regla legal individualmente
- **Performance Tests**: Casos de uso extensos y límites

### 10.2 Coverage Targets

- **Módulos Críticos** (calculators, compliance): >95%
- **Módulos Core** (engine, validators): >90%
- **General del Sistema**: >85%

---

## 11. Evolución y Roadmap de Arquitectura

### 11.1 Version 1.0
- Arquitectura actual implementada
- Soporte para PERIÓDICA y FINIQUITO
- Compliance con 10 reglas básicas

### 11.2 Version 1.1 (Próximo Release)
- Interfaz web administrativa
- Sistema de multi-tenancy
- API REST para integraciones
- Exportación a formatos adicionales (Excel)

### 11.3 Version 2.0
- Sistema de plugins para extensiones
- Motor de reglas configurable
- Integración con sistemas de nómina
- Validación automática contra normativa actualizada

---

## 12. Consideraciones de Seguridad

### 12.1 Manejo de Datos Sensibles

- No se persisten datos personales en logs
- Hash de inputs/outputs para integridad sin exponer datos
- Opcional encryption en entorno de producción

### 12.2 Integridad de Cálculos

- Validación cruzada de fórmulas
- Hashing de resultados para detección de manipulación
- Versionamiento de parámetros para reproducibilidad

---

## 13. Resumen de Decisiones Arquitectónicas Clave

| Decisión | Racional | Impacto |
|----------|----------|---------|
| Arquitectura por capas | Separación clara de responsabilidades | Mantenibilidad y testability |
| Compliance como componente propio | Complejidad legal significativa | Validación legal garantizada |
| Sistemas de hash y auditoría | Requerimientos de trazabilidad legal | Reproducibilidad completa |
| Modularidad de calculadores | Facilitar extensión a nuevas prestaciones | Mantenimiento simplificado |
| Template-based outputs | Consistencia en documentos generados | Profesionalismo y escalabilidad |

Esta arquitectura proporciona una base sólida y extensible para el sistema, garantizando cumplimiento legal, mantenibilidad y escalabilidad a largo plazo.
