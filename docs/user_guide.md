# Guía de Usuario
## Sistema de Liquidación de Nómina Colombia 2025

### Versión: 1.0.0
### Fecha: 2025-11-04

---

## Tabla de Contenidos

1. [Instalación](#1-instalación)
2. [Conceptos Básicos](#2-conceptos-básicos)
3. [Uso Rápido](#3-uso-rápido)
4. [Modos de Liquidación](#4-modos-de-liquidación)
5. [Argumentos de Línea de Comandos](#5-argumentos-de-línea-de-comandos)
6. [Ejemplos Prácticos](#6-ejemplos-prácticos)
7. [Interpretación de Resultados](#7-interpretación-de-resultados)
8. [Solución de Problemas](#8-solución-de-problemas)
9. [Preguntas Frecuentes](#9-preguntas-frecuentes)

---

## 1. Instalación

### 1.1 Requisitos Previos

- **Python 3.8+** instalado en el sistema operativo
- **Acceso a línea de comandos** (Terminal, PowerShell, CMD)
- **Permisos de escritura** en directorio de instalación

### 1.2 Proceso de Instalación

#### Opción 1: Instalación desde Repositorio Git

```bash
# Clonar el repositorio
git clone https://github.com/usuario/liquidacion_cli.git
cd liquidacion_cli

# Instalar dependencias
pip install -r requirements.txt

# Instalar el paquete en modo desarrollo
pip install -e .
```

#### Opción 2: Descarga Manual

1. Descargar archivos del proyecto desde el repositorio
2. Descomprimir en directorio de elección
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Agregar directorio `bin/` al PATH del sistema

### 1.3 Verificación de Instalación

```bash
# Verificar comando disponible
liquidar --help

# Verificar versión
python -c "from liquidator import __version__; print(__version__)"

# Ejecutar prueba básica
python bin/liquidar.py --test-run
```

---

## 2. Conceptos Básicos

### 2.1 Modalidades de Liquidación

El sistema soporta dos modalidades principales:

#### Modalidad PERIÓDICA (Soporte de Pago)
- **Propósito**: Liquidación regular de prestaciones (bimestral/trimestral)
- **Incluye**: Cesantías, intereses, prima de servicios
- **No incluye**: Vacaciones (solo acumulación), indemnización
- **Uso**: Reporting regular, contabilidad, auditorias internas

#### Modalidad FINIQUITO
- **Propósito**: Liquidación final por terminación de contrato
- **Incluye**: Todas las prestaciones más vacaciones y indemnización (si aplica)
- **Uso**: Terminación de contrato, liquidación definitiva

### 2.2 Componentes Salariales

| Componente | Descripción | Incluye en SBL | Observaciones |
|------------|-------------|----------------|---------------|
| Salario Base | Remuneración pactada mensualmente | ✅ SBL_GENERAL, SBL_VACACIONES | Siempre incluido |
| Comisiones | Promedio mensual de comisiones | ✅ Ambos SBLs | Variable permitido |
| Horas Extras | Promedio mensual de horas extras | ✅ SBL_GENERAL exclusivamente | Excluido de vacaciones |
| Bonificaciones | Promedio monthly bonificaciones | ✅ SBL_GENERAL exclusivamente | Excluido de vacaciones |
| Auxilio Transporte | Legalmente establecido | ⚠️ Condicional | NO aplica si reside en lugar de trabajo |

### 2.3 Reglas Especiales Importantes

#### Trabajadores de Finca Rural
- `reside_en_lugar_trabajo`: `true`
- **NO aplica** auxilio de transporte (vive en finca)
- **Puede aplicar** auxilio de transporte si está pactado

#### Límites Salariales
- **Auxilio transporte** solo aplica si SBL ≤ 2 SMMLV
- **Indemnización** tiene tope máximo de 20 SMMLV

#### Periodos Especiales
- **Prima semestral**: Proporcional a días trabajados en semestre
- **Cesantías**: Base 360 días (no 365)
- **Intereses**: Tasa fija 12% anual

---

## 3. Uso Rápido

### 3.1 Ejemplo Inmediato (Trabajador de Finca Rural)

```bash
# Liquidación periódica básica
python bin/liquidar.py \
    --modo PERIODICA \
    --fecha_ingreso 2024-11-16 \
    --fecha_corte 2025-11-15 \
    --salario_mensual 2000000 \
    --reside_en_lugar_trabajo true \
    --auxilio_transporte 200000 \
    --output liquidacion_finca.json
```

### 3.2 Usando Archivo JSON de Entrada

```bash
# Crear archivo de entrada
cat > mi_liquidacion.json << EOF
{
  "modo": "PERIODICA",
  "fecha_ingreso": "2024-01-01",
  "fecha_corte": "2025-01-01",
  "salario_mensual": 2500000,
  "reside_en_lugar_trabajo": false,
  "auxilio_conectividad": 200000,
  "comisiones_promedio_mensual": 300000
}
EOF

# Ejecutar liquidación
python bin/liquidar.py --input mi_liquidacion.json --output resultado.json
```

### 3.3 Generar Documento Imprimible

```bash
# Generar PDF profesional desde resultados
python bin/liquidar.py --generate-pdf resultado.json

# PDF se genera como: resultado.pdf
```

---

## 4. Modos de Liquidación

### 4.1 Modo PERIÓDICA (Recomendado para reporting regular)

#### Cuando usarlo:
- Reportes contables trimestrales/bimestrales
- Auditorías internas de prestaciones
- Verificación de acumulaciones año actual
- Proyecciones de costos laborales

#### Resultado típico:
```json
{
  "modo": "PERIÓDICA",
  "desglose": {
    "cesantias": {"valor": 2200000, "plazo_pago_legal": "2026-02-14"},
    "intereses_cesantias": {"valor": 264000, "plazo_pago_legal": "2026-01-31"},
    "prima": {"valor": 1100000, "plazo_pago_legal": "2025-12-31"},
    "vacaciones": {"valor": 0, "nota": "No aplica en modo PERIÓDICA"}
  },
  "total_liquidacion_periodica": 3564000
}
```

### 4.1.1 Compensación de Vacaciones en Dinero (Acuerdo Mutuo)

Esta funcionalidad especial permite monetizar hasta el 50% de las vacaciones pendientes durante la vigencia del contrato (Liquidación Periódica), conforme al Art. 189 del CST.

#### Requisitos Críticos:
1.  **Solicitud del trabajador:** Debe mediar petición escrita.
2.  **Acuerdo Mutuo:** Empleador y trabajador deben estar de acuerdo.
3.  **Límite del 50%:** No se puede compensar más de la mitad de los días causados. El sistema **ajustará automáticamente** cualquier valor que exceda este límite legal.

#### Instrucciones para Generar el Documento (PDF con Cláusula):

Para que el PDF incluya la **Cláusula Legal de Acuerdo** lista para firma, debe indicar los días a compensar explícitamente.

**Opción A: Vía Línea de Comandos (CLI)**
No existe un flag directo en CLI estándar, por lo que se recomienda usar un archivo JSON o pasar el argumento extra en futuras versiones. Actualmente, use el método JSON para garantizar precisión.

**Opción B: Vía Archivo JSON (Recomendado)**

1. Cree un archivo `compensacion.json`:
```json
{
  "modo": "PERIODICA",
  "fecha_ingreso": "2024-01-01",
  "fecha_corte": "2025-01-01",
  "salario_mensual": 2000000,
  "dias_vacaciones_pendientes": 15,
  "dias_vacaciones_para_compensar_dinero": 7,
  "nombre": "Juan Pérez",
  "documento": "12345678"
}
```

2. Ejecute el comando generando el PDF:
```bash
python bin/liquidar.py --input compensacion.json --output resultado_compensacion.json --generate-pdf AUTO
```

3. **Verifique el PDF:**
   Abra `resultado_compensacion.pdf`. Justo antes de las firmas, encontrará la sección:
   > **CLÁUSULA DE ACUERDO DE COMPENSACIÓN DE VACACIONES**
   > ...se compensan en dinero 7 días... Artículo 189...

Este documento firmado constituye la prueba legal del acuerdo.

### 4.2 Modo FINIQUITO (Para terminación de contrato)

#### Cuando usarlo:
- Despido con o sin justa causa
- Renuncia voluntaria
- Vencimiento de contrato fijo
- Muerte trabajador

#### Datos adicionales requeridos:
```json
{
  "modo": "FINIQUITO",
  "motivo_terminacion": "despido_sin_justa_causa",
  "dias_vacaciones_pendientes": 15,
  "salario_pendiente": 500000,
  "salario_pendiente_dias": 10
}
```

#### Resultado típico:
```json
{
  "modo": "FINIQUITO",
  "desglose": {
    "cesantias": {"valor": 2450000},
    "intereses_cesantias": {"valor": 308000},
    "prima": {"valor": 1375000},
    "vacaciones": {"valor": 1000000},
    "indemnizacion": {"valor": 4445000}
  },
  "total_finiquito": 9573000
}
```

---

## 5. Argumentos de Línea de Comandos

### 5.1 Argumentos Principales

| Argumento | Requerido | Formato | Descripción |
|-----------|-----------|---------|-------------|
| `--modo` | ✅ | PERIODICA | FINIQUITO | Modalidad de liquidación |
| `--fecha_ingreso` | ✅ | YYYY-MM-DD | Fecha de inicio del contrato |
| `--fecha_corte` | ✅ | YYYY-MM-DD | Fecha de fin del período |
| `--salario_mensual` | ✅ | entero (COP) | Salario base mensual |
| `--reside_en_lugar_trabajo` | ✅ | true/false | ¿Vive en lugar de trabajo? |
| `--output` | | ruta_archivo | Archivo JSON de salida |

### 5.2 Componentes Salariales

| Argumento | Formato | Descripción |
|-----------|---------|-------------|
| `--comisiones_promedio_mensual` | decimal | Promedio mensual de comisiones |
| `--horas_extras_promedio_mensual` | decimal | Promedio mensual de horas extras |
| `--bonificaciones_promedio_mensual` | decimal | Promedio mensual de bonificaciones |
| `--auxilio_transporte` | entero (COP) | Valor auxilio de transporte |

### 5.3 Contractuales y Especiales

| Argumento | Formato | Descripción |
|-----------|---------|-------------|
| `--tipo_contrato` | indefinido | fijo | Tipo de contrato |
| `--motivo_terminacion` | texto (solo FINIQUITO) | Motivo de terminación |
| `--dias_vacaciones_pendientes` | entero | Días de vacaciones no disfrutadas |
| `--salario_pendiente` | decimal (COP) | Salario adeudado por pagar |
| `--salario_pendiente_dias` | entero | Días que corresponde al salario pendiente |

### 5.4 Configuración de Compliance

| Argumento | Formato | Defecto | Descripción |
|-----------|---------|----------|-------------|
| `--enforce-compliance` | true/false | true | Forzar cumplimiento legal |
| `--compliance-policy` | lenient | standard | strict | standard Severidad de validaciones |
| `--human-override` | flag | false | Permitir bypass con justificación |
| `--operator-id` | texto | Identificador del operador que autoriza override |
| `--override-reason` | texto | Justificación del override |

### 5.5 Modos Especiales

| Argumento | Descripción |
|-----------|------------|
| `--input archivo.json` | Usar archivo JSON como entrada |
| `--test-run` | Ejecutar suite de validación interna |
| `--generate-pdf archivo.json` | Generar PDF desde JSON existente |
| `--compliance-check-only archivo.json` | Solo validar compliance |

---

## 6. Ejemplos Prácticos

### 6.1 Caso 1: Trabajador de Finca Rural (Periódica)

**Contexto:** Empleado agrícola que vive en la finca

```bash
python bin/liquidar.py \
    --modo PERIODICA \
    --fecha_ingreso 2024-11-16 \
    --fecha_corte 2025-11-15 \
    --salario_mensual 1800000 \
    --reside_en_lugar_trabajo true \
    --auxilio_transporte 150000 \
    --comisiones_promedio_mensual 200000 \
    --output finca_2025.json
```

**Resultados Esperados:**
- SBL_GENERAL: 1.950.000 (sin auxilio transporte)
- SBL_VACACIONES: 1.800.000 (sin comisiones)
- Cesantías: 1.950.000
- Intereses: 234.000
- Prima: 975.000

### 6.2 Caso 2: Empleado Oficina con Auxilio Transporte

**Contexto:** Empleado urbano con auxilio transporte estándar

```bash
python bin/liquidar.py \
    --modo PERIODICA \
    --fecha_ingreso 2024-01-01 \
    --fecha_corte 2024-12-31 \
    --salario_mensual 1600000 \
    --reside_en_lugar_trabajo false \
    --tipo_contrato indefinido \
    --horas_extras_promedio_mensual 150000 \
    --output oficina_2024.json
```

**Resultados Esperados:**
- SBL_GENERAL: 1.750.000 (incluye auxilio transporte 200.000)
- Alerta: Auxilio de transporte incluido por residencia urbana

### 6.3 Caso 3: Finiquito por Despido

**Contexto:** Empleado con 2 años de servicio sin vacaciones tomadas

```bash
python bin/liquidar.py \
    --modo FINIQUITO \
    --fecha_ingreso 2022-11-16 \
    --fecha_corte 2025-11-15 \
    --salario_mensual 3000000 \
    --motivo_terminacion despido_sin_justa_causa \
    --dias_vacaciones_pendientes 24 \
    --salario_pendiente 500000 \
    --tipo_contrato indefinido \
    --output finiquito_empleado.json
```

**Resultados Esperados:**
- Indemnización con tope 20 SMMLV si aplica
- Vacaciones compensadas en dinero
- Salario pendiente incluido
- Pagos inmediatos requeridos

### 6.4 Caso 4: Salario Variable con Historial

**Contexto:** Vendedor con comisiones variables

```bash
# Crear JSON con salarios históricos
cat > vendedor.json << EOF
{
  "modo": "PERIODICA",
  "fecha_ingreso": "2024-01-01",
  "fecha_corte": "2024-12-31",
  "salario_mensual": 1200000,
  "salarios_historicos": [
    {"periodo": "2024-01", "total": 1200000},
    {"periodo": "2024-02", "total": 1800000},
    {"periodo": "2024-03", "total": 2500000}
  ],
  "reside_en_lugar_trabajo": false,
  "comisiones_promedio_mensual": 800000
}
EOF

python bin/liquidar.py --input vendedor.json --output vendedor_result.json
```

**Resultados Esperados:**
- SBL calculado usando promedio de últimos 12 meses
- Alerta sobre variabilidad salarial
- Nota sobre método de promediación utilizado

---

## 7. Interpretación de Resultados

### 7.1 Estructura General del Output

```json
{
  "meta": {
    "modo": "PERIÓDICA",
    "fecha_generacion": "2025-11-04T14:30:00",
    "params_version": "2025-10-31"
  },
  "desglose": {
    // Detalle de cada prestación
  },
  "compliance_report": {
    "compliance_status": "GO",
    "checks": [...]
  }
}
```

### 7.2 Interpretación de Compliance Report

#### Status: GO
- ✅ **Todo correcto**: Aprobado legalmente
- ✅ Sin bloqueos
- ✅ Lista para procesamiento

#### Status: WARN
- ⚠️ **Advertencias no bloqueantes**
- ✅ Se generó resultado
- 📝 Revisar warnings en `compliance_report.checks`

#### Status: NO_GO
- ❌ **Bloqueado legalmente**
- 🚫 No se generó liquidación (con compliance enforzado)
- 📄 Review required in `compliance_report.checks`

#### Status: OVERRIDE
- 🔄 **Override humano aplicado**
- ⚠️ Originalmente fallaba, pero fue autorizado
- 👤 Verificar datos de `operator_action`

### 7.3 Detalles de Cada Prestación

#### Cesantías
```json
{
  "cesantias": {
    "valor": 2200000,
    "dias_liquidados": 365,
    "formula_aplicada": "(2.200.000 × 365) ÷ 360",
    "norma": "Art.249-250 CST",
    "plazo_pago_legal": "2026-02-14"
  }
}
```

**Clave:** Valor en COP que debe consignarse antes del 14 de febrero del año siguiente.

#### Intereses sobre Cesantías
```json
{
  "intereses_cesantias": {
    "valor": 264000,
    "tasa_aplicada": 0.12,
    "norma": "Ley 50/1990 Art.99",
    "plazo_pago_legal": "2026-01-31"
  }
}
```

**Clave:** Intereses que deben pagarse antes del 31 de enero del año siguiente.

#### Prima de Servicios
```json
{
  "prima": {
    "valor": 1100000,
    "dias_liquidados": 180,
    "norma": "Art.306-308 CST",
    "plazo_pago_legal": "2025-12-31"
  }
}
```

**Clave:** Proporcional al semestre trabajado. Pago: 30 de junio o 20 de diciembre.

#### Vacaciones
```json
{
  "vacaciones": {
    "valor": 0,
    "dias_liquidados": 0,
    "nota": "No aplica en modo PERIÓDICA"
  }
}
```

**Clave:** Solo se compensan en efectivo en modo FINIQUITO.

### 7.4 Validaciones y Alertas Importantes

Verificar siempre estos elementos en el output:

1. **Plazos Legales**: Enviar pagos antes de fechas límite
2. **Alertas de SBL**: Revisar si auxilio transporte fue excluido correctamente
3. **Normas Aplicadas**: Verificar referencias legales presentes
4. **Warnings de Compliance**: Atender a advertencias incluso con status GO

---

## 8. Solución de Problemas

### 8.1 Errores Comunes

#### Error: ValidationError: Campo requerido faltante

**Causa:** Faltan datos obligatorios
**Solución:** Agregar campos requeridos:
```bash
# Ejemplo: faltaba tipo_contrato
--tipo_contrato indefinido
```

**Campos obligatorios mínimos:**
- modo
- fecha_ingreso
- fecha_corte
- salario_mensual
- reside_en_lugar_trabajo

#### Error: ComplianceError: No aplica liquidación

**Causa:** Contrato de tipo prestación de servicios
**Solución:** Verificar tipo_contrato
```bash
# Cambiar a contrato laboral válido
--tipo_contrato indefinido
```

#### Error: Fecha inválida

**Causa:** Formato incorrecto o fecha_corte anterior a fecha_ingreso
**Solución:** Verificar formato YYYY-MM-DD y coherencia:
```bash
--fecha_ingreso 2024-01-01
--fecha_corte 2024-12-31  # fecha_corte debe ser posteriore
```

#### Error: Permiso denegado

**Causa:** Sin permisos en directorio de output
**Solución:** 
```bash
# Cambiar a directorio con permisos
--output /ruta/con/permisos/resultado.json

# O especificar directorio temporal
--output /tmp/mi_liquidacion.json
```

### 8.2 Problemas de Compliance

#### Status: NO_GO con multiple failures

**Pasos para resolver:**

1. **Revisar reporte detallado:**
```bash
# Ver reporte completo
cat resultado.json | jq '.compliance_report.checks[]'
```

2. **Identificar issue principal:**
```bash
# Filtrar solo errores FAIL
python -c "import json; data=json.load(open('resultado.json')); [print(f\"{c['id']}: {c['description']} - {c['evidence']}\") for c in data['compliance_report']['checks'] if c['result']=='FAIL']"
```

3. **Aplicar corrección según issue:**
   - V001: Verificar parámetros legales desactualizados
   - V002: Cambiar tipo_contrato a laboral
   - V003: Ajustar residencia_en_lugar_trabajo
   - ...

#### Considerar Override (con supervisión legal)
```bash
python bin/liquidar.py \
    --input problema.json \
    --human-override \
    --operator-id "apellido.nombre@empresa" \
    --override-reason "Caso especial autorizado legalmente" \
    --output resultado_con_override.json
```

### 8.3 Problemas de Rendimiento

#### Sistema muy lento con muchos cálculos

**Causa:** Archivo de entrada muy grande o cálculos complejos
**Solución:**
```bash
# Usar modo test para diagnóstico
python bin/liquidar.py --test-run

# Paralelizar si procesando múltiples casos
for archivo in *.json; do
  python bin/liquidar.py --input "$archivo" --output "result_$archivo" &
done
```

### 8.4 Problemas de Encoding

**Error:** UnicodeDecodeError

**Causa:** caracteres especiales en nombres o datos
**Solución:**
```bash
# Forzar encoding UTF-8
export PYTHONIOENCODING=utf-8
python bin/liquidar.py --input archivo.json --output resultado.json
```

---

## 9. Preguntas Frecuentes

### 9.1 Funcionalidad y Limitaciones

**P: ¿El sistema soporta cálculos retroactivos para años anteriores?**
R: Sí, pero requiere archivos de parámetros del año correspondiente. La versión actual incluye parámetros 2025. Para otros años, contactar administrador.

**P: ¿Es válido legalmente para auditorías de DIAN?**
R: Sí, el sistema incluye trazabilidad completa con evidencia legal y está diseñado para cumplir requerimientos de auditoría.

**P: ¿Diferencia entre días laborales y calendario?**
R: No, todos los cálculos usan días calendario (365/360), excepto vacaciones que se liquidan por laborales (15 laborales = 1 día vacaciones). El sistema maneja esta conversión automaticamente.

**P: ¿Cómo se manejan los días no laborados (incapacidades, licencias)?**
R: La versión actual considera todos los días entre fechas. Para treatment especial de incapacidades o licencias no remuneradas, recomendado hacer ajuste manual o contactar soporte.

### 9.2 Reglas Específicas

**P: ¿Por qué auxilio de transporte no aplica en fincas rurales?**
R: Es porque el trabajador reside en el lugar de trabajo y no realiza desplazamiento diario. Es una excepción legal reconocida.

**P: ¿Desde cuándo aplica el recargo dominical del 80%?**
R: A partir del 1 de julio de 2025 según Ley 2466/2025. Para periodos anteriores, no se calcula.

**P: ¿A qué se refiere "base 360 días" en cesantías?**
R: Es la base legal establecida en el CST para fraccionamiento de prestaciones. Se usa año comercial de 360 días en lugar de calendario de 365 días.

### 9.3 Output y Documentos

**P: ¿Puedo personalizar el formato del PDF?**
R: La versión actual usa plantilla estandar. Para personalización completa, contactar equipo de desarrollo.

**P: ¿Cómo verifico que el cálculo sea correcto?**
R: El sistema incluye compliance automático con 10 reglas. Además, puede ejecutar modo solo validación:
```bash
python bin/liquidar.py --compliance-check-only resultado.json
```

**P: ¿Qué incluye el audit trail?**
R: Incluye hashes del input/output, parámetros utilizados, resultados de validaciones, y metadata con timestamps para reproducibilidad completa.

### 9.4 Técnico y Operativo

**P: ¿El sistema funciona en todos los sistemas operativos?**
R: Sí, es compatible con Windows, macOS y Linux que soporten Python 3.8+.

**P: ¿Requiere conexión a internet?**
R: No, el sistema funciona completamente offline. Los parámetros legales están incluidos localmente.

**P: ¿Cómo reporto un bug o solicito una mejora?**
R: Use el issue tracker del repositorio o contacte directamente al equipo de desarrollo con detalles del escenario.

**P: ¿Hay plan de updates normativos automáticos?**
R: El sistema emite alertas de cambios pero requiere actualización manual. Se está desarrollando sistema de auto-update para futura versión.

### 9.5 Legal y Comprobación

**P: ¿Los resultados tienen validez legal?**
R: Los cálculos cumplen normativa vigente, pero siempre deben ser revisados por personal de Recursos Humanos y, si aplica, departamento legal antes de ejecución.

**P: ¿Qué información debe conservarse para auditorías?**
R: El JSON completo de output, el JSON de input, y si hay override, la justificación del operador. Se recomienda guardar también audit trail generado.

**P: ¿Es necesario estampar física o digitalmente los documentos generados?**
R: Sí, para validez legal los comprobantes deben ser firmados electrónicamente o físicamente por trabajador y empleador.

---

## 10. Checklist Pre-Ejecución

Antes de ejecutar una liquidación, verifique:

- [ ] Datos de contrato correctos (tipo, fechas, salario)
- [ ] Configuración residencia (lugar de trabajo)
- [ ] Componentes salariales correctos y documentados
- [ ] Período de liquidación correcto
- [ ] Directorio de salida con permisos de escritura
- [ ] Política de compliance según necesidad (lenient/standard/strict)

---

## 11. Recursos Adicionales

### 11.1 Documentación Complementaria
- [Plan de Implementación](Plan%20de%20Implementación.md) - Detalles técnicos
- [Referencia API](api_reference.md) - Para desarrolladores
- [Ejemplos Completos](../examples/) - Casos de prueba documentados
- [Referencias Legales](../legal_docs/) - Normativa completa

### 11.2 Soporte y Capacitación
- Email: soporte@empresa.com
- Capacitación presencial o virtual disponible
- Webinars mensuales de actualización normativa

### 11.3 Comunidad y Updates
- Newsletter regulatory updates: suscripción@empresa.com
- Foro de usuarios: forum.empresa.com/liquidacion
- Updates automáticos: configurar en config/default_config.yaml

### 12. Paso a paso para liquidación personalizada

1.	Activar entorno virtual (desde cualquier directorio):
Powershell
C:\Users\Jhond\Github\liquidacion_cli\.venv\Scripts\activate.bat
2.	Navegar al directorio del proyecto:
Powershell
cd C:\Users\Jhond\Github\liquidacion_cli
3.	Ejecutar comando con parámetros personalizados:
Powershell
python bin\liquidar.py --modo PERIODICA --fecha_ingreso 2024-11-16 --fecha_corte 2025-11-15 --salario_mensual 1500000 --reside_en_lugar_trabajo true --auxilio_transporte 200000 --nombre-trabajador "TRABAJADOR DEFINIDO" --documento-trabajador "DOCUMENTO_DEFINIDO" --output liquidacion_corregida.json --generate-pdf AUTO
Reemplaza:
•  YYYY-MM-DD (fecha_ingreso): Fecha de inicio del trabajador
•  YYYY-MM-DD (fecha_corte): Fecha de liquidación
•  XXXXXXXXX (salario_mensual): Salario mensual en pesos
4.	Ejemplo práctico completo:
Powershell
python bin\liquidar.py --modo PERIODICA --fecha_ingreso 2024-11-16 --fecha_corte 2025-11-15 --salario_mensual 1500000 --reside_en_lugar_trabajo true --auxilio_conectividad 200000 --output mi_liquidacion.json --generate-pdf AUTO
5.	Resultados generados:
•  mi_liquidacion.json - Datos completos de liquidación
•  mi_liquidacion.pdf - Documento PDF profesional
Parámetros opcionales adicionales:
•  --comisiones_promedio_mensual XXXXXX - Para comisiones mensuales
•  --horas_extras_promedio_mensual XXXXXX - Para horas extras
•  --bonificaciones_promedio_mensual XXXXXX - Para bonificaciones
•  --dias_vacaciones_pendientes XX - Días de vacaciones pendientes
•  --tipo_contrato indefinido|fijo - Tipo de contrato
Para trabajadores URBANOS (sin residencia en lugar de trabajo):
Powershell
python bin\liquidar.py --modo PERIODICA --fecha_ingreso 2024-01-01 --fecha_corte 2025-01-01 --salario_mensual 1800000 --reside_en_lugar_trabajo false –output liquidacion_urbano.json --generate-pdf AUTO
Este método te permite generar liquidaciones personalizadas directamente desde la terminal sin necesidad de editar archivos JSON.

---

📝 **Nota Importante:** Siempre conserve los archivos JSON de input y output junto con los documentos firmados como evidencia legal de las liquidaciones realizadas.

⚖️ **Recordatorio Legal:** Los resultados de esta herramienta son cálculos basados en normativa vigente, pero deben ser supervisados por personal calificado antes de su ejecución definitiva.
