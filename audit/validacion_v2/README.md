# Validación v2.0 — 3 Liquidaciones Reales (Tarea 4.F)

> **Objetivo:** Verificar que el motor v2.0 produce resultados correctos
> comparados con cálculos manuales o herramienta de referencia.
>
> **Estado al 2026-06-18 (S47):** 0/3 casos completos. Plan y estrategia
> documentados en `STRATEGY.md`. Los `input.json` son placeholders con
> metadatos apuntando al plan. Próximo paso: el usuario (Jhond) elige
> 3 liquidaciones reales de su operación y completa los formularios
> de STRATEGY.md §3.

## Plan y estrategia

**Leer primero:** [`STRATEGY.md`](./STRATEGY.md) — plan completo de
los 3 casos (perfiles, datos a proveer, comandos, template de
comparativa, procedimiento ante discrepancia, cierre de Fase 4).

**Schema de referencia:** [`TEMPLATE_input.json`](./TEMPLATE_input.json)
— todos los campos Forma 1 (plana) que el motor acepta, con
comentarios `_comentarios_*` para guiar el llenado.

## Proceso resumido

1. **Leer** `STRATEGY.md` §2 y §3 (perfil + formulario del caso elegido).
2. **Editar** `audit/validacion_v2/caso_N/input.json` con los datos
   reales (respetando el schema de `TEMPLATE_input.json`).
3. **Ejecutar** con el CLI:
   ```bash
   cd /mnt/c/Users/Jhond/Github/liquidacion_cli
   PYTHONPATH=. uv run --with click --with pydantic --with loguru \
     --with python-dateutil --with Jinja2 --with markdown \
     python3 -m liquidator.cli.main liquidar \
     audit/validacion_v2/caso_N/input.json --json-only \
     --out-dir audit/validacion_v2/caso_N
   ```
   (Comandos completos en STRATEGY.md §4.)
4. **Comparar** el output con tu cálculo manual.
5. **Documentar** discrepancias (si las hay) en `comparativa.md`
   (template en STRATEGY.md §5).
6. **Cerrar** 4.F cuando los 3 casos coincidan (procedimiento en
   STRATEGY.md §6 y §8).

## Modos soportados

- `PERIODICA` — liquidación periódica (cesantías, prima, intereses)
- `FINIQUITO` — liquidación definitiva (incluye vacaciones compensadas
  si aplica; indemnización Art. 64 NO está en v2.0, ver
  `STRATEGY.md §7`)
- `VACACIONES` — solo vacaciones (no usado en los 3 casos)

## DoD (Definition of Done)

- [ ] 3 casos con `input.json` + `output.json` + `comparativa.md`
- [ ] Cada comparativa muestra coincidencia (o discrepancia documentada)
- [ ] Si hay discrepancia → issue abierta + corrección antes de cerrar Fase 4

## Estructura por caso

```
audit/validacion_v2/
├── README.md             ← este archivo
├── STRATEGY.md           ← plan completo (LEER primero)
├── TEMPLATE_input.json   ← schema Forma 1 (plana) de referencia
├── caso_1/               ← "Básico" (PERIODICA, sin segmentación)
│   ├── input.json        ← pendiente: datos reales
│   ├── output.json       ← generado por CLI
│   ├── comparativa.md    ← generado por vos
│   └── notas.md          ← generado por vos
├── caso_2/               ← "Avanzado" (FINIQUITO + SBL variable + vacaciones)
│   └── ...
└── caso_3/               ← "Complejo" (FINIQUITO + IPC + segmentación)
    └── ...
```

## Notas operativas

- **Formato de input:** Forma 1 (plana) por compatibilidad con
  `InputParser` legacy. NO usar `contrato.fecha_ingreso` anidado
  (motor no lo soporta — corresponde a Forma 2 segmentada, que es
  el contrato interno del WorkflowOrchestrator, no input de usuario).
- **Parámetros:** el motor usa automáticamente `params/2025.json` o
  `params/2026.json` según el año de la fecha de corte. NO hardcodear
  SMMLV en el input.
- **Compliance:** si el resultado tiene `compliance_status: NO_GO`, se
  genera `liquidacion_BLOQUEADA.json` (sin PDF, regla AGENTS.md #7).
- **Out of scope:** ver `STRATEGY.md §7` (Art. 64, pago mensual
  intereses, recargo dominical).
