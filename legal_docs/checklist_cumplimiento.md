# CHECKLIST DE CUMPLIMIENTO LEGAL - CLI NOMINA COLOMBIANA 2025

## 🎯 Propósito
Este checklist garantiza el cumplimiento total de todos los aspectos legales y técnicos identificados en Script.py, G.md y Salida.json para evitar omisiones que puedan derivar en demandas legales posteriores.

---

## 📋 CHECKLIST DE PARÁMETROS LEGALES 2025

### ✅ **Parámetros Oficiales 2025**
- [ ] **SMMLV_2025**: $1.423.500 (Decreto 1572/2024)
- [ ] **AUXILIO_TRANS_2025**: $200.000 (Decreto 1573/2024)
- [ ] **LIMITE_AUXILIO**: 2 * SMMLV_2025 = $2.847.000
- [ ] **TASA_INT_CESANTIAS**: 0.12 (12% anual - Ley 50/90 Art. 99)
- [ ] **DIAS_ANUALES**: 360.0 (Base legal para prestaciones)
- [ ] **RECARGO_DOMINICAL_FACTOR_2025**: 0.80 (Vigente desde Jul 1, 2025)

### ✅ **Parámetros de Cálculo**
- [ ] **SBL_DIARIO**: SBL_GENERAL / 30.0
- [ ] **Base cálculo vacaciones**: 720.0 (días laborables para 15 días vacaciones)
- [ ] **Fechas corte**: Automáticas según tipo de liquidación

---

## 📋 CHECKLIST DE FUNCIONES TÉCNICAS REQUERIDAS

### ✅ **Funciones Auxiliares Críticas**
- [ ] **determinar_fecha_corte(modo_liquidacion, fecha_retiro)**
- [ ] **calcular_dias(fecha_inicio, fecha_fin)**
- [ ] **promedio_anual(pagos_variables_12_meses)**
- [ ] **promedio_semestral(pagos_variables_12_meses, fecha_corte_liquidacion)**
- [ ] **calcular_dias_periodo_anual(fecha_corte_liquidacion)**
- [ ] **calcular_dias_semestre_curso(fecha_corte_liquidacion)**
- [ ] **generar_json_output()**
- [ ] **calcular_indemnizacion_art64()**

### ✅ **Lógica de Liquidación Periódica vs Finiquito**
- [ ] **Modo PERIÓDICA**: Cesantías + Intereses + Prima (no finiquito)
- [ ] **Modo FINIQUITO**: Salario pendiente + Vacaciones + Indemnización + Finiquito
- [ ] **Fechas de corte**: Automáticas para modo periódico

---

## 📋 CHECKLIST DE VALIDACIONES LEGALES

### ✅ **Validaciones de Contrato**
- [ ] **Rechazar contratos de prestación de servicios** (NO generan prestaciones)
- [ ] **Aceptar solo contratos laborales**: término_fijo, indefinido, obra_determinada
- [ ] **Verificar afiliación seguridad social** (mencionado en G.md)

### ✅ **Validaciones de Auxilio de Transporte**
- [ ] **Salario ≤ 2 SMMLV**: Auxilio aplica
- [ ] **Salario > 2 SMMLV**: Auxilio NO aplica
- [ ] **Finca Rural/Residencia trabajo**: Auxilio excluido (SIN EXCEPCIÓN)
- [ ] **Alerta específica Finca Rural**: "Auxilio de transporte excluido. Motivo: Residencia en sitio de trabajo (Finca Rural)."

### ✅ **Validaciones de Fechas**
- [ ] **Fecha corte posterior a fecha ingreso**
- [ ] **Período laboral razonable** (máximo 2 años)
- [ ] **Días laborados > 0**

---

## 📋 CHECKLIST DE CÁLCULOS DE PRESTACIONES

