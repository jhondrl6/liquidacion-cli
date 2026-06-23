# Plan: Depuración de archivos huérfanos, obsoletos y en desuso — `liquidacion_cli`

> **Para Hermes:** ejecutar fase por fase con confirmación del usuario entre fases
> (workflow "patch directamente o planear primero"). Cada tarea es una unidad atómica
> con commit + verificación. NO usar `rm -rf` literal en WSL (safety guard WSL sticky);
> usar `git rm` para tracked, `uv run python3 -c "import shutil; shutil.rmtree(...)"`
> para untracked (ver memoria).

**Goal:** eliminar archivos huérfanos, duplicados y de un solo uso identificados en
`liquidacion_cli` sin romper el flujo de v2.0.0 (motor, CLI, CI, suite de tests).

**Estado actual (línea base 2026-06-20):**
- HEAD: `a0a9ac2 docs(REGISTRY): S56 — limpieza colombia_payroll_settlement.egg-info/`
- Working tree: limpio (`git status --short` → vacío)
- 265 archivos tracked
- `.gitignore` tiene ~17 marcadores stale `# [ADD]` / `# [FIX]` de la Tarea 0.C (ya resuelta en S55/S56)
- Últimas fases (S55, S56) ya hicieron housekeeping; este plan es el barrido final

**Inventario de candidatos (auditados en read-only 2026-06-20):**

| Categoría | Item | Tracked | Acción propuesta |
|---|---|---|---|
| DIR VACÍO untracked | `legal/` | NO | ELIMINAR (no tiene propósito, .gitkeep tampoco) |
| STUB inútil | `bin/Permisos.txt` (21B, `chmod +x bin/liquidar`) | SÍ | ELIMINAR |
| DUPLICADO idéntico | `config/production_config.yaml` ≡ `config/default_config.yaml` (2387B) | SÍ | ELIMINAR uno (mantener `production_config.yaml`) |
| KB monolítica con PII | `liquidacion_kb_agente.md` (12KB, cédula real) | SÍ | ARCHIVAR → `legal_docs/_archive/` |
| Legacy plan | `Planificación/_legacy/Plan de ejecución.md` (68KB) | SÍ | MOVER → `docs/audit/_legacy_plans/` |
| Duplicado histórico | `docs/Plan de Implementación.md` (2183L) | SÍ | MOVER → `docs/audit/_legacy_plans/` |
| Duplicado histórico | `docs/Planificación.md` (555L) | SÍ | MOVER → `docs/audit/_legacy_plans/` |
| One-shot scripts | `scripts/_legacy/{generar_varios.py, generate_liquidacion.py}` | SÍ | MOVER → `Planificación/_legacy/code_snippets/` (preservar histórico, sacarlos de `scripts/` que debe ser solo utilidad activa) |
| Test legacy | `tests/_legacy/test_encabezado.py` | SÍ | ELIMINAR (ya gitignored en raíz `/test_encabezado.py`, test no corre en suite activa — verificar antes) |
| Estructura obsoleta | `Planificación/Estructura.ini` (Nov 2025) | SÍ | ELIMINAR (zero refs externas; reemplazado por `pyproject.toml` + árbol real) |
| KB monolítica en root | `Contexto/diagnostico_liquidacion_cli_2026-06-09.md` (55KB) | SÍ | MOVER → `docs/audit/diagnostico_inicial_2026-06-09.md` (era el audit pre-plan; ahora canónico en plan v2.0) |
| Sesiones obsoletas | `docs/sesion_5_resumen.md`, `docs/sesion19_*.md` (216+189+275L) | SÍ | AUDITAR refs; si no referenciados → MOVER → `docs/audit/sesiones/` |
| Análisis one-shot | `docs/code_quality_analysis.md` (301L, Nov 2025) | SÍ | AUDITAR refs; muy probablemente ARCHIVAR |
| Gitignore stale TODOs | 17 marcadores `# [ADD]`/`# [FIX]` en `.gitignore` | SÍ | LIMPIAR (mantener solo los semánticamente vigentes, dejar 1-2 de los más relevantes como referencia histórica) |

