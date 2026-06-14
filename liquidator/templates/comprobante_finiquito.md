# LIQUIDACIÓN POR FINIQUITO DE PRESTACIONES SOCIALES
## Colombia - Año {{ año }}

**Fecha de generación:** {{ fecha }}
**Modo de liquidación:** {{ modo }}
**Período liquidado:** {{ fecha_ingreso }} a {{ fecha_corte }}

**Trabajador:** {{ nombre }} CC: {{ documento }}

### DATOS DEL TRABAJADOR
- **Tipo de contrato:** {{ tipo_contrato }}
- **Reside en lugar de trabajo:** {{ "Sí" if reside_en_lugar else "No" }}
{% if motivo_terminacion %}
- **Motivo de terminación:** {{ motivo_terminacion }}
{% endif %}

### DETALLE DE PRESTACIONES

| Concepto | Valor (COP) | Días | Plazo de pago | Base legal |
|----------|-------------|------|---------------|------------|
| Cesantías | {{ format_currency(cesantias) }} | {{ dias_ces }} | {{ plazo_ces }} | {{ norma_ces }} |
| Intereses | {{ format_currency(intereses) }} | {{ dias_int }} | {{ plazo_int }} | {{ norma_int }} |
| Prima | {{ format_currency(prima) }} | {{ dias_prima }} | {{ plazo_prima }} | {{ norma_prima }} |
| Vacaciones | {{ format_currency(vacaciones) }} | {{ dias_vac }} | Pago inmediato | {{ norma_vac }} |
{% if motivo_terminacion == "renuncia_voluntaria" %}
| Indemnización | N/A — renuncia voluntaria | — | — | Art. 49 num. 6 CST |
{% else %}
| Indemnización | {{ format_currency(indemnizacion) }} | {{ dias_indem }} | Pago inmediato | {{ norma_indem }} |
{% endif %}
| Salario pendiente | {{ format_currency(salario_pendiente) }} | {{ dias_salario_pend }} | Pago inmediato | {{ norma_salario }} |

### TOTAL LIQUIDACIÓN POR FINIQUITO
**{{ format_currency(total) }} COP**

{% if motivo_terminacion == "renuncia_voluntaria" %}
## Indemnización
**NO APLICA** — El trabajador {{ nombre }} renunció
voluntariamente al cargo, conforme al **Art. 49 numeral 6** del Código
Sustantivo del Trabajo. Por tanto, **no se genera indemnización**
conforme al **Art. 64 CST** (indemnización por despido sin justa causa,
no aplicable a renuncia del trabajador).

Base legal: Art. 49 num. 6 CST, Art. 64 CST.
{% endif %}

{% if desglose is defined and desglose.vacaciones is defined and desglose.vacaciones.valor is defined and desglose.vacaciones.valor > 0 %}
## Vacaciones compensadas (Art. 189-190 CST)
Días pendientes al cierre: **{{ desglose.vacaciones.dias|default(0) }}**
Valor: **{{ format_currency(desglose.vacaciones.valor|default(0)) }}**
Fórmula: SBL / 30 × días_pendientes.
{% endif %}

{% if desglose_segmentado %}
{{ desglose_segmentado }}
{% endif %}

### OBSERVACIONES
{{ observaciones }}

### PLAZOS LEGALES DE PAGO
{{ plazos_detallados }}

### DECLARACIÓN LEGAL
{{ declaracion }}

<br>
<br>
<br>
<br>
<br>

<div style="display: flex; justify-content: space-between; margin-top: 50px;">
    <div style="text-align: center;">
        <p>____________________________________</p>
        <p style="margin-top: 30px;"><em>Firma del Trabajador</em></p>
        <p style="margin-top: 40px;">{{ nombre }}</p>
    </div>
    <div style="text-align: center;">
        <p>____________________________________</p>
        <p style="margin-top: 30px;"><em>Firma del Empleador</em></p>
        <p style="margin-top: 40px;">Hildaliria Raigoza L.</p>
        <p>CC 42.066.783</p>
    </div>
</div>