### ✅ **Cesantías (Art. 249-252 CST)**
- [ ] **Fórmula**: (SBL_GENERAL * DIAS_CESANTIAS) / DIAS_ANUALES
- [ ] **Base**: SBL general + auxilio si aplica
- [ ] **Días**: Según período anual liquidado
- [ ] **Sustento legal**: "Art. 249 CST"

### ✅ **Intereses sobre Cesantías (Ley 50/90 Art. 99)**
- [ ] **Fórmula**: (CESANTIAS * DIAS_CESANTIAS * TASA_INT_CESANTIAS) / DIAS_ANUALES
- [ ] **Tasa**: 12% anual (0.12)
- [ ] **Sustento legal**: "Art. 99 Ley 50/90"
- [ ] **Plazo pago**: Antes de enero 31 siguiente año

### ✅ **Prima de Servicios (Art. 306-308 CST)**
- [ ] **Fórmula**: (SBL_PRIMA * DIAS_PRIMA) / DIAS_ANUALES
- [ ] **Fechas pago**: 30 junio (1er semestre) y 20 diciembre (2do semestre)
- [ ] **Base**: SBL semestral + auxilio si aplica
- [ ] **Sustento legal**: "Art. 306 CST"

### ✅ **Vacaciones Compensadas (Solo Finiquito)**
- [ ] **Fórmula**: (SBL_VACACIONES * DIAS_SERVICIO) / 720.0
- [ ] **Base**: SBL FIJO (excluye auxilio/extras)
- [ ] **Vacaciones pendientes**: Valor diario + días pendientes
- [ ] **Sustento legal**: "Art. 186-192 CST"

### ✅ **Indemnización (Solo Finiquito - Sin Justa Causa)**
- [ ] **Cálculo Art. 64 CST**: Mínimo un salario por año trabajado
- [ ] **Tope**: 20 SMMLV para base de cálculo
- [ ] **Solo si**: motivo_terminacion == "Sin_Justa_Causa"
- [ ] **Sustento legal**: "Art. 64 CST"

---

## 📋 CHECKLIST DE ESTRUCTURA JSON DE SALIDA

### ✅ **Estructura Base Requerida**
```json
{
  "parametros_calculo": {
    "modo_liquidacion": "PERIÓDICA",
    "fecha_corte": "YYYY-MM-DD",
    "SBL_General": "valor",
    "tiempo_servicio_dias_periodo": "días"
  },
  "total_liquidacion_periodica": "valor",
  "detalles_prestaciones": {
    "Cesantias": {
      "valor": "valor",
      "dias_liquidados": "días",
      "sustento_legal": "referencia normativa",
      "plazo_pago_legal": "fecha límite"
    }
  },
  "validaciones_y_alertas": {
    "alerta_auxilio_transporte": "mensaje específico",
    "nota_general": "descripción del modo"
  }
}
```

### ✅ **Campos Obligatorios por Prestación**
- [ ] **valor**: Cantidad calculada en pesos
- [ ] **dias_liquidados**: Días utilizados para el cálculo
- [ ] **sustento_legal**: Referencia normativa exacta
- [ ] **plazo_pago_legal**: Fecha límite de pago según ley

---

## 📋 CHECKLIST DE PLAZOS LEGALES DE PAGO

### ✅ **Plazos Obligatorios**
- [ ] **Cesantías**: Consignación antes 31 enero siguiente año
- [ ] **Intereses cesantías**: Pago directo antes 31 enero siguiente año
- [ ] **Prima 1er semestre**: Antes 30 junio
- [ ] **Prima 2do semestre**: Antes 20 diciembre
- [ ] **Art. 65 CST**: Liquidación pagada en fecha de terminación (finiquitos)

### ✅ **Sanciones por Mora**
- [ ] **Intereses cesantías**: 1 día de salario por día de retraso (Art. 99 L. 50/90)
- [ ] **Tope indemnización moratoria**: 24 meses máximo
- [ ] **Art. 65 CST**: Indemnización por mora en pago de prestaciones

