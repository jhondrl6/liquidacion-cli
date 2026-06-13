# 09 — Caso canónico del usuario (ancla de validación continua)

> **Sin excepción, este caso debe poder ejecutarse y verificarse en
> cada fase cerrada.** Fuente: plan §3 (líneas 120-159). Esta nota se
> actualiza en cada fase con la salida real observada para evidenciar
> progreso.

## Versión vigente al 2026-06-13

Una sola liquidación en modo `PERIODICA` con dos segmentos de cálculo
(el año calendario cierra un segmento a 2025-12-31 y abre otro a
2026-01-01). La fecha de terminación real del contrato está pendiente
de confirmar; este caso usa **as-of 2026-06-09** como tope
provisional. Cuando el contrato termine, este caso se cierra con la
fecha de terminación real y se regeneran los golden files.

El SBL se mantiene en **2.200.000** para ambos años (constante del
contrato, no afectada por cambios de SMMLV).

## Input anonimizado

```json
{
  "modo": "PERIODICA",
  "trabajador": {"nombre": "[ANONIMIZADO]", "documento": "[ANONIMIZADO]"},
  "empleador":  {"nombre": "[ANONIMIZADO]", "documento": "[ANONIMIZADO]"},
  "contrato":   {"fecha_ingreso": "2025-11-16", "fecha_corte": "2026-06-09",
                 "tipo": "INDEFINIDO", "fecha_terminacion_real": null},
  "salario":    {"SBL": 2200000, "auxilio_transporte": false, "variable": false},
  "segmentos": [
    {"anio": 2025, "desde": "2025-11-16", "hasta": "2025-12-31",
     "params_ref": "params/2025.json"},
    {"anio": 2026, "desde": "2026-01-01", "hasta": "2026-06-09",
     "params_ref": "params/2026.json"}
  ]
}
```

## Segmentación y días

| Segmento | Rango | Días (inclusivo) | Params                                       | Normas relevantes                         |
|----------|-------|------------------|----------------------------------------------|-------------------------------------------|
| 2025-H2  | 2025-11-16 → 2025-12-31 | 46 | `params/2025.json` (SMMLV 1.423.500; aux 200.000) | Ley 50/1990, CST 249-308                  |
| 2026-H1  | 2026-01-01 → 2026-06-09 | 160 | `params/2026.json` (SMMLV 1.750.905; aux 249.095) | Ley 50/1990, CST 249-308, Ley 2466/2025, **D. 1469/2025 + D. 159/2026 (transitorio, ver R-LEG-07)** |
| **Total**| 2025-11-16 → 2026-06-09 | **206** | (convención día-a-día inclusiva) |  |

> **Convención de días:** inclusiva en ambos extremos. Alternativa
> fin-exclusivo daría 205; la convención **inclusiva** está fijada
> por el plan §3 y debe respetarse. La fecha de fin de segmento es
> el último día trabajado (o fecha_corte, lo que sea menor).

## Valores esperados (estado al cierre de S5)

| Concepto                    | Valor esperado              | Cálculo (referencia)                                          |
|-----------------------------|-----------------------------|---------------------------------------------------------------|
| **Cesantías 2025**          | TBD-motor-Fase1             | `2.200.000 × 46 / 360` usando `params/2025.json`             |
| **Cesantías 2026**          | TBD-motor-Fase1             | `2.200.000 × 160 / 360` usando `params/2026.json`            |
| **Intereses s/cesantías 2025** | TBD-motor-Fase1          | `cesantias_2025 × 0.12 × (46/360)`                            |
| **Intereses s/cesantías 2026** | TBD-motor-Fase1          | `cesantias_2026 × 0.12 × (160/360)`                           |
| **Prima H2 2025**           | TBD-motor-Fase1             | `2.200.000 × 46 / 360` (proporcional a 46 días del H2)        |
| **Prima H1 2026**           | TBD-motor-Fase1             | `2.200.000 × 160 / 360` (proporcional a 160 días del H1)      |
| **Vacaciones**              | TBD-motor-Fase1             | `SBL × 15 / 30` o proporcional al tiempo (Fase 1 cierra)     |
| **Indemnización Art. 64**   | `null`                      | NO IMPLEMENTADA en v2.0 (ver `06_riesgos_modelo.md` R-LEG-01) |
| **Recargo dominical**       | factor 0.80 en todo el rango| Ley 2466/2025 fase 1; cambia a 0.90 el 2026-07-01             |
| **Compliance esperado**     | `GO` (WARN aceptable)       | Ningún check CRITICAL violado                                |

