# Documentación de Casos de Prueba - Prestaciones Sociales

## Propósito

Este directorio contiene casos de prueba documentados para validar el correcto funcionamiento del calculador de prestaciones sociales según la normativa laboral colombiana.

## Estructura de Casos

Cada caso incluye:

1. **ID único**: Identificador del caso (CASO_001, CASO_002, etc.)
2. **Nombre descriptivo**: Título que resume el escenario
3. **Descripción**: Explicación detallada del caso
4. **Input**: Datos de entrada (fechas, SBL, etc.)
5. **Expected**: Resultados esperados con fórmulas
6. **Notas**: Observaciones especiales o advertencias

## Casos Implementados

### CASO_001: Finca rural - año completo
**Escenario típico**: Trabajador de finca con año completo de servicio.
- **Días**: 365
- **Cesantías**: 2.200.000 COP
- **Intereses**: 264.000 COP
- **Prima**: 843.333 COP (segundo semestre parcial)

### CASO_002: Medio año - primer semestre completo
**Semestre completo**: Trabajador que labora todo el primer semestre.
- **Días**: 181
- **Validación**: Prima coincide con cesantías proporcionales

### CASO_003: Periodo parcial - 90 días
**Cuarto de año**: Caso con números exactos (sin decimales).
- **Días**: 90
- **Validación**: Valores exactos de 500.000 para cesantías y prima

### CASO_004: Salario mínimo - año completo
**SMMLV 2025**: Caso común con salario mínimo legal.
- **SBL**: 1.423.500 COP
- **Validación**: Cálculos proporcionales al SMMLV

### CASO_005: Un día de trabajo
**Caso extremo**: Validación de precisión con un solo día.
- **Días**: 1
- **Tolerancia**: ±1 peso por redondeo
- **Validación**: Manejo correcto de decimales

### CASO_006: Año bisiesto completo
**366 días**: Validación de año bisiesto (2024).
- **Días**: 366
- **Validación**: Cesantías mayores que año normal

### CASO_007: Ingreso mitad de semestre
**Proporcionalidad**: Ingreso el 15-Mar, corte 30-Jun.
- **Prima**: 108 días de 181 posibles
- **Validación**: Proporcionalidad correcta

### CASO_008: Salario alto - ejecutivo
**20 SMMLV**: Validación con salarios ejecutivos.
- **SBL**: 28.470.000 COP
- **Validación**: Escalamiento proporcional

### CASO_009: Dos días de trabajo
**Caso mínimo realista**: Validación de precisión.
- **Días**: 2
- **Validación**: Redondeos significativos

### CASO_010: Periodo que cruza año
**Cambio de año**: Ingreso en diciembre, corte en enero.
- **Validación**: Prima solo cuenta días del semestre de corte

## Uso de los Casos

### En Tests Unitarios
```python
import json

# Cargar casos
with open('prestaciones_cases.json', 'r') as f:
    casos = json.load(f)

# Iterar sobre casos
for caso in casos['casos']:
    result = calculator.calculate_cesantias(
        sbl_general=caso['input']['sbl_general'],
        dias_servicio=caso['expected']['dias_servicio'],
        fecha_ingreso=caso['input']['fecha_ingreso'],
        fecha_corte=caso['input']['fecha_corte']
    )
    
    # Validar con tolerancia
    assert abs(result['valor'] - caso['expected']['cesantias']['valor']) <= 1
```

### En Validación Manual
```bash
# Ejecutar tests con verbose
pytest test_prestaciones.py -v

# Ejecutar solo caso específico
pytest test_prestaciones.py -k "CASO_001"

# Ejecutar con coverage
pytest test_prestaciones.py --cov=liquidator.calculators.prestaciones_calculator
```

## Tolerancias y Redondeos

- **Redondeo estándar**: 0 decimales (pesos enteros)
- **Tolerancia**: ±1 peso para casos con decimales significativos
- **Método**: ROUND_HALF_UP (banqueo)

## Referencias Legales

### Cesantías
- **Norma**: Art. 249-250 CST
- **Fórmula**: `(SBL × días) / 360`
- **Plazo**: 14 de febrero año siguiente

### Intereses sobre Cesantías
- **Norma**: Ley 50/1990 Art. 99
- **Fórmula**: `(Cesantías × días × 0.12) / 360`
- **Tasa**: 12% anual
- **Plazo**: 31 de enero año siguiente

### Prima de Servicios
- **Norma**: Art. 306-308 CST
- **Fórmula**: `(SBL × días_semestre) / 360`
- **Plazos**: 30-Jun (1er semestre), 20-Dic (2do semestre)

## Validación de Fórmulas

Cada caso incluye la fórmula exacta usada para facilitar:
1. Auditoría manual de cálculos
2. Reproducibilidad de resultados
3. Trazabilidad legal

## Mantenimiento

Al actualizar parámetros legales (ej. SMMLV 2026):
1. Actualizar `parametros_2025` en el JSON
2. Recalcular casos afectados
3. Ejecutar suite completa de tests
4. Documentar cambios en changelog

## Preguntas Frecuentes

**¿Por qué tolerancia de ±1 peso?**
Debido a redondeos internos con Decimal. Es aceptable legalmente.

**¿Cómo se calculan días en semestre?**
Se toma el semestre de la fecha de corte y se cuentan días desde:
- MAX(fecha_ingreso, inicio_semestre) hasta
- MIN(fecha_corte, fin_semestre)

**¿Qué pasa si hay 0 días en el semestre?**
El calculador retorna valor 0 con advertencia en metadata.

## Contacto

Para reportar inconsistencias o sugerir nuevos casos:
- Crear issue en el repositorio
- Incluir: caso de prueba, resultado esperado, resultado obtenido