---

## 📋 CHECKLIST DE MARCO LEGAL APLICABLE

### ✅ **Normas de Cumplimiento Obligatorio**
- [ ] **Código Sustantivo del Trabajo (CST)**: Arts. 249-252 (Cesantías)
- [ ] **Código Sustantivo del Trabajo (CST)**: Arts. 306-308 (Prima)
- [ ] **Código Sustantivo del Trabajo (CST)**: Arts. 186-192 (Vacaciones)
- [ ] **Código Sustantivo del Trabajo (CST)**: Art. 64 (Indemnizaciones)
- [ ] **Código Sustantivo del Trabajo (CST)**: Art. 65 (Plazos de pago)
- [ ] **Ley 50 de 1990**: Art. 99 (Intereses cesantías)
- [ ] **Decreto 1072 de 2015**: Cesantías e Intereses
- [ ] **Decreto 1572 de 2024**: SMMLV 2025
- [ ] **Decreto 1573 de 2024**: Auxilio transporte 2025

---

## 📋 CHECKLIST DE CASOS ESPECÍFICOS DE USO

### ✅ **Trabajador Finca Rural**
- [ ] **Rechazar auxilio transporte**: Residencia en sitio de trabajo
- [ ] **Alerta específica**: "Auxilio de transporte excluido. Motivo: Residencia en sitio de trabajo (Finca Rural)."
- [ ] **Aplicar auxilio conectividad**: Si corresponde
- [ ] **Nota en documentos**: "Trabajador reside en Finca Rural"

### ✅ **Trabajador con Salarios Variables**
- [ ] **Promedio anual**: Para cesantías e intereses
- [ ] **Promedio semestral**: Para prima de servicios
- [ ] **Validar 12 meses**: Mínimo para promedio
- [ ] **Proporcionalidad**: Para períodos menores a un año

### ✅ **Liquidación Periódica (No Finiquito)**
- [ ] **Solo prestaciones**: Cesantías, intereses, prima
- [ ] **No incluir**: Vacaciones compensadas, salarios pendientes
- [ ] **Fechas corte automáticas**: Según período liquidado
- [ ] **Nota explicativa**: "No es finiquito"

---

## 📋 CHECKLIST DE INTERFAZ CLI

### ✅ **Argumentos CLI Obligatorios**
- [ ] **--ingreso**: Fecha ingreso (YYYY-MM-DD)
- [ ] **--corte**: Fecha corte (YYYY-MM-DD)
- [ ] **--salario**: Salario base mensual
- [ ] **--periodica** o **--finiquito**: Tipo liquidación
- [ ] **--empresa**: Nombre empresa
- [ ] **--trabajador**: Nombre completo trabajador
- [ ] **--cedula**: Cédula trabajador

### ✅ **Argumentos CLI Opcionales**
- [ ] **--auxilio**: Aplica auxilio transporte
- [ ] **--conectividad**: Aplica auxilio conectividad
- [ ] **--finca-rural**: Trabajador reside en Finca Rural
- [ ] **--reside-trabajo**: Reside en sitio trabajo
- [ ] **--variables**: 12 salarios variables
- [ ] **--vacaciones-pendientes**: Días vacaciones pendientes
- [ ] **--salario-pendiente**: Días salario pendiente
- [ ] **--contrato**: Tipo contrato laboral
- [ ] **--motivo**: Motivo terminación

### ✅ **Opciones de Salida**
- [ ] **--json**: Archivo salida JSON
- [ ] **--documento**: Generar documento legal
- [ ] **Mostrar en consola**: Resultado detallado

---

## 📋 CHECKLIST DE GENERACIÓN DE DOCUMENTOS LEGALES