> **TBD-motor-Fase1:** el motor aún no está estabilizado (Fase 0
> EN CURSO, Tarea 0.E). Los valores numéricos se completan cuando
> se ejecute el motor real en Fase 1 Tarea 1.B (golden test). El
> cálculo manual de la tabla es para que un humano verifique la
> fórmula, no para saltarse el motor.

## Golden files esperados (a crear en Fase 1)

- `examples/expected/caso_canonico_periodico_206d_result.json` (el
  output del motor, con `meta.parametros_por_segmento` poblado).
- `examples/expected/caso_canonico_periodico_206d_result.md`
  (render humano, si la Fase 3 ya está activa).
- `examples/expected/caso_canonico_periodico_206d_result.pdf`
  (idem, si aplica).

`meta.parametros_por_segmento` debe registrar **ambos** `params_version`:
- Segmento 2025 → `"2025-10-31"` (versión de `params/2025.json`).
- Segmento 2026 → `"2026-06-09"` (versión de `params/2026.json`).

**Adicional (post-S11, R-LEG-07):** para el segmento 2026, el output
debe incluir `meta.referencias_normativas: ["DECRETO_1469_2025",
"DECRETO_159_2026"]` para trazabilidad de la suspensión provisional
del D. 1469/2025 (Consejo de Estado, 2026-02-12). Ver
`Contexto/KB_LLM/05_schema_salida.md` y `AGENTS.md` regla #15.

## Cómo reproducir el caso

**Estado al cierre de S5:** aún NO reproducible end-to-end (Fase 0
EN CURSO). Cuando el motor esté estabilizado (Fase 1+, Tarea 1.B),
la reproducción será:

```bash
# Activar entorno y verificar dependencias
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
source .venv/bin/activate  # o usar uv run
# (Comando CLI exacto pendiente de Tarea 1.A — pyproject + entry_points)

# Crear archivo de input
cat > /tmp/caso_canonico.json <<EOF
{... input de la sección de arriba ...}
EOF

# Correr liquidación
python -m liquidator.cli run /tmp/caso_canonico.json \
    --output output/caso_canonico_periodico_206d_result.json

# Verificar
diff output/caso_canonico_periodico_206d_result.json \
     examples/expected/caso_canonico_periodico_206d_result.json
```

El `diff` debe ser **vacío** (o solo diffs en `meta.fecha_generacion`
y `meta.input_hash`, que son legítimos).

## Estado de ejecución por sesión/fase

| Sesión | Fase | Estado del caso canónico                                     |
|--------|------|--------------------------------------------------------------|
| S5     | 0    | NO ejecutado. Caso documentado, motor no estabilizado.       |
| (pendiente) | 1 | Tarea 1.B crea golden test verde. Se llena columna "Valor observado". |
| (pendiente) | 2 | Cierre de Fase 2: motor exacto, todos los checks verde.     |
| (pendiente) | 2-bis | Indexación IPC evaluada (no aplica al canónico actual, sin prescripción). |
| (pendiente) | 3 | Generación de PDF/MD/PDF + auditoría inmutable.             |
| (pendiente) | 4 | v2.0.0 release; canónico verde con 3 liquidaciones reales más. |

## Vacaciones pendientes heredadas (referencia, no parte del caso)

El caso real `liquidacion_pedro_franco.json` (modo PERIODICA, contrato
2024-11-16 → 2025-11-15, hoy en `output/_legacy/`) tiene 7.5 días de
vacaciones compensadas por acuerdo mutuo (Art. 189 CST). Si el
contrato de Pedro Franco sigue vigente, esos 7.5 días se arrastran al
finiquito definitivo. **NO se incluyen en este caso canónico** (es de
otro contrato anonimizado). Se documenta aquí solo para que un
operador que vea ambos casos entienda que son distintos.

## Última validación contra código

- **Fecha:** 2026-06-13 (sesión S5, Tarea 0.E).
- **Verificado:** input y segmentación textual del plan §3 (líneas
  120-159). Valores de params 2025 y 2026 confirmados en sus JSON.
- **NO verificado:** ejecución del motor (no se intentó en esta
  sesión; el caso canónico se ejecuta en Fase 1 Tarea 1.B). Los
  TBD se llenan con `output/caso_canonico_periodico_206d_result.json`
  cuando el motor corra.
