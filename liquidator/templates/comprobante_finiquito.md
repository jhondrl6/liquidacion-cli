# LIQUIDACIÓN POR FINIQUITO DE PRESTACIONES SOCIALES
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
| Vacaciones | {{ format_currency(vacaciones) }} | {{ dias_vac }} | Pago inmediato | {{ norma_vac }} |
| Indemnización | {{ format_currency(indemnizacion) }} | {{ dias_indem }} | Pago inmediato | {{ norma_indem }} |
| Salario pendiente | {{ format_currency(salario_pendiente) }} | {{ dias_salario_pend }} | Pago inmediato | {{ norma_salario }} |

### TOTAL LIQUIDACIÓN POR FINIQUITO
**{{ format_currency(total) }} COP**

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