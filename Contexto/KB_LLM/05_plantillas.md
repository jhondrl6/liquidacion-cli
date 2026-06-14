# 05-bis — Plantillas de documentos (Jinja2)

> Documenta los bloques condicionales en las plantillas de generación de
> documentos (`liquidator/templates/`).

## Plantillas activas

| Archivo                     | Modo             | Bloques condicionales                         |
|-----------------------------|------------------|-----------------------------------------------|
| `comprobante_periodica.md`  | PERIODICA        | `desglose_segmentado` (tabla por año)         |
| `comprobante_finiquito.md`  | FINIQUITO        | Renuncia (Art. 49.6), Vacaciones (Art. 189-190), Preaviso (Art. 46) |
| `comprobante_bloqueado.md`  | NO_GO            | Sin bloques (plantilla estática)              |

## `comprobante_finiquito.md` — Bloques condicionales

### 1. Renuncia voluntaria (Tarea 3.G, S34)

```jinja
{% if motivo_terminacion == "renuncia_voluntaria" %}
## Indemnización
**NO APLICA** — El trabajador {{ nombre }} renunció...
Base legal: Art. 49 num. 6 CST, Art. 64 CST.
{% endif %}
```

- **Trigger:** `motivo_terminacion == "renuncia_voluntaria"` (string, flat context)
- **Efecto:** En la tabla de prestaciones, la columna Indemnización muestra "N/A — renuncia voluntaria". Abajo, sección de no-indemnización.
- **Campos requeridos en contexto:** `motivo_terminacion`, `nombre`

### 2. Vacaciones compensadas (Tarea 3.G, S34)

```jinja
{% if desglose is defined and desglose.vacaciones is defined
      and desglose.vacaciones.valor is defined
      and desglose.vacaciones.valor > 0 %}
## Vacaciones compensadas (Art. 189-190 CST)
{% endif %}
```

- **Trigger:** `desglose.vacaciones.valor > 0`
- **Efecto:** Sección de vacaciones compensadas con días pendientes, valor y fórmula.
- **Campos requeridos en contexto:** `desglose` (dict inyectado por `MarkdownGenerator._build_context`)

### 3. Preaviso Art. 46 CST (Tarea 3.H, S35)

```jinja
{% if tipo_contrato == "fijo" and motivo_terminacion == "termino_fijo_vencido" %}
## Preaviso (Art. 46 CST)
{% if preaviso_entregado %}
  ... preaviso entregado: SÍ ...
  {% if desglose.preaviso_indemnizacion.valor > 0 %}
    **Preaviso insuficiente** ... indemnización parcial
  {% else %}
    Preaviso suficiente (≥ 30 días). No aplica indemnización.
  {% endif %}
{% else %}
  Preaviso entregado: **NO**.
  **Indemnización por falta de preaviso (30 días)**
  **Nota:** El empleador debió notificar...
{% endif %}
{% endif %}
```

- **Trigger:** `tipo_contrato == "fijo" and motivo_terminacion == "termino_fijo_vencido"`
- **Efecto:** Sección de preaviso con:
  - Si `preaviso_entregado == True`: muestra fecha, días de anticipación, y si fue suficiente o no
  - Si `preaviso_entregado == False/None`: muestra indemnización completa (30 días) + nota legal
- **Campos requeridos en contexto (flat):**
  - `tipo_contrato` (string, e.g. "fijo")
  - `motivo_terminacion` (string)
  - `preaviso_entregado` (bool|None)
  - `fecha_preaviso` (string)
  - `dias_preaviso` (int)
  - `desglose.preaviso_indemnizacion.valor` (int)
  - `desglose.preaviso_indemnizacion.dias_faltantes` (int)
- **Inyectados por:** `MarkdownGenerator._build_context()` (línea ~238, campos extraídos de `contrato` dict en FINIQUITO mode)

## Contexto plano (no anidado)

Las plantillas reciben un contexto **plano** (no `contrato.tipo`, sino `tipo_contrato`).
`MarkdownGenerator._build_context()` extrae campos del JSON de entrada en claves planas.
La excepción es `desglose` que se pasa como dict anidado para acceso a sub-campos.

## Filtros Jinja2 registrados

| Filtro            | Función                       | Registrado en              |
|-------------------|-------------------------------|----------------------------|
| `format_currency` | Formato COP con separadores   | `TemplateManager.__init__` |

## Convenciones

- **Siempre usar `is defined` guards** para campos del desglose (Pitfall #33, S34).
- **Nunca asumir que `desglose` existe** en el contexto — los tests legacy pueden no pasarlo.
- **Usar `|default(0)`** para valores numéricos opcionales.
- **No crear plantillas separadas** para variantes de motivo — preferir bloques condicionales en `finiquito.j2` (R6, §8.2 plan).