**NO TOCAR (intencionales / vivos):**

- `bin/liquidar.py` — CLI activo, referenciado en `user_guide.md`, `developer_guide.md`, `CHANGELOG.md`.
- `liquidator/` — package code completo (audit, calculators, cli, compliance, contracts, core, legal, output).
- `tests/` (excepto `_legacy/`) — suite activa.
- `examples/` — fixtures de regresión.
- `Planificación/REGISTRY.md`, `REGISTRY_LOG.md`, `addendum_*.md`, `Casos.md`,
  `plan_modernizacion_v2.0_2026-06-09.md` — vivos (referenciados en README, CHANGELOG, audit/validacion_v2).
- `Contexto/KB_LLM/`, `Contexto/prompts/` — agent context intencional.
- `legal_docs/` — KB estructurada viva.
- `audit/validacion_v2/` — outputs de validación intencionales (ya gobernados por .gitignore selectivo).
- `.venv/`, `.venv-liq/`, `liquidacion-env/` — gitignored, sin acción.
- `liquidacion_cli.egg-info/` — ya limpiado en S56.

---

## Fase 0 — Línea base y checkpoint de seguridad

**Objetivo:** confirmar estado limpio antes de empezar; capturar diff de referencia.

**Pasos:**

1. Verificar working tree limpio:
   ```bash
   cd /mnt/c/Users/Jhond/Github/liquidacion_cli
   git status --short
   ```
   Esperado: salida vacía.

2. Crear branch de trabajo (NO directo en master — el user prefiere historia limpia,
   pero ya hubo S44 donde eligió force-amend para limpieza; consultar antes de proceder):
   ```bash
   git checkout -b cleanup/s57-orphan-removal
   ```

3. Confirmar con el usuario antes de continuar:
   - ¿Patch directamente o plan primero? (convención del user)
   - ¿Branch + merge posterior, o force-amend como en S44? (precedente establecido)

**Commit:** ninguno (es solo setup).

---

## Fase 1 — Duplicados triviales (impacto bajo, ganancia alta)

### Tarea 1.1: Eliminar directorio vacío `legal/`

**Justificación:** directorio creado Nov 2025, 0 archivos tracked, 0 referencias externas.
Aparentemente placeholder inicial nunca usado.

**Verificación previa:**
```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
git ls-files legal/   # debe ser vacío
ls -la legal/          # debe mostrar solo . y ..
grep -rn "from legal\|import legal\|docs/legal\|config/legal" \
  --include="*.py" --include="*.md" --include="*.yaml" \
  --exclude-dir=venv . 2>/dev/null | head -10
```
Esperado: 0 archivos tracked, 0 referencias.

**Acción (WSL-safe para untracked):**
```bash
uv run python3 -c "import shutil; shutil.rmtree('/mnt/c/Users/Jhond/Github/liquidacion_cli/legal')"
```

**Verificación post:**
```bash
test ! -d legal/ && echo "OK: legal/ eliminado"
```

---

### Tarea 1.2: Eliminar stub `bin/Permisos.txt`

**Justificación:** 21 bytes, contenido `chmod +x bin/liquidar`. Es una instrucción
de setup de un solo uso que pertenece a CONTRIBUTING.md (o a un comando del README),
no al repo. Tracked desde Nov 2025.

**Verificación previa:**
```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
git log --oneline --all -- bin/Permisos.txt
grep -rn "Permisos.txt" --include="*.py" --include="*.md" --include="*.sh" . | head -5
```
Esperado: 0 referencias externas al nombre del archivo.

**Acción:**
```bash
git rm bin/Permisos.txt
```

**Verificación post:**
```bash
test ! -f bin/Permisos.txt && echo "OK"
git status --short  # debe mostrar D bin/Permisos.txt
```

