# LIQUIDACIÓN PERIÓDICA DE PRESTACIONES SOCIALES
## Colombia - Año {{ año }}

**Fecha de generación:** {{ fecha }}
**Modo de liquidación:** {{ modo }}
**Período liquidado:** {{ fecha_ingreso }} a {{ fecha_corte }}

**Trabajador:** {{ nombre }} CC: {{ documento }}

### DATOS DEL TRABAJADOR
- **Tipo de contrato:** {{ tipo_contrato }}
- **Reside en lugar de trabajo:** {{ "Sí" if reside_en_lugar else "No" }}

### DETALLE DE PRESTACIONES

| Concepto | Valor (COP) | Días | Plazo de pago | Base legal |
|----------|-------------|------|---------------|------------|
| Cesantías | {{ format_currency(cesantias) }} | {{ dias_ces }} | {{ plazo_ces }} | {{ norma_ces }} |
| Intereses | {{ format_currency(intereses) }} | {{ dias_int }} | {{ plazo_int }} | {{ norma_int }} |
| Prima | {{ format_currency(prima) }} | {{ dias_prima }} | {{ plazo_prima }} | {{ norma_prima }} |
{% if vacaciones > 0 %}| Compensación Vacaciones | {{ format_currency(vacaciones) }} | {{ dias_vac }} | N/A | Art. 189 CST |{% endif %}

### TOTAL LIQUIDACIÓN PERIÓDICA
**{{ format_currency(total) }} COP**

{% if desglose_segmentado %}
{{ desglose_segmentado }}
{% endif %}

### OBSERVACIONES
{{ observaciones }}

### PLAZOS LEGALES DE PAGO
{{ plazos_detallados }}

### DECLARACIÓN LEGAL
{{ declaracion }}

{% if vacaciones > 0 %}
### CLÁUSULA DE ACUERDO DE COMPENSACIÓN DE VACACIONES
De conformidad con el Artículo 189 del Código Sustantivo del Trabajo, las partes manifiestan que, previa solicitud del trabajador y de mutuo acuerdo, se compensan en dinero **{{ dias_vac }}** días de vacaciones. El trabajador declara haber recibido el pago correspondiente en esta liquidación (${{ format_currency(vacaciones) }}) y se compromete a disfrutar en tiempo los días restantes de conformidad con la ley y antes de causar el nuevo período.
{% endif %}

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