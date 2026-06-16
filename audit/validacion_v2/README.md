# Validación v2.0 — 3 Liquidaciones Reales (Tarea 4.F)

> **Objetivo:** Verificar que el motor v2.0 produce resultados correctos
> comparados con cálculos manuales o herramienta de referencia.

## Proceso

1. **Seleccionar** 3 liquidaciones reales de tu operación.
2. **Crear** el JSON de entrada en formato Forma 1 (plano) — ver ejemplo abajo.
3. **Ejecutar** con el CLI:
   ```bash
   cd /mnt/c/Users/Jhond/Github/liquidacion_cli
   PYTHONPATH=. uv run --with click --with pydantic --with loguru --with python-dateutil --with Jinja2 --with markdown \
     python3 -m liquidator.cli.main liquidar audit/validacion_v2/caso_1/input.json --json-only
   ```
4. **Comparar** el output con tu cálculo manual.
5. **Documentar** discrepancias (si las hay) en `comparativa.md`.

## Formato de entrada (Forma 1 — plano)

```json
{
  "modo": "PERIODICA",
  "fecha_ingreso": "2025-11-16",
  "fecha_corte": "2026-06-09",
  "salario_mensual": 2200000,
  "tipo_contrato": "INDEFINIDO",
  "auxilio_transporte": false
}
```

### Modos soportados
- `PERIODICA` — liquidación periódica (cesantías, prima, intereses)
- `FINIQUITO` — liquidación definitiva (incluye vacaciones compensadas si aplica)

### Campos opcionales (para casos específicos)
- `vacaciones.dias_pendientes` — para FINIQUITO con vacaciones pendientes
- `contrato.motivo_terminacion` — para FINIQUITO (renuncia, despido, etc.)
- `periodos_no_pagados` — para indexación IPC (Art. 488 CST)

## Estructura por caso

```
audit/validacion_v2/
├── caso_1/
│   ├── input.json          ← JSON de entrada (Forma 1)
│   ├── output.json         ← Output del motor (generado por CLI)
│   ├── comparativa.md      ← Comparación con cálculo manual
│   └── notas.md            ← Observaciones adicionales
├── caso_2/
│   └── ...
└── caso_3/
    └── ...
```

## DoD (Definition of Done)

- [ ] 3 casos con `input.json` + `output.json` + `comparativa.md`
- [ ] Cada comparativa muestra coincidencia (o discrepancia documentada)
- [ ] Si hay discrepancia → issue abierta + corrección antes de cerrar Fase 4

## Notas

- **Formato anidado (Forma 2):** El motor NO soporta `contrato.fecha_ingreso`
  anidado. Usar formato plano (`fecha_ingreso` al nivel raíz).
- **Parámetros:** El motor usa automáticamente `params/2025.json` o
  `params/2026.json` según el año de la fecha de corte.
- **Compliance:** Si el resultado tiene `compliance_status: NO_GO`, se
  genera `liquidacion_BLOQUEADA.json` (sin PDF, regla AGENTS.md #7).