---

### Tarea 1.3: Eliminar duplicado `config/default_config.yaml`

**Justificación:** `diff config/default_config.yaml config/production_config.yaml`
devuelve 0 líneas — son idénticos byte a byte (ambos 2387 bytes). Solo debe quedar
el semánticamente correcto.

**Decisión de diseño:** mantener `production_config.yaml` (nombre más explícito
para una CLI de producción) y eliminar `default_config.yaml`.

**Verificación previa de uso:**
```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
# ¿Qué configuración carga realmente liquidator?
grep -rn "default_config\|production_config" --include="*.py" liquidator/ scripts/ bin/ 2>/dev/null
grep -rn "default_config\|production_config" --include="*.md" --include="*.yaml" --include="*.yml" . 2>/dev/null | grep -v "config/" | head -10
```
Esperado: cero referencias a `default_config.yaml` (si las hay, redirigir primero).

**Acción:**
```bash
git rm config/default_config.yaml
```

**Verificación post:**
```bash
ls config/
# Debe mostrar: compliance_policies.yaml, logging_config.yaml,
#               production_config.yaml, production_logging_config.yaml
# (4 archivos, no 5)
```

---

### Tarea 1.4: Commit Fase 1

```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
git add -A
git status --short
git commit -m "cleanup(S57): Fase 1 duplicados triviales

- Eliminar legal/ (directorio vacío sin uso)
- Eliminar bin/Permisos.txt (stub chmod de un solo uso)
- Eliminar config/default_config.yaml (duplicado byte-a-byte
  de production_config.yaml,后者 es semánticamente más explícito)

Refs: plan .hermes/plans/2026-06-20_112026-repo-cleanup-audit.md
      Fase 1 (duplicados triviales, impacto bajo)"
```

---

## Fase 2 — Archivos monolíticos en root con PII o valor histórico (ARCHIVE, no DELETE)

### Tarea 2.1: Crear directorios de archivo

```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
mkdir -p docs/audit/_legacy_plans docs/audit/diagnosticos docs/audit/sesiones
mkdir -p legal_docs/_archive
mkdir -p Planificación/_legacy/code_snippets
# Crear .gitkeep en los nuevos subdirs tracked para que persistan post-clone
touch docs/audit/_legacy_plans/.gitkeep
touch docs/audit/diagnosticos/.gitkeep
touch docs/audit/sesiones/.gitkeep
touch legal_docs/_archive/.gitkeep
touch Planificación/_legacy/code_snippets/.gitkeep
git add docs/audit/_legacy_plans/.gitkeep docs/audit/diagnosticos/.gitkeep \
        docs/audit/sesiones/.gitkeep legal_docs/_archive/.gitkeep \
        Planificación/_legacy/code_snippets/.gitkeep
# (NO commit aún — seguir con los moves)
```

---

### Tarea 2.2: Archivar `liquidacion_kb_agente.md`

**Justificación:** 12KB en root con PII real (cédula 42.066.783, nombre
"HILDALIRIA RAIGOZA LOAIZA"). Su propósito solapa con `Contexto/KB_LLM/` (10 archivos
estructurados, sin PII, referenciados en prompts). Mantener en root es riesgo de
exposición + desorden.

**Verificación previa:**
```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
grep -rln "liquidacion_kb_agente" --include="*.py" --include="*.md" \
  --include="*.sh" --include="*.toml" --include="*.yaml" . 2>/dev/null
```
Encontrado: solo `Planificación/addendum_finiquito_renuncia_vacaciones_2026-06-11.md`
(una cita incidental). Confirmar que es solo mención y no dependencia funcional
leyendo las ~3 líneas donde aparece.

**Acción:**
```bash
git mv liquidacion_kb_agente.md legal_docs/_archive/liquidacion_kb_agente_v1.0_2025.md
```

