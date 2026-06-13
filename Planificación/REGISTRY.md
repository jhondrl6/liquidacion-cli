# REGISTRY — liquidacion_cli v2.0

> **Fuente de verdad de progreso de fases.** Se actualiza OBLIGATORIAMENTE al cerrar
> cada sesión. Operador o agente lee este archivo PRIMERO al abrir sesión; el
> plan completo (3.353 líneas) solo se consulta cuando se necesita detalle.
>
> **Granularidad:** una entrada por sesión (alineado con la convención "1 fase
> por sesión" del plan §3). Una sesión puede cerrar cero, una o varias tareas
> puntuales, pero solo cierra UNA fase como máximo.

---

## Estado actual (leer primero)

- **Última sesión cerrada:** S9 — 2026-06-13 (Tarea 0.I — `git init` + commit inicial limpio `f04d639`, 200 archivos, 43.477 insertions, con `.gitkeep` en `output/`, `audit/`, `artifacts/`, `logs/`)
- **Última fase cerrada:** (ninguna) — Fase 0 requiere 0.A-0.K; 0.A-0.I ✓, pendientes 0.J y 0.K.
- **Próxima tarea a ejecutar:** Fase 0 — Tarea 0.J (suite `pytest liquidator/tests` 100% verde o fallos documentados en `06_riesgos_modelo.md`)
- **Bloqueos activos:** 0.J pendiente. PENDIENTE (pospuesto por usuario): eliminación de `__pycache__/`, `htmlcov/`, `.coverage`, `liquidacion_nomina_colombia.egg-info/`, `documentos_legales_rurales/` (vacío). Issue conocido post-S9: patrón `.env.backup*` del .gitignore NO matchea `.env.backup_pre_rotation_2026-06-12` en este FS WSL/Windows; el archivo queda untracked (intencional, no se commitea) pero el patrón sigue roto. Fix pendiente en sesión futura.

---

## Tabla de fases

| Fase       | Título                                                | Estado        | Cerrada | Pendiente / Notas                                              |
|------------|-------------------------------------------------------|---------------|---------|----------------------------------------------------------------|
| 0          | Higiene + segundo cerebro mínimo                      | EN CURSO      | —       | 0.A ✓, 0.B ✓, 0.C ✓, 0.D ✓, 0.E ✓, 0.F ✓, 0.G ✓, 0.H ✓, 0.I ✓. Próximas: 0.J, 0.K. |
| 1          | Estabilizar y formalizar                              | BLOQUEADA     | —       | Requiere Fase 0 cerrada.                                       |
| 1.C-bis    | (Addendum SL2630) Schema `Salario` extendido          | NO INICIADA   | —       | Anidada en Fase 1. Aditiva retrocompatible.                    |
| 1.C-ter    | (Addendum finiquito) Schema `Contrato` + `Vacaciones` | NO INICIADA   | —       | Anidada en Fase 1. Aditiva retrocompatible.                    |
| 2          | Contrato legal y cálculo correcto                     | BLOQUEADA     | —       | Requiere Fase 1.                                               |
| 2.B-bis    | (Addendum SL2630) `SalarioResolver` SBL por año       | NO INICIADA   | —       | Anidada en Fase 2.                                             |
| 2.B-ter    | (Addendum finiquito) Vacaciones compensadas           | NO INICIADA   | —       | Anidada en Fase 2.                                             |
| 2.Z        | (Addendum finiquito) Compliance vacaciones            | NO INICIADA   | —       | Anidada en Fase 2.                                             |
| 2-bis      | IPC + anualización salarial (nueva)                   | NO INICIADA   | —       | Plan §7-bis. Requiere Fase 2.                                  |
| 3          | Documento generable robusto                           | BLOQUEADA     | —       | Requiere Fase 2.                                               |
| 3.G        | (Addendum finiquito) PreRender por motivo             | NO INICIADA   | —       | Anidada en Fase 3.                                             |
| 4          | v2.0 release                                          | BLOQUEADA     | —       | Requiere 0-3 + 3 liquidaciones reales verificadas.            |
| 5          | Investigación casos reales (opcional)                 | CONDICIONAL   | —       | Solo si surgen casos en Fases 0-4.                             |

**Estados posibles:** NO INICIADA · EN CURSO · BLOQUEADA · CERRADA · CONDICIONAL · CANCELADA.

---

## Decisiones de addendas (vigentes)

### Addendum SL2630-2024 + IPC
- **Archivo:** `Planificación/addendum_sl2630_y_ipc_2026-06-09.md`
- **Estado:** APROBADO CON REPAROS. Absorbido en v2.0.0 (NO como v2.0.1).
- **Distribución:** Tarea 1.C-bis → Fase 1; Tarea 2.B-bis → Fase 2; Tarea 2.X → Fase 2-bis.
- **Reparos bloqueantes (cerrar antes de Fase 2-bis DoD):**
  - (a) NO usar Art. 155 CST para prescripción — usar **Art. 488 CST**.
  - (b) Verificar texto literal, sala y URL oficial de **SL2630-2024** antes de cerrar.
  - (c) Modelar IPC como **índices acumulados**, NO como tasas anuales de inflación.

### Addendum finiquito por renuncia + vacaciones compensadas
- **Archivo:** `Planificación/addendum_finiquito_renuncia_vacaciones_2026-06-11.md`
- **Estado:** APROBADO CON REPAROS. Absorbido en v2.0.0.
- **Distribución:** Tarea 1.C-ter → Fase 1; Tarea 2.B-ter → Fase 2; Tarea 2.Z → Fase 2; Tarea 3.G → Fase 3.
- **Reparos bloqueantes (cerrar antes de DoD de cada tarea):**
  - (a) Verificar **Art. 189 CST párr. 1°** en SUIN (`https://www.suin-juriscol.gov.co/`) antes de cerrar 2.B-ter; registrar `estado_verificacion: "VERIFICADO"` con URL y fecha en `params/normas.json` (entrada `CST_189_VACACIONES`).
  - (b) El motor debe distinguir *vacaciones compensadas por acuerdo mutuo* (Art. 189) de *vacaciones obligatoriamente compensadas en finiquito* (Art. 189 párr. 1° + Art. 190) — modo `FINIQUITO` invoca `calculate_vacaciones_compensadas_finiquito`; modo `PERIODICA` NO.
  - (c) **Indemnización Art. 64 CST NO se implementa en v2.0** (queda referenciada en `Contexto/KB_LLM/01_reglas_calculo.md` para casos futuros).

---

## Regla de cierre de sesión (a transcribir a AGENTS.md cuando se cree en Fase 0)

Al cerrar sesión, en este orden:
1. **Validar DoD contra código vivo** (regla §5.5.11 del diagnóstico: si código y plan discrepan, código gana).
2. **Actualizar este REGISTRY.md** — cambiar estado de fase/tarea, agregar entrada al log de cierres.
3. **Si quedó alguna fase cerrada**, agregar entrada en `CHANGELOG.md` bajo `[Unreleased]`.
4. **Si hubo cambio en params/reglas**, sincronizar `Contexto/KB_LLM/` correspondiente (cuando exista en Fase 0+).
5. **Si se tocó un addenda**, verificar que la decisión aprobada no haya cambiado (si cambió, documentar en el addenda y re-evaluar aprobaciones).

**No cerrar sesión sin completar los 5 puntos.**

---

## Log de cierres de sesión

(Orden cronológico inverso — más reciente arriba. Una fila por sesión cerrada.)

| # | Fecha | Sesión ID | Fase / Tareas cerradas | Evidencia (archivos tocados, tests corridos) | DoD verificado |
|---|-------|-----------|------------------------|----------------------------------------------|----------------|
| 9 | 2026-06-13 | S9 | Fase 0 / Tarea 0.I — `git init` + commit inicial limpio | `git init` en `master` (default WSL); `git config user.name "Jhond"` + `git config user.email "jhondrl@hermes"` (placeholder del plan §5.2 T0.I, sobrescribible con `git config user.email "[email Jhond]" && git commit --amend --reset-author --no-edit`). `.gitkeep` añadido a `output/`, `audit/`, `artifacts/`, `logs/` (4 dirs, completa el contrato del .gitignore líneas 48-52 con las excepciones `!X/.gitkeep`). 1 commit: `f04d639 chore(fase-0): repo inicial limpio con KB, .gitignore, sintaxis corregida, scripts espurios reubicados` (200 files, 43.477 insertions). Pre-commit blockers resueltos: 1 crítico (`.env.backup_pre_rotation_2026-06-12` con clave antigua SHA256 `de1b22...8868` INVALIDADA en S1) y 4 de logs (`audit/logs/audit_202511.log`, `audit_202512.log`, `audit_202606.log`, `docs/audit/logs/audit_202511.log`) quedaron untracked y NO en el commit. Validación: `git status` post-commit muestra 0 staged, 0 modified, 3 untracked intencionales (los 2 dirs `audit/logs/`, `docs/audit/` ignorados por `audit/` pattern, y `.env.backup_*` por bug conocido del patrón — ver Bloqueos activos). 6 checks de handoff de S8 re-ejecutados: KB 10/10 ✓, prompts ✓, AGENTS.md ✓, `check_kb_freshness.py` exit 0 ✓, .git ✓, Art. 155 en `06_riesgos_modelo.md` (5 matches esperados, documenta R-LEG-02). | Parcial — orden estricto cumplido (0.A→0.B→...→0.I) ✓; pre-condiciones S8 verificadas ✓; commit inicial limpio ✓. Pendiente Fase 0: 0.J (suite pytest real en Windows venv) y 0.K (params 2026 activos en KB). |
| 8 | 2026-06-13 | S8 | Fase 0 / Tarea 0.H — `scripts/check_kb_freshness.py` year-aware + `liquidator/tests/test_kb_freshness.py` con 6 tests, validados manualmente | 2 archivos creados: `scripts/check_kb_freshness.py` (157 líneas, 5.3 KB) y `liquidator/tests/test_kb_freshness.py` (189 líneas, 6.7 KB). Script year-aware: itera `params/[0-9][0-9][0-9][0-9].json` por glob (cubre 2025 + 2026 vigentes y años futuros sin tocar el script). 4 chequeos: (1) campos monetarios grandes (SMMLV, AUXILIO_TRANS) de cada `params/<año>.json` están citados en `KB_LLM/02_parametros_vigentes.md` con normalización de separadores de miles (acepta `1.423.500`, `1,423,500`, `1423500`); (2) 10 notas KB presentes (00-09); (3) `AGENTS.md` referencia el diagnóstico vigente `diagnostico_liquidacion_cli_2026-06-09.md`; (4) helper `_kb_02` acepta el nombre `02_parametros_vigentes.md` (Tarea 0.K) o el legado `02_parametros_2025.md` (Tarea 0.E). Salida: `KB fresh.` + exit 0 si todo OK; `ERROR: <motivo>` en STDERR + exit 1 si encuentra desactualización. Suite: 6 funciones de test (`test_kb_freshness_exits_zero`, `test_kb_freshness_informe_clara_errores`, `test_kb_has_ten_notes`, `test_agents_md_references_diagnostico`, `test_params_smmlv_citado_en_kb` parametrizado para 2025/2026, `test_params_futuro_sera_detectado`). Validación: las 6 funciones ejecutadas en aislamiento pasan; script `python3 scripts/check_kb_freshness.py` retorna 0; 4 escenarios de fallo (params/2099.json inventado, SMMLV 2026 alterado a 1.900.000) detectan y reportan error específico con archivo:línea-correctos. pytest real no ejecutado en este WSL (sin pytest instalado y `uv run --with pytest` bloqueado por política de seguridad); próximo en Windows venv (`liquidacion-env/Scripts/pytest.exe`) por el usuario. | Parcial — script ✓ y suite ✓, ambas validadas; pytest real bloqueado por entorno (sin pytest en WSL ni en liquidacion-env). Pendiente: correr `pytest liquidator/tests/test_kb_freshness.py -v` en Windows para confirmar 6/6 con el runner real. |
| 6 | 2026-06-13 | S6 | Fase 0 / Tarea 0.F — Crear `Contexto/prompts/` con 3 prompts | 3 archivos .md creados (581 líneas totales, 24.6 KB). `prompt_generacion_liquidacion.md` (171 líneas): workflow A/B/C pre-cálculo/cálculo/post-cálculo, 10 reglas inamovibles (no hardcodear, no PDF si NO_GO, prescripción Art. 488, etc.), formato de respuesta obligatorio con cita legal y params_version. `prompt_auditoria_antes_de_responder.md` (176 líneas): 5 pasos de auditoría, formato con evidencia verbatim (archivo:línea), lista "lo que NUNCA debés hacer" (no inventar URLs SUIN, no aceptar doc como verdad). `prompt_plan_modernizacion.md` (234 líneas): 5 checks contra disco, decisión "1 fase por sesión" como máximo, resumen de las 2 addendas vigentes con sus reparos bloqueantes, 11 trampas conocidas. Sync mínimo en `Contexto/KB_LLM/00_fuente_de_verdad.md` (una línea apuntando a `Contexto/prompts/` como capa operativa de la KB). CHANGELOG.md `[Unreleased]` actualizado (3 prompts movidos de Pending a Added). | ✓ — `ls Contexto/prompts/` muestra 3 archivos, c/u ≥20 líneas (DoD plan §5.2 T0.F: 171/176/234). |
| 4 | 2026-06-12 | S4 | Fase 0 / Tarea 0.D — Corregir 5 archivos con SyntaxError | 5 imports rotos de `datetime` corregidos: `markdown_generator.py` (`from datetime`→`import datetime`), `params_versioning.py` (`from datetime`→`import datetime`), `test_trail_generator.py` (`from datetime` eliminado, no usado), `test_indemnizacion.py` (`from datetime , timedelta`→`from datetime import datetime, timedelta`), `test_override.py` (`from datetime`→`import datetime`). `docs/Plan de Implementación.py` (hallazgo adicional, carácter `│` + .py en doc) renombrado a `.md`. 102/102 .py compilan limpios. | ✓ — 0 SyntaxError en sweep completo. |
| 5 | 2026-06-13 | S5 | Fase 0 / Tarea 0.E — Crear `Contexto/KB_LLM/` con 9 notas | 10 archivos .md creados (00-09, 1.226 líneas totales, 61 KB). `00_fuente_de_verdad.md` (jerarquía código > params > tests > legal > docs). `01_reglas_calculo.md` (cesantías, intereses 12%, prima, vacaciones, Art. 64 referenciado NO implementado). `02_parametros_vigentes.md` (SMMLV/aux_trans 2025 y 2026, regla de selección por `fecha_corte`, pendientes URL Decretos 1469/1470/2025). `03_compliance_blocking.md` (GO/WARN/NO_GO/OVERRIDE_APPROVED, V001-V010, mecánica `OverrideRecord`). `04_schema_entrada.md` (Forma 1 informal + Forma 2 segmentada, campos pendientes addendas 1.C-bis/1.C-ter). `05_schema_salida.md` (shape `liquidacion_result.json` con `meta.parametros_por_segmento` por año). `06_riesgos_modelo.md` (12 riesgos R-LEG-01 a R-SEC-01, prescripción Art. 488 CST no Art. 155, SL2630-2024 pendiente, Art. 189 párr. 1° pendiente SUIN). `07_checklist_generacion_liquidacion.md` (17 pasos A-E pre/durante/post). `08_arquitectura_segundo_cerebro.md` (6 capas, no fine-tuning). `09_caso_canonico_usuario.md` (caso ancla 206 días, SBL 2.200.000, valores TBD-motor-Fase1). CHANGELOG.md `[Unreleased]` actualizado. | ✓ — `ls Contexto/KB_LLM/` muestra 10 archivos (00-09), cada uno ≥73 líneas con contenido sustantivo (DoD plan §5.2: ≥20). |
| 3 | 2026-06-12 | S3 | Fase 0 / Tarea 0.C — Mover/eliminar outputs y scripts espurios | 19 `liquidacion*.{json,pdf,txt}` → `output/_legacy/`. `compensacion_pedro_franco.json`, `finca_rural_result.json` → `output/_legacy/`. `finca_rural.json` → `examples/inputs/`. `generate_liquidacion.py` (+ cabecera DEPRECATED), `generar_varios.py` → `scripts/_legacy/`. `test_encabezado.py` → `tests/_legacy/`. `Plan de ejecución.py` → `Planificación/_legacy/Plan de ejecución.md`. Raíz sin `.json`/`.pdf` sueltos. | Parcial — movimientos ✓; 6 eliminaciones pospuestas por usuario: `__pycache__/`, `htmlcov/`, `.coverage`, 2 `egg-info/`, `documentos_legales_rurales/`. |
| 2 | 2026-06-12 | S2 | Fase 0 / Tarea 0.B — .gitignore exhaustivo | `.gitignore` creado en raíz (~7.5 KB, ~95 líneas). Patrones del plan §5.2 incluidos textualmente; 12 adiciones propias marcadas con `# [ADD]` o `# [FIX]`. Cubre: entornos (.venv, liquidacion-env), empaquetado (*.egg-info), bytecode (__pycache__, *.pyc, *.pyo), cachés (.mypy_cache, .pytest_cache, .ruff_cache), cobertura (.coverage, htmlcov), salidas (output/, artifacts/, logs/, audit/), datos (data/, *.sqlite, *.db), artefactos históricos (liquidacion*.{json,pdf,txt}, finca_rural*.json, compensacion_*.json), secretos (.env, .env.local, .env.*.local, .env.backup*, *.pem, *.key), scripts espurios (/generate_liquidacion.py, /generar_varios.py, /test_encabezado.py, /Plan de ejecución.py), backups genéricos (*.bak, *.backup, *.tmp, *.swp, *~), logs genéricos (*.log), editores (.vscode/, .idea/, *.iml, .DS_Store, Thumbs.db), legacy (/documentos_legales_rurales/). `.env.example` y archivos fuente (README, CHANGELOG, LICENSE, liquidator/, params/, Contexto/, Planificación/, config/, examples/, legal_docs/, docs/, bin/) NO ignorados. | Parcial — archivo creado ✓; validación automatizada bloqueada por sistema post-seguridad. |
| 1 | 2026-06-12 | S1 | Fase 0 / Tarea 0.A — rotación de clave de cifrado | Clave anterior SHA256 `de1b22...8868` INVALIDADA. Nueva clave 64-char hex en `.env` (SHA256 nueva: `194bf30d...ee786` — validar contra este hash en futuras sesiones). Backup en `.env.backup_pre_rotation_2026-06-12` (permiso 777 por FS Windows, no POSIX). `.env.example` creado con placeholders. `grep` de clave vieja en `.env` retorna 0. | Parcial — acción de rotación ✓; documentación de compromiso diferida a Tarea 0.E (KB_LLM/06_riesgos_modelo.md). |
| 0 | 2026-06-12 | S0 | Meta-tarea de tracking (crear REGISTRY.md) | `Planificación/REGISTRY.md` creado (106 líneas, 7.091 bytes). Estado real de Fase 0 validado contra disco (8 checks de Fase 0 DoD ejecutados; todos en ✗). Plan + 2 addenda revisados para poblar tabla de fases y decisiones de addenda. | N/A (no es tarea de fase) |

---

## Handoff — si abrís esto en una sesión nueva

> Esta sección existe para que un agente (o vos) pueda retomar **sin
> re-leer las 3.353 líneas del plan**. Verificá los 6 checks, leé el
> orden sugerido, y arrancá la próxima tarea.

### Verificación rápida de estado (6 checks, ~10 segundos)

```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli

# 1. KB existe con 10 archivos
n=$(ls Contexto/KB_LLM/ 2>/dev/null | wc -l); echo "[KB] $n archivos (esperado 10)"

# 2. Prompts ausentes (cerrado en S6 — Tarea 0.F)
test -d Contexto/prompts && echo "[prompts] OK" || echo "[prompts] PENDIENTE 0.F"

# 3. AGENTS.md presente (creado en S7 — Tarea 0.G)
test -f AGENTS.md && echo "[AGENTS] OK (creado en S7 — Tarea 0.G)" || echo "[AGENTS] PENDIENTE 0.G ⚠"

# 4. check_kb_freshness.py existe Y corre con exit 0 (cerrado en S8 — Tarea 0.H)
test -f scripts/check_kb_freshness.py && \
  test -f liquidator/tests/test_kb_freshness.py && \
  python3 scripts/check_kb_freshness.py >/dev/null 2>&1 && \
  echo "[KB-fresh] OK (creado en S8 — Tarea 0.H)" || \
  echo "[KB-fresh] PENDIENTE 0.H"

# 5. .git inicializado (cerrado en S9 — Tarea 0.I)
test -d .git && echo "[git] OK (cerrado en S9 — Tarea 0.I)" || echo "[git] PENDIENTE 0.I"

# 6. KB y código sin Art. 155 en contexto de prescripción (R-LEG-02).
#    Búsqueda focalizada: solo lo operacional (NO Planificación/, donde
#    los reparos y decisiones LEGÍTIMAMENTE mencionan "no usar Art. 155").
matches=$(grep -rn "Art\. 155" liquidator/ params/ Contexto/KB_LLM/ legal_docs/ 2>/dev/null)
if [ -z "$matches" ]; then
    echo "[Art.155] OK: cero referencias operacionales"
else
    echo "[Art.155] REVISAR (matches operacionales):"
    echo "$matches"
    echo "→ Si es cita legal vigente, reemplazar por Art. 488 CST."
    echo "→ ESPERADO en Contexto/KB_LLM/06_riesgos_modelo.md (documenta R-LEG-02)."
    echo "  Los matches allí son la descripción del riesgo, no uso. OK ignorar."
    echo "→ INESPERADO en liquidator/, params/, legal_docs/, otras notas KB."
    echo "  Esos SÍ son uso operacional: evaluar y reemplazar por Art. 488 CST."
fi
```

Si algún check falla distinto a lo esperado, **no avanzar**: actualizar
REGISTRY primero.

### Orden de lectura sugerido (1-2 minutos)

1. **"Estado actual"** (arriba) → qué tarea viene.
2. **Esta sección "Handoff"** → trampas y orden de tareas restantes.
3. **"Tabla de fases"** → cómo encaja en el roadmap.
4. **"Decisiones de addendas"** → qué reparos bloquean.
5. **"Log de cierres"** → última fila S8 (esta) para entender qué se hizo.
6. **KB nota relevante** (si la tarea es de cálculo/legal → 01-03; si es
   de input/output → 04-05; si es de riesgos → 06; si es operativo → 07).
7. **Plan §X.Y** de la tarea (líneas exactas abajo en la tabla).

### Tareas restantes de Fase 0 (en orden de ejecución)

| # | Tarea              | Output esperado                                                                 | Plan ref                               | Bloquea a        | Notas                                                                                                                                |
|----|--------------------|---------------------------------------------------------------------------------|----------------------------------------|------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| 0.J | suite 100%         | `pytest liquidator/tests` verde o fallos documentados                            | §5.2 T0.J, líneas 613-631              | Fase 1           | Cada fallo preexistente → entrada en `06_riesgos_modelo.md` con issue → Fase 1. Pendiente: ejecutar `pytest` en Windows venv (WSL sin pytest). |
| 0.K | params 2026 activos| Renombrar `KB_LLM/02_parametros_vigentes.md` con tabla comparativa              | §5.2 T0.K, líneas 499-591              | v2.0 release     | El cambio REAL del motor (ParamsProvider year-aware) es Tarea 1.E de Fase 1; 0.K solo deja KB y params listos.                       |

> **Convención "1 fase por sesión" del usuario:** cada sesión cierra UNA
> tarea como máximo. La Fase 0 va a requerir ≥1 sesión más (0.J + 0.K en
> una). El cierre formal de Fase 0 es cuando se completan 0.A-0.K.

> **Tarea 0.I cerrada en S9 (commit `f04d639`).** Orden estricto cumplido:
> 0.A (clave rotada) → 0.B (.gitignore presente) → ... → 0.I (git init).

### Trampas conocidas (no violar)

- **No cerrar sesión sin los 5 pasos del cierre** (ver bloque inferior).
- **No generar PDF si compliance = `NO_GO`** (será regla AGENTS.md #7).
- **No disfrazar `.txt` como PDF** (será regla AGENTS.md #8).
- **No hardcodear SMMLV, aux_trans, tasas, plazos** (será regla #4).
- **No usar outputs como expected values** sin firma del usuario
  (`output/_legacy/` NO es contrato; es histórico).
- **Prescripción de prestaciones = Art. 488 CST**, NO Art. 155
  (R-LEG-02, R-LEG-03). Cualquier referencia a Art. 155 en ese contexto
  es bug.
- **SL2630-2024** citada como `PENDIENTE` en KB hasta verificación
  verbatim de URL/sala/texto (Fase 2-bis).
- **Art. 189 párr. 1° CST** (compensación obligatoria en finiquito) NO
  verificado en SUIN; bloqueante para 2.B-ter.
- **Indemnización Art. 64 CST** NO implementada en v2.0 (R-LEG-01);
  output debe traer `indemnizacion: null`.
- **No hacer `git init` antes de 0.A** (clave de cifrado rotada en S1).
- **No hacer primer `git add` antes de 0.B** (.gitignore).
- **Eliminaciones pospuestas** (decisión S3): `__pycache__/`, `htmlcov/`,
  `.coverage`, 2 `*.egg-info/`, `documentos_legales_rurales/`. NO borrar
  sin que el usuario lo pida de nuevo.

### Estado del caso canónico (KB_LLM/09)

- **Documentado:** sí (S5, 2026-06-13).
- **Ejecutado end-to-end:** NO. Motor no estabilizado (Fase 0).
- **Trazabilidad:** cada vez que se ejecute (primera vez en Fase 1 Tarea
  1.B), actualizar `KB_LLM/09` con valores observados y referenciar el
  golden file en `examples/expected/`.
- **Cuándo es bloqueante:** el caso canónico DEBE poder ejecutarse
  antes de cerrar cualquier fase. Si falla, es bug del motor → Fase
  anterior, no se cierra la fase objetivo.

### Regla de cierre (recordatorio, ya en bloque arriba)

Al cerrar la sesión, en este orden:
1. Validar DoD contra código vivo.
2. Actualizar este REGISTRY (estado, fase, log, próxima).
3. Si cerraste fase → entrada en `CHANGELOG.md` bajo `[Unreleased]`.
4. Si tocaste `params/` o reglas → sincronizar `KB_LLM/02` o `03`.
5. Si tocaste un addenda → verificar que la decisión aprobada no haya
   cambiado; si cambió, documentar en el addenda y re-evaluar.

**No cerrar sesión sin completar los 5 puntos.**

---

## Cómo se lee este archivo

- **Abrir sesión nueva** → leer **primero "Handoff"** (verificación 5
  checks + trampas + tareas restantes), después "Estado actual" (4
  líneas).
- **Decidir qué viene** → leer "Tabla de fases" (1 pantalla) + "Handoff /
  Tareas restantes".
- **Entender contexto histórico** → leer "Log de cierres" (scroll abajo).
- **Recordar por qué un addenda se decidió así** → leer "Decisiones de
  addendas".

---

## Referencias

- **Plan fuente:** `Planificación/plan_modernizacion_v2.0_2026-06-09.md` (3.353 líneas — consultar solo para detalle)
- **Diagnóstico fuente:** `Contexto/diagnostico_liquidacion_cli_2026-06-09.md`
- **Addenda:**
  - `Planificación/addendum_sl2630_y_ipc_2026-06-09.md`
  - `Planificación/addendum_finiquito_renuncia_vacaciones_2026-06-11.md`
- **Estado de Fase 0 validado contra disco:** 2026-06-13 (sesión S9 — Tarea 0.I cerrada, `git init` + commit `f04d639` con 200 archivos, 43.477 insertions, working tree clean except 3 untracked intencionales; 0.A-0.I ✓, pendientes 0.J y 0.K). Verificación rápida de 6 checks en sección "Handoff".