### ✅ **Documento para Firma Requerido**
- [ ] **Encabezado**: Liquidación Prestaciones Sociales Colombia 2025
- [ ] **Datos trabajador**: Nombre, cédula, empresa
- [ ] **Período liquidado**: Fecha ingreso a fecha corte
- [ ] **Desglose prestaciones**: Cada concepto valorizado
- [ ] **Total liquidación**: Suma total
- [ ] **Sustento legal**: Referencias normativas por prestación
- [ ] **Fecha límite pago**: Según normativa
- [ ] **Espacios firma**: Trabajador y Representante Legal
- [ ] **Declaración legal**: "Trabajador declara haber recibido prestaciones"
- [ ] **Propósito legal**: "Prueba de liquidación y recibo"

---

## 📋 CHECKLIST DE TESTING Y VALIDACIÓN

### ✅ **Tests Unitarios Obligatorios**
- [ ] **Fórmulas cesantías**: Caso conocido verificado
- [ ] **Fórmula intereses**: 12% anual verificado
- [ ] **Prima semestral**: Cálculo por días
- [ ] **Auxilio transporte**: Límite 2 SMMLV
- [ ] **Finca Rural**: Rechazo auxilio
- [ ] **Salarios variables**: Promedios correctos
- [ ] **Validaciones**: Todos los casos error

### ✅ **Casos de Prueba Legales**
- [ ] **Trabajador salario fijo sin auxilio**
- [ ] **Trabajador salario fijo con auxilio**
- [ ] **Trabajador Finca Rural**
- [ ] **Trabajador salarios variables**
- [ ] **Liquidación semestral (prima)**
- [ ] **Liquidación anual (cesantías/intereses)**
- [ ] **Validación rechazo contratos servicios**

---

## 📋 CHECKLIST DE DOCUMENTACIÓN

### ✅ **Documentación Obligatoria**
- [ ] **README.md**: Instrucciones de uso
- [ ] **Ejemplos de uso**: Casos específicos documentados
- [ ] **Marco legal**: Referencias normativas incluidas
- [ ] **Parámetros 2025**: Valores oficiales documentados
- [ ] **Casos Finca Rural**: Ejemplos específicos

---

## ✅ CRITERIOS DE APROBACIÓN LEGAL

### El CLI será APROBADO únicamente cuando:
- [ ] **TODOS** los parámetros legales 2025 estén implementados
- [ ] **TODAS** las validaciones legales estén funcionando
- [ ] **TODAS** las fórmulas de cálculo sean exactas
- [ ] **TODOS** los plazos legales estén documentados
- [ ] **TODAS** las prestaciones tengan sustento legal
- [ ] **TODOS** los casos especiales estén validados
- [ ] **TODOS** los documentos generados sean legalmente válidos
- [ ] **TODOS** los tests unitarios pasen exitosamente

---

## 🚨 ADVERTENCIAS LEGALES CRÍTICAS

### ⚠️ **OMISIONES PROHIBIDAS**
- ❌ **NO OMITIR** rechazo de contratos de prestación de servicios
- ❌ **NO OMITIR** validación límite 2 SMMLV para auxilio
- ❌ **NO OMITIR** caso específico Finca Rural
- ❌ **NO OMITIR** plazos legales de pago
- ❌ **NO OMITIR** sustento legal por cada prestación
- ❌ **NO OMITIR** sanciones por mora en cálculos

### ⚠️ **RESPONSABILIDAD LEGAL**
- Cualquier omisión en este checklist puede resultar en demandas laborales posteriores
- La empresa será responsable por liquidaciones incorrectas o incompletas
- Los documentos generados deben servir como prueba legal válida

---

## 📊 CHECKLIST DE COMPLETITUD

**Estado actual del desarrollo:**
- [ ] Script.py analizado ✅
- [ ] G.md analizado ✅  
- [ ] Salida.json analizado ✅
- [ ] Checklist creado ✅
- [ ] Validación pendiente: **PENDIENTE**

**Fecha de creación**: 31 octubre 2025
**Versión**: 1.0
**Próxima revisión**: Antes de implementación final