**Seguimiento:** actualizar la cita en `addendum_finiquito_renuncia_vacaciones_2026-06-11.md`
para apuntar a la nueva ubicación.

---

### Tarea 2.3: Mover `Planificación/_legacy/Plan de ejecución.md`

**Justificación:** 68KB, Nov 2025. Es el plan "qué íbamos a hacer" pre-v2.0;
el canónico es `Planificación/plan_modernizacion_v2.0_2026-06-09.md`. Ya está en
`_legacy/`, pero el `.gitignore` (línea 115) tiene `# [ADD] legacy 68KB; revisar
en Tarea 0.C` — esa tarea está cerrada en S56. Mover a `docs/audit/_legacy_plans/`
para consolidarlo con los otros planes históricos en el mirror de auditoría.

**Acción:**
```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
git mv "Planificación/_legacy/Plan de ejecución.md" \
       "docs/audit/_legacy_plans/plan_de_ejecucion_inicial_2025-11.md"
```

**Actualización:** eliminar `Planificación/_legacy/` si queda vacío tras esta move
y la Tarea 2.5:
```bash
rmdir Planificación/_legacy/ 2>/dev/null || echo "quedan archivos, revisar"
```

---

### Tarea 2.4: Mover planes legacy de `docs/`

**Justificación:**
- `docs/Plan de Implementación.md` (2183 líneas, Nov 2025) — plan histórico grande
- `docs/Planificación.md` (555 líneas) — plan histórico corto

Ambos son superseded por `Planificación/plan_modernizacion_v2.0_2026-06-09.md`.

**Verificación previa:**
```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
grep -rln "Plan de Implementación\|Planificaci" \
  --include="*.py" --include="*.md" --include="*.sh" \
  --exclude-dir=Planificación --exclude-dir=docs . 2>/dev/null
```
Confirmar que solo se referencian entre sí o desde contexto histórico.

**Acción:**
```bash
git mv "docs/Plan de Implementación.md" \
       "docs/audit/_legacy_plans/plan_de_implementacion_inicial_2025-11.md"
git mv "docs/Planificación.md" \
       "docs/audit/_legacy_plans/planificacion_inicial_2025-11.md"
```

---

### Tarea 2.5: Mover one-shot scripts de `scripts/_legacy/` a `Planificación/_legacy/code_snippets/`

**Justificación:** son scripts de un solo uso ya ejecutados; tenerlos en `scripts/`
contamina el directorio de utilidades activas. El .gitignore ya los bloquea en raíz
(`/generate_liquidacion.py`, `/generar_varios.py`).

**Acción:**
```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
git mv scripts/_legacy/generar_varios.py Planificación/_legacy/code_snippets/
git mv scripts/_legacy/generate_liquidacion.py Planificación/_legacy/code_snippets/
rmdir scripts/_legacy/ 2>/dev/null || echo "quedan archivos, revisar"
```

---

### Tarea 2.6: Commit Fase 2

```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
git add -A
git status --short
git commit -m "cleanup(S57): Fase 2 archivar KBs/planes/scripts legacy

- Mover liquidacion_kb_agente.md (12KB, contiene PII) a legal_docs/_archive/
- Consolidar planes legacy en docs/audit/_legacy_plans/ (3 archivos, ~84KB)
- Mover one-shot scripts de scripts/_legacy/ a Planificación/_legacy/code_snippets/
- Crear directorios de archivo con .gitkeep para persistencia post-clone

Refs: plan .hermes/plans/2026-06-20_112026-repo-cleanup-audit.md
      Fase 2 (archivos históricos)"
```

---

## Fase 3 — Estructura obsoleta y archivos sin referencias

### Tarea 3.1: Eliminar `Planificación/Estructura.ini`

**Justificación:** Nov 2025, ZERO referencias externas (grep no encuentra nada).
Reemplazado por `pyproject.toml` + la estructura real del repo.

