> **SUPERSEDED — S49 (2026-06-19)**: este borrador de borrador contenía 3 errores conceptuales
> (prima por período completo en lugar de semestral; vacaciones compensadas en PERIODICA
> cuando el motor solo compensa con acuerdo mutuo explícito; cobertura del período limitada
> a la última fracción en lugar del contrato completo). El motor v2.0 SÍ aplica correctamente
> la normatividad sustantiva y jurisprudencial. La fuente de verdad para los 3 casos es:
> - `audit/validacion_v2/caso_1/comparativa.md` (Básico PERIODICA)
> - `audit/validacion_v2/caso_2/comparativa.md` (Avanzado FINIQUITO SBL variable)
> - `audit/validacion_v2/caso_3/comparativa.md` (Complejo FINIQUITO IPC + preaviso)
> Este archivo se conserva solo como referencia histórica del input del usuario en S49.
> ---
>
> Aquí tienes los tres casos estructurados en JSON de Forma 1 PLANA (en raíz), listos para integrarse en tu orquestador, junto con el cálculo manual correspondiente para la validación de la métrica en tu matriz de cotejo.

### 1. CASO BÁSICO (Smoke Test)

**Archivo:** `audit/validacion_v2/caso_1/input.json`
Este caso cubre el escenario "happy path" de un trabajador con contrato a término indefinido dentro de un mismo año calendario, devengando un salario que da derecho al auxilio de transporte.

```json
{
  "fecha_ingreso": "2024-03-01",
  "fecha_corte": "2024-11-30",
  "salario_mensual": 1500000,
  "tipo_contrato": "INDEFINIDO",
  "modo": "PERIODICA",
  "auxilio_transporte": true,
  "aux_transporte_real_mensual": 162000,
  "reside_en_lugar_trabajo": false,
  "comisiones_promedio_mensual": 0,
  "horas_extras_promedio_mensual": 0,
  "bonificaciones_promedio_mensual": 0
}

```

**Cálculo Manual Esperado (Tolerancia ±$1):**

* **Días liquidados:** 270 (9 meses).
* **Base de Liquidación Prestaciones (SBL):** $1.662.000 ($1.500.000 + $162.000).
* **Base Liquidación Vacaciones:** $1.500.000.
* **Cesantías:** $1.662.000 × 270 / 360 = **$1.246.500**
* **Intereses s/ Cesantías:** $1.246.500 × 270 × 0.12 / 360 = **$112.185**
* **Prima de Servicios:** $1.662.000 × 270 / 360 = **$1.246.500** *(Asumiendo consolidado del periodo)*
* **Vacaciones:** $1.500.000 × 270 / 720 = **$562.500**
* **Total Acumulado:** **$3.167.685**

---

### 2. CASO AVANZADO (Addendum SL2630-2024 end-to-end)

**Archivo:** `audit/validacion_v2/caso_2/input.json`
Este escenario maneja un contrato mayor a un año, calculando el finiquito con salario base de liquidación (SBL) variable por año según la directriz jurisprudencial, y liquidando vacaciones compensadas en dinero.

```json
{
  "fecha_ingreso": "2023-01-01",
  "fecha_terminacion_real": "2024-12-30",
  "fecha_corte": "2024-12-30",
  "tipo_contrato": "INDEFINIDO",
  "motivo_terminacion": "renuncia_voluntaria",
  "salario_mensual": 3000000,
  "modo": "FINIQUITO",
  "auxilio_transporte": false,
  "sbl_por_anio": {
    "2023": 2500000,
    "2024": 3000000
  },
  "vacaciones": {
    "dias_pendientes": 15,
    "dias_disfrutados": 0
  }
}

```

**Cálculo Manual Esperado (Asumiendo liquidación retrospectiva completa no consignada por SBL variable):**

* **Días liquidados:** 720 (2 años exactos).
* **Cesantías Total:** Anualizadas. Año 2023 ($2.500.000) + Año 2024 ($3.000.000) = **$5.500.000**
* **Intereses Total:** Int 2023 ($300.000) + Int 2024 ($360.000) = **$660.000**
* **Prima Total:** Prima 2023 ($2.500.000) + Prima 2024 ($3.000.000) = **$5.500.000**
* **Vacaciones Compensadas:** (Días pendientes: 15. Base: Último salario $3.000.000). $3.000.000 × 15 / 30 = **$1.500.000**
* **Total Finiquito:** **$13.160.000**

---

### 3. CASO COMPLEJO (IPC + Segmentación multi-año + Compliance preaviso)

**Archivo:** `audit/validacion_v2/caso_3/input.json`
El caso más robusto. Cruza años calendario, valida una terminación de contrato a término fijo (con preaviso entregado en tiempos legales para evitar indemnización) y requiere la indexación de un concepto no pagado en su momento exigible.

```json
{
  "fecha_ingreso": "2023-01-01",
  "fecha_terminacion_real": "2025-06-30",
  "fecha_corte": "2025-06-30",
  "tipo_contrato": "FIJO",
  "motivo_terminacion": "termino_fijo_vencido",
  "salario_mensual": 4000000,
  "modo": "FINIQUITO",
  "auxilio_transporte": false,
  "vacaciones": {
    "dias_pendientes": 0
  },
  "periodos_no_pagados": [
    {
      "concepto": "cesantias",
      "valor_historico": 3500000,
      "fecha_causacion": "2023-12-31",
      "fecha_exigibilidad": "2024-02-14",
      "fecha_referencia_indexacion": "2025-06-30"
    }
  ],
  "fecha_vencimiento_termino_fijo": "2025-06-30",
  "preaviso_entregado": true,
  "fecha_preaviso": "2025-05-25",
  "dias_preaviso": 36
}

```

**Cálculo Manual Esperado:**

* **Fracción Finiquito 2025:** (Del 01-Ene al 30-Jun = 180 días). SBL = $4.000.000.
* Cesantías: $4.000.000 × 180 / 360 = **$2.000.000**
* Intereses: $2.000.000 × 180 × 0.12 / 360 = **$120.000**
* Prima: $4.000.000 × 180 / 360 = **$2.000.000**


* **Indexación Periodo No Pagado (IPC):**
Aplica la fórmula de Valor Actual (VA), donde Valor Histórico (VH) es $3.500.000.
$$ VA = VH \times \left( \frac{IPC_{final}}{IPC_{inicial}} \right) $$
*(Para la matriz, asumiendo un factor inflacionario hipotético del periodo entre Febrero-2024 y Junio-2025 de 1.1098)*: $3.500.000 × 1.1098 = **$3.884.300**
* **Indemnización Preaviso:** **$0** (Se cumplió la entrega > 30 días previos).
* **Total Finiquito (Fracción 2025 + Deuda Indexada):** **$8.004.300**