# 07 — Checklist de generación de liquidación (operación)

> Procedimiento operativo para correr una liquidación sin saltarse
> pasos. Inspirado en el plan §5.6-5.7. **No reemplaza la suite de
> tests**; es para uso humano (operador) o asistente (LLM) en sesión.

## Fase A — Pre-cálculo (antes de invocar el motor)

1. **Leer el input completo** y validar a ojo:
   - ¿Las fechas son coherentes? (ingreso < corte)
   - ¿El salario_mensual es positivo?
   - ¿El modo es coherente con la terminación del contrato? (FINIQUITO
     requiere `fecha_terminacion_real` set).
   - **Anonimizar** si vas a loguear, copiar a KB o commitear.
2. **Resolver los params por año:**
   - Si el periodo NO cruza 1-ene → 1 archivo `params/<año>.json`.
   - Si cruza 1-ene → 2+ archivos, uno por segmento. Ver
     `02_parametros_vigentes.md` y `04_schema_entrada.md`.
3. **Verificar que la KB está vigente:**
   - `ls Contexto/KB_LLM/` debe mostrar 9-10 archivos (00-09).
   - Si la última nota tiene >30 días sin re-validar, **re-validar**
     antes de confiar.
4. **Verificar que el caso canónico de cordura** (`09_caso_canonico_usuario.md`)
   está verde. Si no, no se puede asegurar que el motor esté sano;
   primero arreglar el canónico.
5. **Cargar el checklist:** `params/checklist.json` debe tener las
   reglas V001-V010 con `severity` y `blocking` correctos.

## Fase B — Cálculo (durante la corrida)

6. **Ejecutar el motor** con el input del paso 1.
7. **Inspeccionar el output:**
   - ¿`meta.parametros_por_segmento` tiene un objeto por segmento?
   - ¿`desglose` agrupa por año?
   - ¿`total_liquidacion` = suma de `desglose[*][*]`?
   - ¿`compliance_report.compliance_status` es `GO` o `WARN`?
   - Si `NO_GO`: ¿hay override documentado? Si no, abortar y NO
     generar PDF/MD.

## Fase C — Pre-generación (antes de emitir artefactos)

8. **Compliance verde:**
   - Estado = `GO` o `WARN` → OK.
   - Estado = `NO_GO` → abortar (regla AGENTS.md #7).
   - Estado = `OVERRIDE_APPROVED` → OK, **pero el `OverrideRecord`
     debe estar en el output** (sección `compliance_report.overrides`).
9. **Contexto completo:**
   - `normas_aplicadas` lista las citas de `params/normas.json`.
   - Cada cita tiene `url` válida (no placeholder `?i=XXXXXX`).
10. **Plantillas renderizan (Fase 3+):**
    - Si la plantilla Jinja falla, NO emitir PDF. Loguear el error.
    - Si la plantilla genera campos vacíos en renglones que sí
      tienen valor, es bug de plantilla: NO emitir.
11. **Auditoría registrada:**
    - `meta.input_hash` se computa y registra.
    - `meta.fecha_generacion` se setea en el momento de la corrida.
    - `meta.motor_version` matchea la versión del repo
      (`liquidator/__init__.py` o similar).

## Fase D — Emisión

12. **Generar artefactos derivados** (Fase 3+):
    - `liquidacion_<caso>.json` (siempre, es la fuente).
    - `liquidacion_<caso>.md` (vista humana).
    - `liquidacion_<caso>.pdf` (documento final, solo si compliance OK).
    - Si `NO_GO` y NO override: `liquidacion_<caso>_BLOQUEADA.{md,pdf}`
      con explicación.
    - **Regla dura:** NO disfrazar `.txt` como `.pdf` (AGENTS.md #8).
13. **Mover outputs a `output/`:**
    - Nunca en la raíz. Si la corrida los dejó en raíz, mover a
      `output/<caso>/` o `output/_legacy/`.
14. **No usar outputs como expected values:**
    - El primer output de un caso es un *candidato*, no la verdad.
    - El expected value solo se acepta cuando está firmado por el
      usuario (ver §6.8 del diagnóstico: "3 liquidaciones reales
      verificadas por Jhond").

## Fase E — Post-corrida

15. **Si la corrida reveló un bug o un gap:** abrir issue y
    referenciarlo en `06_riesgos_modelo.md` o en
    `Planificación/REGISTRY.md` (log de cierres, columna "Notas").
16. **Si modificaste params/reglas:** sincronizar
    `Contexto/KB_LLM/02_parametros_vigentes.md` y
    `03_compliance_blocking.md` antes de cerrar sesión.
17. **Si tocaste un addenda:** verificar que la decisión aprobada
    no haya cambiado; si cambió, documentar en el addenda y
    re-evaluar aprobación (ver regla de cierre de sesión en
    `REGISTRY.md` punto 5).

## Última validación contra código

- **Fecha:** 2026-06-13 (sesión S5, Tarea 0.E).
- **Verificado:** la lista refleja plan §5.6-5.7 y reglas AGENTS.md
  del plan §0.G.
- **NO verificado:** que el motor (Fase 1+) implemente los pasos
  6-7 (cálculo y output con shape esperado). Esta nota es la
  promesa de lo que el motor DEBE hacer; la verificación es el
  golden test de Fase 1 Tarea 1.B.