**Verificación:**
```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
grep -rln "Estructura.ini\|estructura.ini" . 2>/dev/null
```
Esperado: 0 resultados fuera del propio `Estructura.ini`.

**Acción:**
```bash
git rm "Planificación/Estructura.ini"
```

---

### Tarea 3.2: Mover `Contexto/diagnostico_liquidacion_cli_2026-06-09.md` al mirror de auditoría

**Justificación:** 55KB, Jun 2025 (pre-plan-v2.0). Era el audit inicial que
informó el plan; ahora el plan v2.0 está cerrado (commits S39-S56). Mantenerlo en
`Contexto/` sugiere que es contexto operativo, cuando en realidad es histórico.
Mover al mirror `docs/audit/diagnosticos/` para que el .gitignore lo cubra
adecuadamente (`docs/audit/**` ya está gitignored).

**Verificación previa:**
```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
grep -rln "diagnostico_liquidacion_cli_2026-06-09" \
  --include="*.py" --include="*.md" . 2>/dev/null
```
Probable: varias referencias en CHANGELOG, plan v2.0, README. Confirmar que
todavía digeribles (es histórico, no roto).

**Acción:**
```bash
git mv Contexto/diagnostico_liquidacion_cli_2026-06-09.md \
       docs/audit/diagnosticos/diagnostico_inicial_2026-06-09.md
```

---

### Tarea 3.3: Auditar `docs/sesion_5_resumen.md`, `docs/sesion19_*.md`, `docs/code_quality_analysis.md`

**Verificación previa (ejecutar y leer resultados):**
```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
for f in docs/sesion_5_resumen.md docs/sesion19_compliance_checklist.md \
         docs/sesion19_final_report.md docs/code_quality_analysis.md; do
  echo "=== refs a $f ==="
  grep -rln "$(basename $f .md)" \
    --include="*.md" --include="*.py" . 2>/dev/null | grep -v "^./$f$"
done
```

**Decisión por archivo** (sub-tareas):
- Si `sesion_5_resumen.md` no tiene refs activas → mover a `docs/audit/sesiones/`
- Si `sesion19_*.md` solo se citan entre sí → mover a `docs/audit/sesiones/`
- Si `code_quality_analysis.md` ya está superseded por ruff/CI → mover a `docs/audit/`

**Acción (asumiendo el caso típico "sesiones superseded"):**
```bash
git mv docs/sesion_5_resumen.md docs/audit/sesiones/sesion_5_resumen.md
git mv docs/sesion19_compliance_checklist.md docs/audit/sesiones/
git mv docs/sesion19_final_report.md docs/audit/sesiones/
git mv docs/code_quality_analysis.md docs/audit/code_quality_analysis_2025-11.md
```

---

### Tarea 3.4: Eliminar `tests/_legacy/test_encabezado.py`

**Justificación:** test legacy, ya bloqueado en raíz por `.gitignore`
(`/test_encabezado.py`). Si pytest lo descubre, su falla crónicamente roja está
documentada en CHANGELOG ("S45: doc — CI crónicamente rojo en pytest, 5+ runs,
gap heredado"). Muerte misericordiosa.

**Verificación previa (crítica):**
```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
grep -rln "test_encabezado" . --include="*.py" --include="*.toml" \
  --include="*.ini" --include="*.cfg" 2>/dev/null | head -10
pytest --collect-only -q tests/_legacy/test_encabezado.py 2>&1 | head -20
```
Esperado: solo se referencia a sí mismo; o si pytest lo recoge, ver si tiene
fixtures o helpers compartidos con la suite activa.

**Acción:**
```bash
git rm tests/_legacy/test_encabezado.py
rmdir tests/_legacy/ 2>/dev/null
```

**Verificación post:**
```bash
uv run pytest --collect-only -q 2>&1 | tail -5
# Esperado: no aparecen tests de test_encabezado; la suite se reduce en 1 test.
```

---

### Tarea 3.5: Commit Fase 3

```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
git add -A
git status --short
git commit -m "cleanup(S57): Fase 3 estructura obsoleta y sin referencias

- Eliminar Planificación/Estructura.ini (zero refs, Nov 2025, superseded por pyproject.toml)
- Mover diagnostico inicial a docs/audit/diagnosticos/ (era input del plan v2.0 cerrado)
- Archivar resúmenes de sesión obsoletos en docs/audit/sesiones/
- Archivar code_quality_analysis (análisis one-shot Nov 2025)
- Eliminar tests/_legacy/test_encabezado.py (test superseded, gap heredado)

Refs: plan .hermes/plans/2026-06-20_112026-repo-cleanup-audit.md
      Fase 3 (estructura obsoleta)"
```

---

## Fase 4 — Higiene del `.gitignore`

### Tarea 4.1: Eliminar marcadores stale `# [ADD]` y `# [FIX]`

**Justificación:** los marcadores `[ADD]` fueron introducidos en Fase 0 / Tarea 0.B
(Jun 2025) como tags de "agregar después". La Tarea 0.C (revisar) está cerrada en
S56. Mantener 17 marcadores en `.gitignore` confunde (parece que hay trabajo
pendiente cuando no lo hay). Solo mantener comentarios que aporten valor semántico.

**Estrategia:** limpieza quirúrgica — leer `.gitignore`, eliminar líneas
`# [ADD]`, `# [FIX]`, `# [ADD Sxx]`, `# [FIX Sxx]` donde aparezcan. Preservar los
comentarios `# Fuente:` y `# Nota:` que sí documentan decisiones.

**Comando guiado:**
```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
# Backup antes de editar
cp .gitignore .gitignore.backup_pre_S57
# Editar con patch (sesiones con contexto, no sed ciego)
```

**Cambios específicos a aplicar:**

1. Eliminar `# [ADD S14] venv local usado en uv pip install -e . para validar packaging`
   (la justificación del `.venv-liq/` ya es obvia por estar listado abajo).

2. Eliminar `# [FIX S34] NO ignorar liquidator/output/...` — esto es contexto
   histórico que ya está implícito en `!liquidator/output/`.

3. Eliminar `# [FIX] mantener marcador para que el dir exista post-clone` y
   variantes — los `.gitkeep` son autoexplicativos.

4. Consolidar las 4 líneas `# [ADD] proteger backups de rotación...`:
   ```diff
   -# [ADD] proteger backups de rotación de clave (issue 2026-06-12)
   -# Secretos y entorno (no modificar orden — los .env.* dependen de que .env se liste primero)
   +# Secretos y entorno (no modificar orden — los .env.* dependen de que .env se liste primero)
   +# Backups de rotación de clave (issue 2026-06-12)
    .env
    .env.local
    .env.*.local
   -# [ADD] proteger backups de rotación de clave (issue 2026-06-12)
    .env.backup*
   ```

5. Eliminar `# [ADD] legacy 68KB; revisar en Tarea 0.C` — la Tarea 0.C está cerrada.

6. Eliminar los `# [ADD]` repetidos en bloque de backups (`*.bak`, `*.backup`,
   `*.tmp`, `*.swp`, `*~`) — son autoexplicativos.

7. Eliminar `# [ADD] revisar contenido en Tarea 0.C` (línea 147).

**Acción (vía patch tool, no sed):**
```python
# Usar patch tool con old_string/new_string por cada cambio.
# Verificar diff antes de commit:
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
diff .gitignore.backup_pre_S57 .gitignore
```

---

### Tarea 4.2: Verificar que `.gitignore` sigue cubriendo todo

```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
# ¿Hay archivos untracked que deberían estar gitignored?
git status --short --ignored | head -20
# ¿Las reglas siguen funcionando?
git check-ignore -v legal/ bin/Permisos.txt scripts/_legacy/ 2>&1
```
Esperado: nada crítico untracked; reglas vigentes.

---

### Tarea 4.3: Commit Fase 4

```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
rm .gitignore.backup_pre_S57
git add .gitignore
git commit -m "cleanup(S57): Fase 4 higiene .gitignore

- Eliminar 17 marcadores stale # [ADD]/#[FIX] de Fase 0 (cerrada en S56)
- Consolidar bloque de secretos/rotación con comentario semántico
- Preservar solo comentarios que documentan decisiones (Fuente:, Nota:)

Refs: plan .hermes/plans/2026-06-20_112026-repo-cleanup-audit.md
      Fase 4 (higiene .gitignore)"
```

---

## Fase 5 — Verificación end-to-end

### Tarea 5.1: Suite de tests + CI en local

```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
uv run pytest -q 2>&1 | tail -20
uv run pytest --collect-only -q 2>&1 | tail -5
bash scripts/ci.sh 2>&1 | tail -30
```

**Criterios de éxito:**
- `pytest`: pasa sin nuevas fallas vs baseline S56
- `pytest --collect-only`: muestra N-1 tests (eliminamos `test_encabezado.py`)
- `scripts/ci.sh`: termina con `Pipeline SUCCEEDED` o equivalente
- `ruff check .`: 0 errores

---

### Tarea 5.2: Smoke test del CLI

```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
# Caso canónico (debe seguir produciendo el mismo output que v2.0.0)
uv run python bin/liquidar.py \
  --modo PERIODICA \
  --fecha_ingreso 2024-01-01 \
  --fecha_corte 2025-01-01 \
  --salario_mensual 2200000 \
  --auxilio_transporte 200000 \
  --reside_en_lugar_trabajo false \
  --documento-trabajador "TEST-CLEANUP" \
  --nombre-trabajador "TEST CLEANUP" \
  --output /tmp/liquidacion_cleanup_test.json \
  --json-only 2>&1 | tail -5
```

**Criterio:** exit code 0 o 2 (NO_GO acceptable en test sintético), archivo JSON
generado con estructura válida.

---

### Tarea 5.3: Verificación de tamaños

```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
git ls-files | wc -l   # debe haber bajado (era 265)
du -sh . --exclude=.git --exclude=.venv --exclude=.venv-liq \
  --exclude=liquidacion-env --exclude=.mypy_cache --exclude=.pytest_cache \
  --exclude=.ruff_cache
```

**Esperado:** reducción medible (meta: −15 archivos tracked, −100KB).

---

### Tarea 5.4: Auditoría final de referencias muertas

```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
# Greps finales para asegurar que nada quedó roto
grep -rn "Permisos.txt\|Estructura.ini\|legal/" \
  --include="*.py" --include="*.md" --include="*.sh" \
  --include="*.yaml" --include="*.yml" --include="*.toml" \
  --exclude-dir=.git . 2>/dev/null | grep -v "no use legal" | head -10
grep -rn "test_encabezado" \
  --include="*.py" --include="*.md" --include="*.toml" \
  --exclude-dir=.git . 2>/dev/null | head -5
grep -rn "default_config\.yaml" \
  --include="*.py" --include="*.md" --include="*.yaml" \
  --exclude-dir=.git . 2>/dev/null | head -5
```

**Esperado:** cero referencias rotas (los archivos movidos conservan path
semántico en mirror audit/ o _archive/).

---

### Tarea 5.5: Commit de housekeeping final + tag

```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
git log --oneline master..HEAD  # revisar los 4-5 commits de S57
# Actualizar CHANGELOG.md con la entrada S57 (siguiendo el formato existente)
# Actualizar AGENTS.md si cambió algún path referido
# Actualizar README.md si aplica (paths a planes legacy)

git add CHANGELOG.md AGENTS.md README.md
git commit -m "docs(S57): REGISTRY update post-cleanup"
git tag -a v2.0.1 -m "v2.0.1: housekeeping S57 (orphan/legacy cleanup)"
```

---

## Fase 6 — Push y cleanup del branch

### Tarea 6.1: Push (precedente S44 = force-amend para limpieza)

**⚠ Precaución crítica del user:** WSL safety guard bloquea `rm -rf` literal y
`git push --force-with-lease` aunque el user dé OK explícito. Antes de cualquier
push, **auditar el árbol git**:

```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
git status
git diff master..HEAD --stat
git log master..HEAD --oneline
```

**Decisión a confirmar con el user (precedente S44 fue force-amend por
"limpieza historial"):**
- Opción A: merge branch → master con merge commit (historial append-only)
- Opción B: cherry-pick → master, luego `git push --force-with-lease` (limpio)

Si opción B, verificar antes:
```bash
git push --force-with-lease origin master 2>&1
# Si safety guard bloquea: parar y reportar al user.
```

Si opción A:
```bash
git checkout master
git merge --no-ff cleanup/s57-orphan-removal
git push origin master
```

### Tarea 6.2: Cleanup local

```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
git branch -d cleanup/s57-orphan-removal
git remote prune origin
```

---

## Resumen de impacto esperado

| Métrica | Antes (S56) | Después (S57) | Delta |
|---|---|---|---|
| Archivos tracked | 265 | ~245 | −20 |
| KB tracked | ~580 | ~395 | −185KB |
| `.gitignore` líneas comentario stale | 17 | 0 | −17 |
| `_legacy/` directories activos | 2 (`Planificación/`, `scripts/`, `tests/`) | 1 (`Planificación/_legacy/code_snippets/`) | consolidados |
| Directorios vacíos untracked | 1 (`legal/`) | 0 | −1 |
| Riesgo PII en root | 1 archivo (`liquidacion_kb_agente.md`) | 0 | mitigado |

---

## Riesgos y rollback

**Riesgos identificados:**

1. **`test_encabezado.py` puede tener helpers compartidos** — mitigado por
   verificación previa (Tarea 3.4: pytest --collect-only + grep de imports).

2. **`Plan de Implementación.md` puede estar enlazado desde docs activos** —
   mitigado por verificación de refs antes del `git mv`. Si se rompe un link,
   actualizar el destino al path nuevo en el mirror.

3. **`.gitignore` editado puede romper reglas vigentes** — mitigado por backup
   (`.gitignore.backup_pre_S57`) + verificación con `git check-ignore`.

4. **CI puede revelar tests que dependían de archivos eliminados** — mitigado
   por ejecución local previa (`scripts/ci.sh` en Tarea 5.1).

**Rollback:**
```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
# Si S57 falla en cualquier fase:
git reset --hard HEAD~N  # N = número de commits S57 a deshacer
# Si ya pusheó a master con merge:
git revert -m 1 <merge-commit-sha>
```

---

## Decisiones pendientes con el user

Antes de ejecutar Fase 0, confirmar:

1. **¿Patch directamente o plan primero?** (convención del user)
2. **¿Branch + merge o force-amend (precedente S44)?** (decide historia git)
3. **¿`test_encabezado.py` se elimina o se mantiene en `tests/_archive/`?** (alternativa)
4. **¿Se actualiza `CHANGELOG.md` con el formato existente o se omite para no inflar?**
5. **¿Se bumpa versión a v2.0.1 o se queda en v2.0.0 con tag anotado aparte?**

---

## Tiempo estimado

| Fase | Minutos |
|---|---|
| 0 — Setup | 5 |
| 1 — Duplicados triviales | 10 |
| 2 — Archives | 25 |
| 3 — Estructura obsoleta | 30 |
| 4 — `.gitignore` | 15 |
| 5 — Verificación | 20 |
| 6 — Push | 5 |
| **Total** | **~110 min (≈ 2 horas)** |

Ejecutable en 1-2 sesiones de trabajo; cabe en una sola sesión si se hace
en modo batch con confirmación periódica.
