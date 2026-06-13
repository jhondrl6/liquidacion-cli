# Plan de modernización a v2.0 — liquidacion_cli

|> **Para Hermes/operador:** Este plan es ejecutable fase por fase. **Una fase por sesión** (convención del usuario). Antes de cualquier cambio, reproducir el caso canónico como prueba de cordura (§5).
>
> **Diagnóstico fuente:** `Contexto/diagnostico_liquidacion_cli_2026-06-09.md` (1329 líneas, auditado contra código vivo el 2026-06-09). Toda afirmación de este plan se considera vigente salvo verificación que la contradiga.
>
> **Regla operativa dura (§5.5.11 del diagnóstico):** Antes de aceptar como verdad cualquier afirmación de este plan o del diagnóstico, **verificar contra código vivo**. Si código y plan/diagnóstico discrepan, código gana; el plan se actualiza.
>
> **Addendum SL2630-2024 + IPC absorbido en v2.0.0 (2026-06-09):** Por decisión del 2026-06-09, las 3 tareas del `addendum_sl2630_y_ipc_2026-06-09.md` se incorporan a v2.0.0 como **corrección de alcance antes del release** (no como v2.0.1). Distribución:
> - **Tarea 1.C-bis** (extender schema `Salario` con `sbl_por_anio` y `historial_salarial`) → **Fase 1** (anexada como Tarea 1.C-bis en §6.2).
> - **Tarea 2.B-bis** (`SalarioResolver` con SBL del año del segmento) → **Fase 2** (anexada como Tarea 2.B-bis en §7.2).
> - **Tarea 2.X** (indexación IPC para prestaciones no pagadas + normas SL2630-2024 y Art. 488 CST) → **nueva Fase 2-bis** (§7-bis).
>
> **Addendum finiquito por renuncia + vacaciones compensadas absorbido en v2.0.0 (2026-06-11):** Por decisión del 2026-06-11, las 4 tareas del `addendum_finiquito_renuncia_vacaciones_2026-06-11.md` (APROBADO CON REPAROS) se incorporan a v2.0.0 como **corrección de alcance antes del release** (mismo tratamiento que el addendum SL2630-2024 + IPC). Distribución:
> - **Tarea 1.C-ter** (extender `Contrato` con `motivo_terminacion` y `VacacionesEstado` tipado) → **Fase 1** (anexada como Tarea 1.C-ter en §6.2).
> - **Tarea 2.B-ter** (`calculate_vacaciones_compensadas_finiquito` en `PrestacionesCalculator`, fórmula Art. 189-190 CST) → **Fase 2** (anexada como Tarea 2.B-ter en §7.2).
> - **Tarea 2.Z** (reglas de compliance `V_VACACIONES_FINIQUITO` CRITICAL y `V_VACACIONES_DECLARADAS_FINIQUITO` MEDIUM) → **Fase 2** (anexada como Tarea 2.Z en §7.2).
> - **Tarea 3.G** (`PreRenderValidator` específico por motivo + plantilla `finiquito_renuncia.j2` con nota de no-indemnización) → **Fase 3** (anexada como Tarea 3.G en §8.2).
>
> **Reparos bloqueantes del addendum finiquito/vacaciones (a cerrar antes de marcar las tareas como DoD):** (a) **Verificar texto literal del Art. 189 CST en SUIN** (https://www.suin-juriscol.gov.co/) antes de cerrar Tarea 2.B-ter — específicamente el párr. 1° sobre compensación obligatoria de vacaciones no disfrutadas al terminar el contrato; (b) **confirmar que el motor distingue explícitamente** entre *vacaciones compensadas por acuerdo mutuo* (Art. 189, periodo vigente) y *vacaciones obligatoriamente compensadas en finiquito* (Art. 189 párr. 1° + Art. 190, terminación del contrato) — el modo `FINIQUITO` debe invocar `calculate_vacaciones_compensadas_finiquito` y el modo `PERIODICA` no debe pagarlas por error; (c) **Indemnización Art. 64 CST NO se implementa en esta iteración** (queda referenciada y documentada en el addendum para casos futuros de despido sin justa causa, pero no es código de v2.0). **Convención:** 1 fase por sesión (respetar convención del usuario). **Regresión dura:** el caso canónico PERIODICA (SBL 2.200.000, 206d, dos segmentos) **sigue verde** — los nuevos campos de `Contrato` y `LiquidacionInput` son retrocompatibles (opcionales o con default seguro).
>
> **Reparos bloqueantes del addendum (a cerrar antes de marcar Fase 2-bis como DoD):** (a) **NO usar Art. 155 CST** como sustento de prescripción — usar **Art. 488 CST**; (b) verificar **texto literal, sala y URL oficial** de SL2630-2024 antes de tratar su `texto_relevante` como cita verificada (estado inicial: `PENDIENTE_VERBATIM`); (c) modelar IPC como **índices acumulados**, no como tasas anuales de inflación. **Convención:** 1 fase por sesión (respetar convención del usuario).

---

## 1. Goal

Llevar `liquidacion_cli` de prototipo con deuda técnica a **herramienta CLI local v2.0 confiable** que:

1. Liquide correctamente el caso canónico (16-Nov-2025 a 9-Jun-2026 (as-of 2026-06-09; fecha de terminación real TBD), 206 días en dos segmentos, SBL=2.200.000 → cesantías TBD-motor-Fase2 (ver §3, segmento 2025 + segmento 2026)).
2. Genere los 3 artefactos (JSON + Markdown + PDF) trazables a parámetros, normas y reglas.
3. Bloquee o advierta explícitamente ante errores legales (CRITICAL/HIGH) y permita override auditado.
4. Pase el **100% de la suite de tests** como criterio de cierre de fase.
5. Mantenga un **segundo cerebro local** (KB versionada en Markdown) que documente la fuente de verdad y permita operar el sistema sin depender de documentación desactualizada.

**Out of scope (validado, ver diagnóstico §6):**
- API, servicio web, validación por terceros.
- LLM comercial en la nube (cualquier LLM usado debe ser local: ollama, llama.cpp, vLLM, LM Studio, Jan).
- Retro-compatibilidad con v1.x (v2.0 permite breaking changes).

---

## 2. Architecture (decisiones adoptadas, inamovibles salvo revocación explícita)

| Aspecto | Decisión | Fuente |
|---|---|---|
| Tipo de producto | CLI local, usuario único (Jhond) | Diag. §6.1 |
| Infraestructura | 100% local, sin API externa | Diag. §6.3 |
| Versión objetivo | v2.0 (semver, breaking changes permitidos) | Diag. §6.5 |
| Compliance | `severity` → `blocking` (CRITICAL/HIGH bloquean, MEDIUM/LOW/INFO solo registra) | Diag. §3.7, §6.4 |
| DoD universal | 100% de tests pasando al cerrar cada fase (0 errores de colección, 0 fallos) | Diag. §6.6 |
| Caso canónico | Reproducible desde CLI en cada fase; si falla, la fase no está cerrada | Diag. §6.2 |
| Stack | Python 3.12, Pydantic para input/output, Jinja2 para plantillas, Click o Typer para CLI, WeasyPrint para PDF, pytest + ruff como gates de CI | Implícito del estado actual + diag. §3.3, §3.4 |

### 2.1 Estructura objetivo del proyecto (referencia)

```
liquidacion_cli/
├── AGENTS.md                          # Jerarquía de verdad + reglas para agentes
├── README.md                          # Contrato real v2.0 (no v1.0.0)
├── CHANGELOG.md                       # Entrada v2.0 con breaking changes
├── pyproject.toml                     # Empaquetado moderno
├── setup.py                           # Mantenido por compatibilidad temporal
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── .env.example                       # Placeholders, sin secretos
├── .gitignore                         # Outputs, caches, venvs, .env
├── bin/liquidar                       # Wrapper CLI
├── liquidator/
│   ├── __init__.py
│   ├── cli/                           # Entry point real
│   │   └── main.py
│   ├── core/                          # Motor
│   │   ├── engine.py
│   │   ├── input_parser.py
│   │   └── params_provider.py         # Acceso centralizado a parámetros
│   ├── calculators/                   # Cálculos legales
│   │   ├── prestaciones.py
│   │   ├── indemnizacion.py
│   │   ├── sbl.py
│   │   └── ...
│   ├── validators/                    # Validación de entrada (unificada)
│   │   └── input_validator.py
│   ├── legal/                         # Normas, plazos, topes, recargos
│   ├── compliance/                    # Motor de compliance
│   ├── output/                        # Generadores JSON/MD/PDF
│   │   ├── json_generator.py
│   │   ├── markdown_generator.py
│   │   └── pdf_generator.py
│   ├── audit/                         # Trazabilidad
│   ├── params/                        # Versionamiento y validación de params
│   ├── security/                      # Sanitización
│   ├── tests/                         # 100% pasando
│   └── templates/                     # Plantillas Jinja (movidas aquí)
├── params/
│   ├── 2025.json
│   ├── normas.json
│   ├── plazos.json
│   └── checklist.json                 # Con campo blocking por regla
├── config/
├── templates/                         # Compatibilidad transitoria
├── examples/
│   ├── inputs/                        # JSON de entrada
│   └── expected/                      # Salidas esperadas (golden)
├── docs/                              # Generadas, no fuente de verdad
├── Contexto/
│   ├── diagnostico_liquidacion_cli_2026-06-09.md
│   ├── KB_LLM/                        # Segundo cerebro (10 notas)
│   └── prompts/                       # Prompts base para agentes
├── scripts/                           # Utilidades operativas
├── output/                            # Artefactos generados (gitignored)
├── artifacts/                         # Auditoría inmutable (gitignored)
├── logs/                              # Logs (gitignored)
└── audit/                             # Auditoría histórica (gitignored excepto .gitkeep)
```

---

## 3. Caso canónico (ancla de validación continua)

**Sin excepción, este caso debe poder ejecutarse y verificarse en cada fase cerrada.**

> **Versión vigente al 2026-06-09:** una sola liquidación en modo PERIODICA con dos segmentos de cálculo (el año calendario cierra un segmento a 2025-12-31 y abre otro a 2026-01-01). La fecha de terminación real del contrato está **pendiente de confirmar**; el caso canónico usa la fecha de corte **as-of 2026-06-09** (hoy) como tope provisional. Cuando el contrato termine, este caso se cierra con la fecha de terminación real y se regeneran los golden files. El SBL se mantiene en 2.200.000 para ambos años (constante del contrato, no afectada por cambios de SMMLV).

```json
{
  "trabajador": {"nombre": "[ANONIMIZADO]", "documento": "[ANONIMIZADO]"},
  "empleador":  {"nombre": "[ANONIMIZADO]", "documento": "[ANONIMIZADO]"},
  "contrato":   {"fecha_ingreso": "2025-11-16", "fecha_corte": "2026-06-09", "tipo": "INDEFINIDO", "fecha_terminacion_real": null},
  "salario":    {"SBL": 2200000, "auxilio_transporte": false, "variable": false},
  "modo":       "PERIODICA",
  "segmentos": [
    {"anio": 2025, "desde": "2025-11-16", "hasta": "2025-12-31", "params_ref": "params/2025.json"},
    {"anio": 2026, "desde": "2026-01-01", "hasta": "2026-06-09", "params_ref": "params/2026.json"}
  ]
}
```

| Segmento | Rango | Días (incl.) | Params que aplica | Normas |
|---|---|---|---|---|
| 2025-H2 (cerrado) | 2025-11-16 → 2025-12-31 | 46 | `params/2025.json` (Decreto 1572/2024 SMMLV 1.423.500; Decreto 1573/2024 aux_trans 200.000) | Ley 50/1990, CST 249-308 |
| 2026-H1 (en curso) | 2026-01-01 → 2026-06-09 | 160 | `params/2026.json` (Decreto 1469/2025 SMMLV 1.750.905 — **SUSPENDIDO provisionalmente, ver D. 159/2026**; Decreto 1470/2025 aux_trans 249.095) | Ley 50/1990, CST 249-308, Ley 2466/2025 (recargo dominical gradual) |
| **Total** | 2025-11-16 → 2026-06-09 | **206** | (convención día-a-día inclusiva; alternativamente 205 con fin exclusivo, a fijar en Fase 1 con el motor) | |

| Concepto | Valor esperado | Cálculo |
|---|---|---|
| Cesantías 2025 | TBD por motor | 2.200.000 × 46 / 360 (usando `params/2025.json`) |
| Cesantías 2026 | TBD por motor | 2.200.000 × 160 / 360 (usando `params/2026.json`) |
| Prima H2 2025 | proporcional a 46 días | ver cálculo interno |
| Prima H1 2026 | proporcional a 160 días | ver cálculo interno |
| Intereses sobre cesantías | proporcional (12% anual) | ver cálculo interno (la opción 1% mensual del Art. 64 Ley 2466/2025 solo aplica si hay acuerdo escrito) |
| Recargo dominical | 80% en todo el rango (cambia a 90% el 2026-07-01) | Ley 2466/2025 cronograma gradual |
| Estado compliance esperado | GO (con WARN aceptable mientras no haya regla CRITICAL violada) | — |

**Archivos golden esperados (a crear en Fase 1+):** `examples/expected/caso_canonico_periodico_206d_result.json` (y `.md`, `.pdf`). El `params_version` debe registrar TANTO `2025-10-31` (segmento 2025) como `2026-06-09` (segmento 2026) en `meta.parametros_por_segmento` para auditoría. La segmentación debe verse en `desglose` con sub-objetos por año para que sea auditable per-year. **Mismo formato de salida** que `liquidacion_pedro_franco.json` (shape `meta / trabajador / parametros / desglose / total_liquidacion / validaciones_y_alertas / normas_aplicadas / compliance_report`).

**Vacaciones pendientes heredadas (referencia, no parte del caso canónico):** El caso real `liquidacion_pedro_franco.json` (modo PERIODICA, 2024-11-16 → 2025-11-15) tiene 7.5 días de vacaciones compensadas por acuerdo mutuo (Art. 189 CST). Si el contrato de Pedro Franco sigue vigente, esos 7.5 días se arrastran al finiquito definitivo. NO se incluyen en este caso canónico (es de otro contrato anonimizado).

---

## 4. Roadmap de fases (resumen)

| Fase | Título | Foco | DoD | Esfuerzo |
|---|---|---|---|---|
| **0** | Higiene + segundo cerebro mínimo | Repo limpio, sintaxis válida, KB esbozada, `.git` inicializado tras rotar clave | `compileall`=0, `git status` limpio, 9 notas KB + AGENTS.md creados, suite al 100% o fallos preexistentes documentados | Bajo-Medio |
| **1** | Estabilizar y formalizar | `pyproject.toml`, CLI real, schemas Pydantic, generadores consistentes, caso canónico verde | `pip install -e .` OK, `python -m liquidator.cli --help` OK, caso canónico verde, suite 100% | Medio |
| **2** | Contrato legal y cálculo correcto | Cap de cesantías resuelto con cita legal, `severity→blocking` activo, `OVERRIDE_APPROVED` implementado, `NormasRepository`/`PlazosManager` integrados, tests golden | Caso canónico exacto, todos los golden tests verdes, suite 100% | Alto |
| **2-bis** | Indexación IPC + anualización salarial *(absorción addendum SL2630-2024)* | `IPCIndexador` con datos DANE en **formato índice acumulado**, `params/normas.json` con SL2630-2024 y Art. 488 CST (NO Art. 155), regla `V_INDEXACION_IPC` (severity MEDIUM, no bloqueante), test golden de prescripción/indexación verde, KB actualizada | `IPCIndexador.indexar()` retorna VA coherente con datos DANE reales; SL2630-2024 citada con `estado_verificacion` real (no `PENDIENTE_VERBATIM`); Art. 488 CST citado para prescripción; cero referencias a Art. 155 CST en código/params/KB; suite 100% | Alto (3-4 sesiones) |
| **3** | Documento generable robusto | `document_context` formal, plantillas Jinja, estados GO/WARN/NO_GO/OVERRIDE_APPROVED, evidencia legal por renglón, validación pre-render, `liquidacion_BLOQUEADA.*`, auditoría inmutable por ejecución | Caso canónico genera 3 archivos correctos; caso bloqueado genera `*_BLOQUEADA.*` con explicación; suite 100% | Alto |
| **4** | v2.0 release | Pydantic total, ruff+black+mypy en CI, CLI con Typer/Click, PDF robusto, CHANGELOG v2.0, README reescrito, `liquidacion --version`=2.0.0 | `liquidacion --version`=2.0.0, CHANGELOG con breaking changes, CI verde, suite 100%, **3 liquidaciones reales verificadas por Jhond** (diag. §6.8) | Medio |
| **5** | Investigación de casos reales *(opcional)* | Solo si surgen casos en Fases 0-4 | Al menos 1 caso real anexado con fuente citada y golden test derivado verde | Condicional |

**Convención:** El usuario trabaja **una fase por sesión**. Al cerrar una fase, se actualizan registros (ver §10).

---

## 5. Fase 0 — Higiene del repositorio y segundo cerebro mínimo

> **Objetivo:** Dejar el repo en estado mínimo seguro, versionado, y con KB_LLM esbozada para que cualquier sesión futura pueda operar sin perder contexto.

### 5.1 DoD Fase 0 (criterio de cierre binario)

- [ ] `git init` exitoso en `/mnt/c/Users/Jhond/Github/liquidacion_cli`.
- [ ] `git status` limpio tras commit inicial.
- [ ] `python3 -m compileall liquidator` retorna 0 (los 5 archivos con `SyntaxError` corregidos).
- [ ] Los 13 errores de colección de tests (baseline §2.4 del diagnóstico) reducidos a 0 o, si quedan por imports en lógica de negocio, **documentados y trasladados a Fase 1**.
- [ ] `Contexto/KB_LLM/` con 9 notas + `Contexto/prompts/` con 3 prompts.
- [ ] `AGENTS.md` creado en la raíz.
- [ ] `output/`, `artifacts/`, `logs/` creados con `.gitkeep`.
- [ ] Outputs generados movidos fuera de la raíz (a `output/` o eliminados).
- [ ] Scripts espurios (`generate_liquidacion.py`, `generar_varios.py`, `test_encabezado.py`) reubicados a `scripts/_legacy/` o eliminados.
- [ ] `scripts/check_kb_freshness.py` creado.
- [ ] `tests/test_kb_freshness.py` creado y verde.
- [ ] Suite al 100% o fallos preexistentes **explícitamente documentados y agendados** en Fase 1.
- [ ] Caso canónico de cordura ejecutado (o documentado por qué no aplica todavía si requiere Fase 1).

### 5.2 Tareas Fase 0 (orden de ejecución)

#### Tarea 0.A — Rotación de clave de cifrado (SEGURIDAD, hacer antes de `git init`)

**Archivos:** `.env` (lectura), `.env.example` (crear), `config/` (verificar uso de clave)

1. **Inspeccionar `.env`** y anotar el valor actual de `LIQUIDACION_ENCRYPTION_KEY` (no exponer en logs).
2. **Generar nueva clave** (32 bytes hexadecimales):
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```
3. **Reemplazar** la clave en `.env` con la nueva.
4. **Asumir compromiso** de la clave anterior (cualquier dato cifrado con la clave vieja debe re-cifrarse si se reutiliza; para Fase 0 basta documentar en `Contexto/KB_LLM/06_riesgos_modelo.md`).
5. **Crear `.env.example`** en la raíz con valores placeholder (sin secretos reales):
   ```ini
   LIQUIDACION_ENV=development
   LIQUIDACION_ENCRYPTION_KEY=<GENERAR_CON: python -c "import secrets; print(secrets.token_hex(32))">
   LIQUIDACION_CONFIG_PATH=./config
   LIQUIDACION_DATA_PATH=./data
   ```

**Validación:** `grep -r "5ca2e4b56c6e977d5c685796599c2673d7856e7354553064971b790692e04498" .` debe retornar 0 matches fuera de backups deliberados.

---

#### Tarea 0.B — `.gitignore` exhaustivo

**Archivo:** crear `.gitignore` en la raíz.

Contenido mínimo (consolidar diag. §3.14 + §3.2):

```gitignore
# Entornos
.venv/
liquidacion-env/
env/
*.egg-info/
__pycache__/
*.pyc
*.pyo
.mypy_cache/
.pytest_cache/

# Cobertura
.coverage
htmlcov/

# Salidas generadas
output/
artifacts/
logs/
audit/logs/
!audit/logs/.gitkeep

# Artefactos históricos (mover fuera de la raíz o ignorar)
liquidacion*.json
liquidacion*.pdf
liquidacion*.txt
finca_rural*.json
compensacion_*.json
*.egg-info/

# Secretos y entorno
.env
.env.local

# Scripts espurios de un solo uso
/generate_liquidacion.py
/generar_varios.py
/test_encabezado.py
```

**Validación:** `git status` (cuando se haga `git init`) debe mostrar solo archivos fuente, configs y docs versionables.

---

#### Tarea 0.C — Mover/eliminar outputs y scripts espurios

**Archivos/dirs afectados (raíz):**

| Origen | Destino |
|---|---|
| `compensacion_pedro_franco.json` | `output/_legacy/` o eliminar |
| `finca_rural.json`, `finca_rural_result.json` | `examples/inputs/` (si son entrada útil) y `output/_legacy/` (si es salida) |
| `liquidacion*.{json,pdf,txt}` (todos) | `output/_legacy/` o eliminar |
| `generate_liquidacion.py` | `scripts/_legacy/` con cabecera `# DEPRECATED: usar python -m liquidator.cli` |
| `generar_varios.py` | `scripts/_legacy/` o eliminar |
| `test_encabezado.py` | `tests/_legacy/` o eliminar |
| `Plan de ejecución.py` | revisar; si es plan, mover a `Plan/` con extensión `.md`; si es script, eliminar |
| `htmlcov/` | `.gitignore` ya lo cubre; eliminar del tree |
| `.coverage` | `.gitignore` ya lo cubre |
| `documentos_legales_rurales/` | revisar; si son PDFs de referencia, mover a `legal_docs/`; si son outputs, eliminar |
| `colombia_payroll_settlement.egg-info/`, `liquidacion_nomina_colombia.egg-info/` | eliminar (`.gitignore` ya los cubre) |

**Validación:** Raíz del proyecto limpia, sin `.json`/`.pdf` sueltos excepto `README.md`, `CHANGELOG.md`, `LICENSE`, `DISCLAIMER.md`, `QWEN.md`, configs.

---

#### Tarea 0.D — Corregir los 5 archivos con `SyntaxError`

**Archivos (del diag. §2.3):**

1. `liquidator/output/markdown_generator.py` L7 — cambiar `from datetime` por `from datetime import datetime, date` (u otro uso real).
2. `liquidator/params/params_versioning.py` L6 — mismo patrón.
3. `liquidator/tests/test_audit/test_trail_generator.py` L9 — mismo patrón.
4. `liquidator/tests/test_calculators/test_indemnizacion.py` L8 — `from datetime , timedelta` → `from datetime import datetime, timedelta`.
5. `liquidator/tests/test_compliance/test_override.py` L6 — mismo patrón.

**Validación inmediata:**
```bash
python3 -m compileall -q liquidator
# Esperado: exit code 0, sin salida
```

**Validación extendida:**
```bash
PYTHONPATH=/mnt/c/Users/Jhond/Github/liquidacion_cli \
uv run --with pytest --with python-dateutil --with PyYAML --with jsonschema \
--with pydantic --with loguru --with click --with markdown --with Jinja2 \
pytest liquidator/tests --collect-only -q
# Esperado: 173 tests collected, 0 errors
```

Si tras corregir los 5 archivos aún hay errores de colección, documentar cada uno en `Contexto/KB_LLM/06_riesgos_modelo.md` como "issue preexistente → Fase 1".

---

#### Tarea 0.E — Crear `Contexto/KB_LLM/` con 9 notas

**Directorio:** `Contexto/KB_LLM/`

Crear 9 archivos (uno por nota):

| Archivo | Contenido mínimo | Fuente |
|---|---|---|
| `00_fuente_de_verdad.md` | Jerarquía explícita: código > params > tests > legal_docs > diagnósticos > docs. Regla "si contradice, gana código". | Diag. §5.1, §5.5.11 |
| `01_reglas_calculo.md` | Lista de conceptos liquidados (cesantías, prima, intereses, vacaciones, indemnización), fórmula legal esperada para cada uno, cita CST/decreto/ley cuando esté disponible. | Diag. §3.6, `legal_docs/` |
| `02_parametros_vigentes.md` | SMMLV, auxilio transporte, límites, tasas de TODOS los años vigentes. **Citar fuente (`params/<año>.json`) y fecha de vigencia de cada año.** Prohibido hardcodear. Estructura: tabla comparativa por año + regla de selección por `fecha_corte`. Tras Tarea 0.K este archivo reemplaza al legado `02_parametros_2025.md`. | Diag. §3.8, §3.11 |
| `03_compliance_blocking.md` | Tabla `severity → blocking` (CRITICAL/HIGH bloquean, MEDIUM/LOW/INFO no). Mecánica de `OVERRIDE_APPROVED`. | Diag. §3.7, §6.4 |
| `04_schema_entrada.md` | Contrato de entrada (campos: trabajador, empleador, contrato, salario, modo, auxilios, vacaciones, motivo_terminación). Referencia al schema formal a crear en Fase 1. | Diag. §3.5 |
| `05_schema_salida.md` | Contrato de salida (`liquidacion_result.json`): metadatos, desglose por concepto con evidencia legal, compliance, auditoría. Referencia al schema formal a crear en Fase 1. | Diag. §3.8, §3.15 |
| `06_riesgos_modelo.md` | Lista de riesgos validados: docs desactualizados, fine-tuning prematuro, MCP demasiado amplio, datos sensibles en KB, dependencia LLM externo, errores heredados del diagnóstico. | Diag. §5.10 |
| `07_checklist_generacion_liquidacion.md` | Checklist pre-cálculo (leer params, validar input) + checklist pre-generación (compliance verde, contexto completo, plantillas renderizan, auditoría registrada). | Diag. §5.6, §5.7 |
| `08_arquitectura_segundo_cerebro.md` | Capas (código, KB, memoria, skill, retrieval, validación), decisión de no usar fine-tuning, criterios de aceptación. | Diag. §5.4, §5.11 |
| `09_caso_canonico_usuario.md` | Caso canónico completo: input JSON (anonimizado), cálculos esperados (cesantías TBD-motor-Fase2 (ver §3, segmento 2025 + segmento 2026), prima por semestre, intereses 12% anual), cómo reproducirlo desde CLI. **Este archivo se actualiza en cada fase con la salida real observada para evidenciar progreso.** | Diag. §6.2 |

**Validación:** `ls Contexto/KB_LLM/` debe mostrar los 10 archivos (00-09). Cada uno ≥ 20 líneas con contenido sustantivo (no placeholders).

---

#### Tarea 0.F — Crear `Contexto/prompts/` con 3 prompts

**Directorio:** `Contexto/prompts/`

| Archivo | Contenido |
|---|---|
| `prompt_generacion_liquidacion.md` | Prompt base para agentes que generan liquidaciones: leer diag, KB, params, no hardcodear, no generar PDF si NO_GO. |
| `prompt_auditoria_antes_de_responder.md` | Prompt para agentes que responden sobre liquidacion_cli: verificar contra código, contrastar docs, declarar incertidumbre. |
| `prompt_plan_modernizacion.md` | Prompt para sesiones de planificación: revisar estado de fases, qué DoD falta, qué tareas siguen. |

**Validación:** `ls Contexto/prompts/` muestra los 3 archivos.

---

#### Tarea 0.G — Crear `AGENTS.md` en la raíz

**Archivo:** `AGENTS.md`

Contenido mínimo:

```markdown
# Reglas para agentes que operan en liquidacion_cli

## Jerarquía de verdad (en orden)
1. Código vivo en `liquidator/`, `params/`, `legal_docs/`, `tests/`.
2. Parámetros versionados (`params/<año>.json` para 2025 y 2026 vigentes, `params/normas.json`, `params/plazos.json`).
3. Tests reales y resultados de ejecución.
4. Diagnóstico `Contexto/diagnostico_liquidacion_cli_2026-06-09.md` (contrastado contra código).
5. KB local `Contexto/KB_LLM/`.
6. Documentación general `docs/`, `README.md` (última en la jerarquía).

## Reglas operativas inamovibles
1. Antes de calcular, leer `params/<año>.json` (todos los vigentes), `params/normas.json`, `params/plazos.json`.
2. Antes de confiar en una regla legal, buscar evidencia en `legal_docs/` o en el código.
3. Antes de aceptar documentación, contrastarla contra código, params y tests.
4. No hardcodear SMMLV, auxilio de transporte, límites salariales, tasas o plazos.
5. No usar outputs generados como fuente de verdad.
6. No incluir nombres, documentos de identidad, salarios reales o datos sensibles en la KB, logs o repo.
7. No generar PDF si el estado de compliance es `NO_GO`.
8. No disfrazar `.txt` como PDF.
9. Separar claramente estados `GO`, `WARN`, `NO_GO`, `OVERRIDE_APPROVED`.
10. Cada documento generado debe poder auditar qué params, normas y reglas usó.
11. **Antes de aceptar como verdad cualquier afirmación del diagnóstico 2026-06-09 o de la KB, verificar contra código vivo.**
12. Reproducir el caso canónico (206 días en dos segmentos: 2025-H2 46d + 2026-H1 160d, SBL=2.200.000, cesantías TBD-motor-Fase2 (ver §3, segmento 2025 + segmento 2026)) como primera prueba de cordura antes de cualquier cambio de fase.

## Caso canónico
Ver `Contexto/KB_LLM/09_caso_canonico_usuario.md`. Cesantías esperadas: TBD-motor-Fase2 (ver §3, segmento 2025 + segmento 2026).

## Cómo correr la suite
\`\`\`bash
PYTHONPATH=. uv run --with pytest --with python-dateutil --with PyYAML \\
  --with jsonschema --with pydantic --with loguru --with click \\
  --with markdown --with Jinja2 pytest liquidator/tests -q
\`\`\`
```

**Validación:** `AGENTS.md` existe, ≥ 30 líneas, contiene las 12 reglas y la jerarquía.

---

#### Tarea 0.H — `scripts/check_kb_freshness.py` y `tests/test_kb_freshness.py`

**Archivos:**
- Crear `scripts/check_kb_freshness.py`
- Crear `tests/test_kb_freshness.py` (en raíz o en `liquidator/tests/`)

**Propósito de `check_kb_freshness.py`:** Detectar si la KB quedó desactualizada respecto a:
- `params/<año>.json` para cada año presente en `params/` (campos clave: SMMLV, auxilio_trans, tasas). Versión inicial: 2025 y 2026 (a partir de Tarea 0.K; queda extensible a años futuros sin tocar este script).
- Tests rotos o pendientes.
- Diagnóstico: ¿hay hallazgos no cerrados en `Contexto/diagnostico_liquidacion_cli_2026-06-09.md`?

**Esqueleto sugerido** (a completar en Tarea 0.H; la lógica year-aware se materializa en 0.K con la creación de `2026.json`):

```python
#!/usr/bin/env python3
"""KB freshness check. Sale con código != 0 si encuentra desactualizaciones críticas."""
import json, sys, re
from pathlib import Path
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parents[1]
KB = REPO / "Contexto" / "KB_LLM"
PARAMS = REPO / "params"

def main() -> int:
    errors = []
    # 1. Para cada params/<año>.json presente, su SMMLV debe estar citado en la KB.
    #    La KB debe ser un único archivo "02_parametros_vigentes.md" (Tarea 0.E/0.K) que
    #    liste TODOS los años vigentes con sus SMMLV/aux_trans/etc. Acepta el nombre
    #    legado 02_parametros_2025.md para retro-compat.
    kb_02_candidates = [KB / "02_parametros_vigentes.md", KB / "02_parametros_2025.md"]
    kb_02_path = next((p for p in kb_02_candidates if p.exists()), None)
    if kb_02_path is None:
        errors.append("KB_LLM/02_parametros_vigentes.md (o 02_parametros_2025.md legado) no existe")
        kb_02_text = ""
    else:
        kb_02_text = kb_02_path.read_text()
    for params_file in sorted(PARAMS.glob("[0-9][0-9][0-9][0-9].json")):
        anio = params_file.stem
        data = json.loads(params_file.read_text())
        smmlv = data.get("SMMLV")
        if smmlv and str(smmlv) not in kb_02_text:
            errors.append(f"KB_LLM/{kb_02_path.name} no refleja SMMLV={smmlv} de {params_file.name}")
    # 2. Las 10 notas KB deben existir
    for i in range(10):
        nota = KB / f"{i:02d}_*.md"
        if not list(KB.glob(f"{i:02d}_*.md")):
            errors.append(f"Falta nota KB {i:02d}_*.md en Contexto/KB_LLM/")
    # 3. Diagnóstico referenciado en AGENTS.md
    agents = (REPO / "AGENTS.md").read_text()
    if "diagnostico_liquidacion_cli_2026-06-09.md" not in agents:
        errors.append("AGENTS.md no referencia el diagnóstico vigente")
    if errors:
        for e in errors: print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print("KB fresh.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

**Test mínimo en `tests/test_kb_freshness.py`:**

```python
import subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

def test_kb_freshness_exits_zero():
    r = subprocess.run([sys.executable, "scripts/check_kb_freshness.py"],
                       cwd=REPO, capture_output=True, text=True)
    assert r.returncode == 0, f"KB no fresh:\nSTDOUT:{r.stdout}\nSTDERR:{r.stderr}"

def test_kb_has_ten_notes():
    kb = REPO / "Contexto" / "KB_LLM"
    notes = sorted(kb.glob("[0-9][0-9]_*.md"))
    assert len(notes) == 10, f"Esperadas 10 notas, encontradas {len(notes)}: {[n.name for n in notes]}"
```

**Validación:**
```bash
python3 scripts/check_kb_freshness.py    # Esperado: "KB fresh." exit 0
pytest tests/test_kb_freshness.py -v     # Esperado: 2 passed
```

> **Ajuste 2026-06-09:** el script se extiende en Tarea 0.K para validar también `params/2026.json` y `KB_LLM/02_parametros_vigentes.md` (ver Tarea 0.K abajo).

---

#### Tarea 0.K — Actualización a params 2026 (Decreto 1469/2025 SMMLV, Decreto 1470/2025 aux_trans, Ley 2466/2025 Art. 64)

> **Origen:** la SMMLV 2026 ($1.750.905) y el auxilio de transporte 2026 ($249.095) fueron fijados por los Decretos 1469 y 1470 de 2025 (expedidos 30-dic-2025), vigentes desde el 1-ene-2026. La Ley 2466/2025 (Art. 64) añadió la opción de pago mensual de intereses sobre cesantías (1% mensual = 12% anual, solo con acuerdo escrito). Adicionalmente, el cronograma de recargo dominical gradual cambia de 80% a 90% el 2026-07-01. Esta tarea es prerequisito de Tarea 1.E (ParamsProvider debe ser year-aware para poder servir 2025 y 2026).

**Archivos a crear/modificar:**
- Crear `params/2026.json`.
- Modificar `params/normas.json` (entradas nuevas: DECRETO_1469_2025, DECRETO_1470_2025, LEY_2466_2025_INTERESES_MENSUALES; actualizar LEY_2466_2025).
- Modificar `scripts/check_kb_freshness.py` (validar también `params/2026.json`).
- Modificar `tests/test_kb_freshness.py` (test nuevo: KB cita SMMLV 2026).
- Modificar `Contexto/KB_LLM/02_parametros_2025.md` → renombrar a `02_parametros_vigentes.md` con tabla comparativa 2025 vs 2026 y regla de selección por `fecha_corte`.
- (Opcional, si hay URL pública verificable) descargar PDFs de los decretos a `legal_docs/` y registrarlos en `params/normas.json:url`.

**Contenido de `params/2026.json` (esquema `parametros_anuales`):**

```json
{
  "SMMLV": 1750905,
  "AUXILIO_TRANS": 249095,
  "LIMITE_AUXILIO": 3501810,
  "TASA_INT_CESANTIAS": 0.12,
  "DIAS_BASE": 360.0,
  "VACACIONES_DENOM": 720.0,
  "REDONDEO": 0,
  "TOPE_INDEMNIZACION_SMMLV": 20,
  "FECHA_APLICACION_RECARGO_DOMINICAL": "2026-07-01",
  "version": "2026-06-09",
  "referencia": "Decreto 1469 de 2025 (SMMLV 2026), Decreto 1470 de 2025 (aux_trans 2026), Ley 2466 de 2025 (recargo dominical gradual + Art. 64 opcion pago mensual intereses), Ley 50 de 1990 (intereses cesantias)"
}
```

**Entradas a agregar/modificar en `params/normas.json`:**

```json
{
  "id": "DECRETO_1469_2025",
  "nombre": "Decreto 1469 de 2025",
  "descripcion": "Salario Mínimo Legal Mensual Vigente 2026",
  "texto_relevante": "Establece el Salario Mínimo Legal Mensual Vigente para el año 2026 en la suma de $1.750.905 (un millón setecientos cincuenta mil novecientos cinco pesos).",
  "valor": 1750905,
  "url": "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=XXXXXX",
  "vigencia": "2026"
},
{
  "id": "DECRETO_1470_2025",
  "nombre": "Decreto 1470 de 2025",
  "descripcion": "Auxilio de transporte 2026",
  "texto_relevante": "Establece el valor del auxilio de transporte para el año 2026 en la suma de $249.095 (doscientos cuarenta y nueve mil noventa y cinco pesos) mensuales para trabajadores que devenguen hasta dos (2) Salarios Mínimos Mensuales Legales Vigentes.",
  "valor": 249095,
  "url": "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=XXXXXX",
  "vigencia": "2026"
},
{
  "id": "LEY_2466_2025_INTERESES_MENSUALES",
  "nombre": "Ley 2466 de 2025 Art. 64 (opcional)",
  "descripcion": "Pago mensual opcional de intereses sobre cesantías",
  "texto_relevante": "El empleador y el trabajador podrán acordar por escrito el pago mensual de los intereses sobre las cesantías, equivalente al uno por ciento (1%) del salario base de liquidación mensual, en lugar del pago anual único previsto en la Ley 50 de 1990. La tasa anual efectiva sigue siendo del 12% (1% mensual nominal = 12% anual nominal).",
  "factor_recargo": 0.01,
  "fecha_aplicacion": "2026-01-01",
  "url": "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=XXXXXX",
  "vigencia": "2026"
}
```

Y la entrada existente `LEY_2466_2025` (recargo dominical) se actualiza: `vigencia` cambia de `"2025"` a `"temporal"` y se le agrega nota sobre el cronograma gradual 75→80→90→100. La `factor_recargo` queda en 0.80 hasta el 2026-06-30; a partir del 2026-07-01 entra el 0.90.

**Regla de selección de params por año (a implementar en Tarea 1.E ParamsProvider):**

> Para cada fecha del rango líquido (p. ej. cada día entre `fecha_ingreso` y `fecha_corte`), se cargan los `params/<año_YYYY>.json` correspondientes. Para cálculos en un solo año se carga `params/<año>.json` directamente. Si la liquidación cruza el 1-Ene, el cálculo se segmenta por año calendario y se suman los resultados por concepto (cesantías 2025 + cesantías 2026, etc.).

**Validación:**
```bash
# 1. params/2026.json válido contra schema
PYTHONPATH=. python -c "import json, jsonschema; \
  schema=json.load(open('params/schema.json')); \
  p=json.load(open('params/2026.json')); \
  jsonschema.validate(p, schema['definitions']['parametros_anuales']); \
  print('2026.json OK')"

# 2. params/normas.json válido contra schema (tras agregar entradas nuevas)
PYTHONPATH=. python -c "import json, jsonschema; \
  schema=json.load(open('params/schema.json')); \
  n=json.load(open('params/normas.json')); \
  jsonschema.validate(n, schema['definitions']['normas_laborales']); \
  print('normas.json OK')"

# 3. Freshness script detecta 2026 (en la KB)
python3 scripts/check_kb_freshness.py   # Debe pasar tras actualizar KB_LLM/02

# 4. Suite verde
PYTHONPATH=. uv run --with pytest --with jsonschema pytest liquidator/tests -q
```

**No-DoD hasta ejecutar Tarea 0.K:** el motor seguirá usando `params/2025.json` (hardcodeado en `liquidator/params/` y próximamente en `ParamsProvider`). Cualquier cálculo con `fecha_corte >= 2026-01-01` dará resultados incorrectos hasta que ParamsProvider (Tarea 1.E) se haga year-aware. La auditoría inmutable (Fase 3) registrará este desfase.

> **⚠ Nota post-S11 (2026-06-13) — Hallazgo legal durante ejecución de 0.K:**
> El **Decreto 1469/2025 (SMMLV 2026 = $1.750.905)** fue **suspendido
> provisionalmente** por el **Consejo de Estado** (Sec. Segunda,
> Subsección A, Auto del 2026-02-12, **Exp. 11001-03-25-000-2026-00004-00**)
> y **re-fijado transitoriamente** por el **Decreto 159/2026** del
> **2026-02-19** con **el mismo valor** ($1.750.905). El SMMLV 2026
> **sigue vigente**; solo cambia el acto administrativo que lo fija.
> El motor **NO requiere cambios** (valor idéntico), pero el output
> de cada liquidación con `fecha_corte >= 2026-01-01` debe listar
> **ambos decretos** (`DECRETO_1469_2025` + `DECRETO_159_2026`) en
> `meta.referencias_normativas` para trazabilidad legal (ver
> `Contexto/KB_LLM/05_schema_salida.md` y R-LEG-07 en
> `Contexto/KB_LLM/06_riesgos_modelo.md`). Vigilar nulidad pendiente
> antes de v2.0 release. Esta nota **corrige** la línea 501 de este
> plan, que no mencionaba la suspensión (el plan fue escrito
> 2026-06-09, después de la suspensión pero antes del hallazgo en S11).
>
> **⚠ Otro hallazgo post-S11 (R-LEG-06, bloqueante):** la atribución
> de este plan (línea 501) al "Art. 64 de la Ley 2466/2025" para
> pago mensual de intereses sobre cesantías es **incorrecta**.
> Verificación SUIN del 2026-06-13 muestra que Art. 64 = "Régimen
> simple laboral", NO pago mensual de intereses. El motor NO debe
> implementar pago mensual de intereses hasta verificar el artículo
> literal exacto.

---

#### Tarea 0.I — `git init` y commit inicial

**Orden estricto:** Tarea 0.A (rotación de clave) **antes** de `git init`. `.gitignore` (0.B) **antes** del primer `git add`.

```bash
cd /mnt/c/Users/Jhond/Github/liquidacion_cli
git init
git config user.name "Jhond"
git config user.email "[email Jhond]"
git add .
git status   # Verificar: no debe listar .env, *.json sueltos, .coverage, htmlcov/, .venv/, liquidacion-env/
git commit -m "chore(fase-0): repo inicial limpio con KB, .gitignore, sintaxis corregida, scripts espurios reubicados"
```

**Validación:** `git status` retorna `nothing to commit, working tree clean`. `git log --oneline` muestra 1 commit.

---

#### Tarea 0.J — Estabilizar suite al 100% (o documentar)

Ejecutar la suite completa tras los fixes 0.D:

```bash
PYTHONPATH=/mnt/c/Users/Jhond/Github/liquidacion_cli \
uv run --with pytest --with python-dateutil --with PyYAML --with jsonschema \
--with pydantic --with loguru --with click --with markdown --with Jinja2 \
pytest liquidator/tests -q
```

- Si **0 fallos, 0 errores**: DoD cumplido en este punto.
- Si **fallos preexistentes** (no causados por 0.D): documentar cada uno en `Contexto/KB_LLM/06_riesgos_modelo.md` con:
  - ID del test que falla.
  - Razón probable (bug de cálculo vs expected value incorrecto).
  - Acción propuesta (corregir motor / corregir test) y **fase de resolución**.

**No se acepta cerrar Fase 0 con fallos preexistentes sin documentar.**

---

### 5.3 Riesgos Fase 0

- **R1:** Al rotar la clave de cifrado, datos previamente cifrados quedan ilegibles. Mitigación: documentar en `06_riesgos_modelo.md`; si hay datos cifrados en disco, re-cifrar o descartar.
- **R2:** `git init` después de la rotación pero con `.env` aún presente expone la clave nueva. Mitigación: 0.A → 0.B → `git init` en ese orden estricto.
- **R3:** Corregir `SyntaxError` puede requerir imports que no se usan (lint falla). Mitigación: agregar `# noqa: F401` o usar la importación inmediatamente.
- **R4:** Mover outputs a `output/_legacy/` puede romper scripts que esperan paths en raíz. Mitigación: en Fase 1, el entry point real no dependerá de la raíz.

---

## 6. Fase 1 — Estabilizar y formalizar

> **Objetivo:** Empaquetado moderno, CLI real, schemas formales (Pydantic), generadores consistentes, caso canónico verde.

### 6.1 DoD Fase 1

- [ ] `pyproject.toml` creado y vigente; `setup.py` reducido a compatibilidad.
- [ ] `pip install -e .` instala la CLI correctamente.
- [ ] `python -m liquidator.cli --help` muestra ayuda; `liquidacion --version` retorna versión (puede ser `0.x` o `1.0-dev` mientras se llega a v2.0).
- [ ] `liquidator/cli/main.py` existe con entry point real (`liquidacion=...` y `python -m liquidator.cli`).
- [ ] `input_schema/liquidacion_input.schema.json` creado (o modelo Pydantic `LiquidacionInput`).
- [ ] `contracts/liquidacion_result.schema.json` creado.
- [ ] `JSONGenerator`:
  - Acepta `schema_path` en `__init__`.
  - Lee todos los valores desde `params/2025.json` (sin constantes hardcodeadas).
  - Usa `validaciones_y_alertas` consistentemente.
- [ ] `markdown_generator.py`: SyntaxError corregido, maneja estado bloqueado/advertido, valida contexto antes de renderizar.
- [ ] `pdf_generator.py`: código muerto eliminado, no genera `.txt` disfrazado, valida header `%PDF-`.
- [ ] `params_versioning.py`: SyntaxError corregido, integración real con `ParamsLoader`.
- [ ] `params_validator.py`: validación real con schema (no `return True`).
- [ ] Test del caso canónico (206 días en dos segmentos, SBL=2.200.000, cesantías TBD-motor-Fase2 (ver §3, segmento 2025 + segmento 2026)) **verde**.
- [ ] **Schema `Salario` extendido con `sbl_por_anio: dict[int, Decimal] | None` y `historial_salarial: list[MesValor] | None`** (campos opcionales, retrocompatibles con `Salario.SBL` único). `model_validator` rechaza `variable=True` sin `historial_salarial` ni `sbl_por_anio`.
- [ ] Caso canónico **sin los campos nuevos rellenos** sigue verde (regresión cero: comportamiento idéntico al actual). Input con `sbl_por_anio` o `historial_salarial` activa el modelo anualizado (consumido por Tarea 2.B-bis en Fase 2).
- [ ] **Schema `Contrato` extendido con `motivo_terminacion: MotivoTerminacion | None` (enum)** que cubre los motivos de terminación de los Arts. 45-49 CST (renuncia_voluntaria, despido_sin_justa_causa, despido_con_justa_causa, termino_fijo_vencido, obra_o_labor_terminada, mutuo_acuerdo, muerte_trabajador, muerte_empleador, suspension_deficitaria, cierre_empresa). Campo opcional (default `None`) → retrocompatible con caso canónico PERIODICA. `model_validator` exige `motivo_terminacion` cuando `fecha_terminacion_real` está presente.
- [ ] **Nuevo modelo `VacacionesEstado` tipado** (reemplaza el `dict` libre de `LiquidacionInput.vacaciones`) con campos `dias_causados_proporcionales`, `dias_disfrutados`, `dias_pendientes` (en `Decimal`, no `int`, para soportar fracciones de día legalmente válidas CST), `fechas_disfrute` opcional. `model_validator` rechaza `dias_pendientes > dias_causados - dias_disfrutados` con mensaje claro.
- [ ] `LiquidacionInput._finiquito_requiere_motivo` valida que `modo == "FINIQUITO"` exige `contrato.motivo_terminacion`. Caso canónico PERIODICA (sin `motivo_terminacion`) **sigue verde** (regresión cero: PERIODICA no requiere motivo).
- [ ] Tests nuevos en `liquidator/tests/test_contracts/test_vacaciones_estado.py` y `liquidator/tests/test_contracts/test_motivo_terminacion.py` verdes; caso canónico (PERIODICA) sin campos nuevos **sigue verde** (regresión obligatoria).
- [ ] Suite al 100%.

### 6.2 Tareas Fase 1 (orden sugerido)

#### Tarea 1.A — `pyproject.toml` y packaging

**Archivo:** crear `pyproject.toml` en la raíz.

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "liquidacion-cli"
version = "0.2.0-dev"   # Se promoverá a 2.0.0 en Fase 4
description = "CLI local para liquidación de nómina colombiana"
requires-python = ">=3.11"
dependencies = [
  "pydantic>=2",
  "PyYAML>=6",
  "jsonschema>=4",
  "python-dateutil>=2.8",
  "click>=8",
  "loguru>=0.7",
  "markdown>=3.5",
  "Jinja2>=3.1",
  "WeasyPrint>=60",
]

[project.optional-dependencies]
dev = ["pytest>=8", "pytest-cov", "ruff", "mypy", "black"]

[project.scripts]
liquidacion = "liquidator.cli.main:main"

[tool.setuptools.packages.find]
include = ["liquidator*"]

[tool.setuptools.package-data]
liquidator = ["templates/*.j2", "templates/*.md", "templates/*.css"]
```

**Acciones:**
1. Crear `pyproject.toml`.
2. Mover plantillas reales de `templates/` a `liquidator/templates/` (o ajustar `package-data`).
3. **Eliminar** los entry points inválidos de `setup.py` (`settle`, `settle-compliance`, `settle-update-params`, `settle-generate-tests`).
4. **Eliminar** `package_data` incorrecto de `setup.py` (el que apunta a `liquidator/templates/*` cuando las plantillas están en `templates/`).

**Validación:**
```bash
pip install -e .      # O: uv pip install -e .
liquidacion --version # Esperado: 0.2.0-dev (o similar)
```

---

#### Tarea 1.B — `liquidator/cli/main.py` (entry point real)

**Archivo:** crear `liquidator/cli/__init__.py` y `liquidator/cli/main.py`.

CLI mínimo basado en Click (subcomandos: `liquidar`, `validate`, `info`):

```python
# liquidator/cli/main.py
"""Entry point CLI: liquidacion"""
import sys
import click
from pathlib import Path
from loguru import logger

from .. import __version__
from ..core.engine import LiquidacionEngine
from ..core.input_parser import InputParser
from ..validators.input_validator import InputValidator
from ..core.params_provider import ParamsProvider

@click.group()
@click.version_option(__version__, prog_name="liquidacion")
def main():
    """Liquidación de nómina colombiana — CLI local."""

@main.command()
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.option("--out-dir", type=click.Path(path_type=Path), default=Path("output"))
@click.option("--override", is_flag=True, help="Forzar override de fallos HIGH (registrado en auditoría)")
@click.option("--override-reason", default=None, help="Justificación del override")
def liquidar(input_path: Path, out_dir: Path, override: bool, override_reason: str | None):
    """Liquida a partir de un JSON de entrada."""
    params = ParamsProvider.current()
    raw = InputParser().parse(str(input_path))
    InputValidator(params).validate(raw)  # puede lanzar CRITICAL
    engine = LiquidacionEngine(params=params)
    result = engine.process_input(raw, override=override, override_reason=override_reason)
    # ... persistir result, renderizar markdown/pdf, retornar exit code
    sys.exit(0 if result["compliance_status"] in ("GO", "WARN", "OVERRIDE_APPROVED") else 2)

@main.command()
def info():
    """Muestra parámetros vigentes y estado de la suite."""
    p = ParamsProvider.current()
    click.echo(f"SMMLV: {p.SMMLV}")
    click.echo(f"Auxilio transporte: {p.AUXILIO_TRANS}")
    click.echo(f"Tasa int. cesantías: {p.TASA_INT_CESANTIAS}")

if __name__ == "__main__":
    main()
```

> **Nota:** Esta es la forma objetivo. En Fase 1.B se acepta un esqueleto que solo valide input y muestre el resultado en JSON por stdout. La integración completa con generadores MD/PDF se hace en Fase 3.

**Validación:**
```bash
python -m liquidator.cli --help
# Esperado: Usage: ...
python -m liquidator.cli info
# Esperado: SMMLV: 1423500, ...
```

---

#### Tarea 1.C — Schemas de entrada y salida (Pydantic)

**Archivos:**
- Crear `liquidator/contracts/input_model.py` con modelo Pydantic `LiquidacionInput`.
- Crear `liquidator/contracts/output_model.py` con `LiquidacionResult`.
- (Opcional) `input_schema/liquidacion_input.schema.json` y `contracts/liquidacion_result.schema.json` como JSON Schema derivable de los modelos Pydantic con `model_json_schema()`.

Modelo de entrada (campos del diag. §3.5):

```python
from pydantic import BaseModel, Field, field_validator
from datetime import date
from decimal import Decimal
from typing import Literal

class Trabajador(BaseModel):
    nombre: str
    documento: str

class Empleador(BaseModel):
    nombre: str
    documento: str

class Contrato(BaseModel):
    fecha_ingreso: date
    fecha_corte: date
    tipo: Literal["INDEFINIDO", "FIJO", "OBRA_LABOR", "PRESTACION"]
    motivo_terminacion: str | None = None

class Salario(BaseModel):
    SBL: Decimal = Field(gt=0)
    auxilio_transporte: bool = False
    variable: bool = False
    dias_trabajados: int | None = None  # requerido si variable=True

class LiquidacionInput(BaseModel):
    trabajador: Trabajador
    empleador: Empleador
    contrato: Contrato
    salario: Salario
    modo: Literal["PERIODICA", "FINIQUITO", "VACACIONES"]
    vacaciones: dict | None = None  # {dias_causados, dias_tomados, fecha_inicio, fecha_fin}
    auxilios: dict | None = None   # extensibilidad

    @field_validator("contrato")
    @classmethod
    def _corte_mayor_ingreso(cls, v):
        if v.fecha_corte < v.fecha_ingreso:
            raise ValueError("fecha_corte debe ser >= fecha_ingreso")
        return v
```

**Validación:**
```python
def test_input_canonico_pasa():
    inp = LiquidacionInput.model_validate({
      "trabajador": {"nombre": "X", "documento": "1"},
      "empleador":  {"nombre": "Y", "documento": "2"},
      "contrato":   {"fecha_ingreso": "2025-11-16", "fecha_corte": "2026-06-15", "tipo": "INDEFINIDO"},
      "salario":    {"SBL": 2200000},
      "modo":       "PERIODICA",
    })
    assert inp.contrato.fecha_corte > inp.contrato.fecha_ingreso

def test_input_corte_anterior_falla():
    with pytest.raises(ValidationError):
        LiquidacionInput.model_validate({
          "trabajador": {"nombre": "X", "documento": "1"},
          "empleador":  {"nombre": "Y", "documento": "2"},
          "contrato":   {"fecha_ingreso": "2026-06-15", "fecha_corte": "2025-11-16", "tipo": "INDEFINIDO"},
          "salario":    {"SBL": 2200000},
          "modo":       "PERIODICA",
        })
```

---

#### Tarea 1.C-bis — Extender `Salario` con historial/B.1 *(absorción addendum SL2630-2024)*

>**Origen:** Addendum `addendum_sl2630_y_ipc_2026-06-09.md` §B.1 y Tarea 1.C-bis. Decisión: absorber en v2.0.0 antes del release. Habilita anualización salarial (SL2630-2024: cada año calendario se liquida con el promedio del salario de ESE año). Por sí sola esta tarea NO cambia el cálculo del caso canónico (SBL constante 2.200.000); prepara el terreno para Tarea 2.B-bis (Fase 2) que sí cambia el motor.

**Archivos:**
- Modificar `liquidator/contracts/input_model.py` (extender `Salario`, agregar `MesValor`).
- Actualizar `Contexto/KB_LLM/04_schema_entrada.md` (documentar campos nuevos).
- Actualizar `examples/inputs/caso_canonico_periodico_206d.json` (sin nuevos campos, mantener regresión).
- Crear `liquidator/tests/test_contracts/test_salario_extendido.py` (cubrir regresión + nueva lógica).

**Cambios al schema (forma mínima viable, retrocompatible):**

```python
from pydantic import BaseModel, Field, model_validator
from decimal import Decimal

class MesValor(BaseModel):
    año: int
    mes: int = Field(ge=1, le=12)
    valor: Decimal = Field(gt=0)

class Salario(BaseModel):
    # Existentes (compatibilidad total con v1.x)
    SBL: Decimal = Field(gt=0)
    auxilio_transporte: bool = False
    variable: bool = False
    dias_trabajados: int | None = None

    # NUEVOS (opcionales, retrocompatibles; consumo en Tarea 2.B-bis)
    sbl_por_anio: dict[int, Decimal] | None = None
    historial_salarial: list[MesValor] | None = None

    @model_validator(mode="after")
    def _consistencia(self):
        if self.variable and not self.historial_salarial and not self.sbl_por_anio:
            raise ValueError(
                "Salario variable requiere historial_salarial o sbl_por_anio"
            )
        return self
```

**Mutuamente excluyentes a nivel de input (documentar en KB):** el usuario elige una de tres formas (o una combinación compatible). El motor intenta en este orden (Tarea 2.B-bis):
1. `historial_salarial` → promedio del año del segmento.
2. `sbl_por_anio[<año>]` → SBL explícito por año.
3. `SBL` único (compatibilidad actual).

**Validación (DoD Fase 1):**

```python
# tests/test_contracts/test_salario_extendido.py
import pytest
from pydantic import ValidationError
from decimal import Decimal
from liquidator.contracts.input_model import Salario, MesValor

def test_salario_sin_campos_nuevos_es_compatible():
    """Regresión: input v1.x sigue funcionando idéntico."""
    s = Salario(SBL=Decimal("2200000"))
    assert s.sbl_por_anio is None
    assert s.historial_salarial is None
    assert s.variable is False

def test_salario_variable_sin_historial_falla():
    """variable=True exige al menos uno de los campos nuevos."""
    with pytest.raises(ValidationError, match="variable requiere"):
        Salario(SBL=Decimal("2200000"), variable=True)

def test_salario_variable_con_historial_pasa():
    s = Salario(
        SBL=Decimal("2200000"),
        variable=True,
        historial_salarial=[
            MesValor(año=2025, mes=11, valor=Decimal("2200000")),
            MesValor(año=2025, mes=12, valor=Decimal("2200000")),
            MesValor(año=2026, mes=1, valor=Decimal("2400000")),
        ],
    )
    assert len(s.historial_salarial) == 3

def test_salario_con_sbl_por_anio_pasa():
    s = Salario(
        SBL=Decimal("2200000"),
        sbl_por_anio={2025: Decimal("2200000"), 2026: Decimal("2400000")},
    )
    assert s.sbl_por_anio[2026] == Decimal("2400000")

def test_mesvalor_valida_rango_mes():
    with pytest.raises(ValidationError):
        MesValor(año=2025, mes=13, valor=Decimal("2200000"))
    with pytest.raises(ValidationError):
        MesValor(año=2025, mes=0, valor=Decimal("2200000"))

def test_mesvalor_valida_valor_positivo():
    with pytest.raises(ValidationError):
        MesValor(año=2025, mes=6, valor=Decimal("0"))
    with pytest.raises(ValidationError):
        MesValor(año=2025, mes=6, valor=Decimal("-1000"))
```

**Pruebas de regresión obligatorias (no romper Fase 0):**
```bash
# Caso canónico SIN los campos nuevos: resultado idéntico al actual
PYTHONPATH=. pytest liquidator/tests/test_canonico/test_caso_canonico_usuario.py -v
# Esperado: 1+ passed (sin modificar el JSON de input)

# Suite completa Fase 1
PYTHONPATH=. pytest liquidator/tests -q
# Esperado: 100% passed, 0 errors (los nuevos tests suman al conteo)
```

**No-DoD hasta ejecutar Tarea 1.C-bis:** el motor seguirá tratando `SBL` como valor único anual. Cualquier intento de anualización real (Tarea 2.B-bis) NO puede completarse sin esta tarea. La auditoría inmutable (Fase 3) NO se afecta; pero el sistema queda **incapaz** de manejar casos con variabilidad salarial (SBL cambia a mitad de periodo) hasta cerrar esta tarea y la 2.B-bis.

**Riesgos específicos:**
- **R1:** `model_validator` se evalúa DESPUÉS de la creación de campos, por lo que un input con `variable=True` que también trae `SBL` pero ningún campo nuevo debe fallar. Mitigación: test explícito `test_salario_variable_sin_historial_falla`.
- **R2:** `dict[int, Decimal]` puede traer claves que no correspondan a años vigentes. Mitigación: validación laxa en esta tarea (acepta cualquier `int`); `ParamsProvider.for_year(año)` en Fase 2 levantará `FileNotFoundError` si el año no tiene `params/<año>.json`.
- **R3:** El validador podría romper inputs históricos de Fase 0 que tenían `variable=True` por error. Mitigación: revisar `examples/inputs/` y `examples/expected/` en busca de `variable: true` y corregir antes de aplicar el validador.

---

#### Tarea 1.C-ter — Extender `Contrato` con `motivo_terminacion` y agregar `VacacionesEstado` tipado *(absorción addendum finiquito/vacaciones 2026-06-11)*

>**Origen:** Addendum `addendum_finiquito_renuncia_vacaciones_2026-06-11.md` §B.2, §B.3 y Tarea 1.C-ter. Decisión 2026-06-11: absorber en v2.0.0 antes del release. Habilita el motor para distinguir finiquito por renuncia voluntaria (Art. 49 num. 6 CST, sin indemnización) de otros motivos (despido sin justa causa con Art. 64, mutuo acuerdo, etc.) y formaliza el estado de vacaciones al cierre. Por sí sola esta tarea NO cambia el cálculo del caso canónico (modo PERIODICA, sin `motivo_terminacion` ni `vacaciones`); prepara el terreno para Tarea 2.B-ter (Fase 2, `calculate_vacaciones_compensadas_finiquito`) y Tarea 3.G (Fase 3, pre-render + plantilla por motivo).
>
> **Convención de nombre:** se numera "1.C-ter" (ter) por analogía con 1.C-bis y para mantener el correlato de numeración entre addenda, aunque la tarea **no toca** `Salario` sino `Contrato` y `LiquidacionInput`.

**Archivos:**
- Modificar `liquidator/contracts/input_model.py` (agregar `MotivoTerminacion` enum, `PeriodoDisfrute`, `VacacionesEstado`; actualizar `Contrato.fecha_terminacion_real` para que coexista con `motivo_terminacion`; actualizar `LiquidacionInput.vacaciones` para usar el modelo tipado).
- Actualizar `Contexto/KB_LLM/04_schema_entrada.md` (documentar `motivo_terminacion`, `VacacionesEstado` y los motivos del enum).
- Crear `liquidator/tests/test_contracts/test_vacaciones_estado.py` (cubrir validación, casos válidos, casos inválidos).
- Crear `liquidator/tests/test_contracts/test_motivo_terminacion.py` (cubrir enum, validación cruzada con `fecha_terminacion_real`, validación cruzada con `modo FINIQUITO`).
- Actualizar `examples/inputs/caso_canonico_periodico_206d.json` (sin nuevos campos, mantener regresión — verificar que sigue parseando idéntico).

**Cambios al schema (forma mínima viable, retrocompatible):**

```python
# liquidator/contracts/input_model.py
from pydantic import BaseModel, Field, model_validator
from datetime import date
from decimal import Decimal
from typing import Literal
from enum import Enum

class MotivoTerminacion(str, Enum):
    """Motivos de terminación del contrato laboral (Arts. 45-49 CST).
    El valor del enum es el string canónico que va al JSON."""
    RENUNCIA_VOLUNTARIA = "renuncia_voluntaria"           # Art. 49 num. 6
    DESPIDO_SIN_JUSTA_CAUSA = "despido_sin_justa_causa"   # Art. 64
    DESPIDO_CON_JUSTA_CAUSA = "despido_con_justa_causa"   # Art. 62
    TERMINO_FIJO_VENCIDO = "termino_fijo_vencido"         # Art. 46
    OBRA_O_LABOR_TERMINADA = "obra_o_labor_terminada"     # Art. 45
    MUTUO_ACUERDO = "mutuo_acuerdo"                       # Art. 49 num. 1
    MUERTE_TRABAJADOR = "muerte_trabajador"               # Art. 49 num. 5
    MUERTE_EMPLEADOR = "muerte_empleador"                 # Art. 49 num. 4 (persona natural)
    SUSPENSION_DEFICITARIA = "suspension_deficitaria"     # Art. 49 num. 3
    CIERRE_EMPRESA = "cierre_empresa"                     # Art. 49 num. 3

class PeriodoDisfrute(BaseModel):
    """Rango continuo de disfrute de vacaciones (histórico opcional)."""
    desde: date
    hasta: date  # inclusive

class VacacionesEstado(BaseModel):
    """Estado de vacaciones del trabajador al cierre del periodo.
    Reemplaza el `dict` libre del input. Tipos en Decimal para soportar
    fracciones de día legalmente válidas en CST (Art. 189 + 190)."""
    dias_causados_proporcionales: Decimal | None = None
    dias_disfrutados: Decimal = Decimal(0)
    dias_pendientes: Decimal = Field(ge=0)
    fechas_disfrute: list[PeriodoDisfrute] | None = None

    @model_validator(mode="after")
    def _consistencia(self):
        # Si el usuario pasó dias_causados_proporcionales, validar que
        # dias_pendientes <= dias_causados - dias_disfrutados.
        causados = self.dias_causados_proporcionales
        if causados is not None:
            max_pendientes = causados - self.dias_disfrutados
            if self.dias_pendientes > max_pendientes:
                raise ValueError(
                    f"dias_pendientes ({self.dias_pendientes}) excede el máximo "
                    f"causable ({max_pendientes} = {causados} - {self.dias_disfrutados})"
                )
        return self

class Contrato(BaseModel):
    fecha_ingreso: date
    fecha_corte: date
    tipo: Literal["INDEFINIDO", "FIJO", "OBRA_LABOR", "PRESTACION"]
    motivo_terminacion: MotivoTerminacion | None = None      # NUEVO (opcional)
    fecha_terminacion_real: date | None = None               # ya existía opcional

    @model_validator(mode="after")
    def _terminacion_real_requiere_motivo(self):
        # Si hay fecha de terminación real, debe venir con motivo.
        if self.fecha_terminacion_real and not self.motivo_terminacion:
            raise ValueError(
                "Si hay fecha_terminacion_real, es obligatorio motivo_terminacion"
            )
        return self

class LiquidacionInput(BaseModel):
    trabajador: Trabajador
    empleador: Empleador
    contrato: Contrato
    salario: Salario
    modo: Literal["PERIODICA", "FINIQUITO", "VACACIONES"]
    vacaciones: VacacionesEstado | None = None              # NUEVO: tipado (antes dict)
    auxilios: dict | None = None                            # extensibilidad

    @model_validator(mode="after")
    def _finiquito_requiere_motivo(self):
        # Modo FINIQUITO exige motivo_terminacion explícito.
        if self.modo == "FINIQUITO" and not self.contrato.motivo_terminacion:
            raise ValueError(
                "Liquidación en modo FINIQUITO requiere contrato.motivo_terminacion"
            )
        return self
```

**Compatibilidad hacia atrás (validada con tests de regresión):**
- Caso canónico PERIODICA (sin `motivo_terminacion`, sin `vacaciones`): el input **sigue parseando idéntico**. La regresión se valida con `test_canonico_sin_campos_nuevos_sigue_verde` (extensión del existente en Tarea 1.C-bis).
- Inputs con `vacaciones` como `dict` legacy: la migración la hace Pydantic automáticamente. Si los campos del dict son consistentes con `VacacionesEstado`, la coerción a `VacacionesEstado` funciona; si no, `ValidationError` claro.
- Inputs históricos con `fecha_terminacion_real` sin `motivo_terminacion`: **nuevo requisito obligatorio** que rompe compatibilidad. Acción: revisar `examples/inputs/` y agregar `motivo_terminacion` apropiado a los fixtures históricos que ya tengan `fecha_terminacion_real`.

**DoD específico de Tarea 1.C-ter:**
- Caso canónico (PERIODICA, SBL 2.200.000, 206d en dos segmentos) **sigue verde** sin modificar el JSON de input (regresión cero obligatoria).
- Input nuevo con `modo=FINIQUITO`, `motivo_terminacion=RENUNCIA_VOLUNTARIA`, `vacaciones={dias_pendientes: 7.5}` pasa validación.
- Input con `dias_pendientes > dias_causados - dias_disfrutados` falla con `ValidationError` claro.
- Input con `modo=FINIQUITO` sin `motivo_terminacion` falla con `ValidationError` claro.
- Input con `fecha_terminacion_real` sin `motivo_terminacion` falla con `ValidationError` claro.
- `VacacionesEstado.dias_pendientes` acepta `Decimal("7.5")` (fracciones de día).

**Validación (tests de Fase 1):**

```python
# liquidator/tests/test_contracts/test_vacaciones_estado.py
import pytest
from decimal import Decimal
from pydantic import ValidationError
from liquidator.contracts.input_model import VacacionesEstado

def test_vacaciones_estado_pasa_minimo():
    v = VacacionesEstado(dias_pendientes=Decimal("7.5"))
    assert v.dias_pendientes == Decimal("7.5")
    assert v.dias_disfrutados == Decimal(0)
    assert v.dias_causados_proporcionales is None
    assert v.fechas_disfrute is None

def test_vacaciones_estado_pasa_con_causados_ok():
    v = VacacionesEstado(
        dias_causados_proporcionales=Decimal("10"),
        dias_disfrutados=Decimal("2"),
        dias_pendientes=Decimal("8"),
    )
    assert v.dias_pendientes == Decimal("8")

def test_vacaciones_estado_rechaza_pendientes_excedidos():
    with pytest.raises(ValidationError, match="excede el máximo"):
        VacacionesEstado(
            dias_causados_proporcionales=Decimal("5"),
            dias_disfrutados=Decimal("2"),
            dias_pendientes=Decimal("10"),  # 10 > 5 - 2 = 3 → falla
        )

def test_vacaciones_estado_acepta_fracciones_dia():
    """Caso real: 7.5 días de vacaciones pendientes (fracción legal en CST)."""
    v = VacacionesEstado(dias_pendientes=Decimal("7.5"))
    assert v.dias_pendientes == Decimal("7.5")

def test_vacaciones_estado_pendientes_negativo_falla():
    with pytest.raises(ValidationError):
        VacacionesEstado(dias_pendientes=Decimal("-1"))
```

```python
# liquidator/tests/test_contracts/test_motivo_terminacion.py
import pytest
from datetime import date
from decimal import Decimal
from pydantic import ValidationError
from liquidator.contracts.input_model import (
    LiquidacionInput, MotivoTerminacion,
)

def _base_kwargs():
    return {
        "trabajador": {"nombre": "X", "documento": "1"},
        "empleador":  {"nombre": "Y", "documento": "2"},
        "contrato": {
            "fecha_ingreso": "2025-11-16",
            "fecha_corte":   "2026-06-15",
            "tipo": "INDEFINIDO",
        },
        "salario": {"SBL": 2200000},
        "modo": "PERIODICA",
    }

def test_motivo_enum_valores():
    assert MotivoTerminacion.RENUNCIA_VOLUNTARIA.value == "renuncia_voluntaria"
    assert MotivoTerminacion.DESPIDO_SIN_JUSTA_CAUSA.value == "despido_sin_justa_causa"
    # Cobertura rápida de los 10 motivos:
    assert len(MotivoTerminacion) == 10

def test_canonico_periodico_sin_motivo_sigue_verde():
    """Regresión dura: caso canónico (PERIODICA, sin motivo) no debe romperse."""
    inp = LiquidacionInput.model_validate(_base_kwargs())
    assert inp.contrato.motivo_terminacion is None
    assert inp.vacaciones is None
    assert inp.modo == "PERIODICA"

def test_finiquito_renuncia_voluntaria_pasa():
    inp_dict = _base_kwargs()
    inp_dict.update({
        "contrato": {
            **inp_dict["contrato"],
            "motivo_terminacion": "renuncia_voluntaria",
            "fecha_terminacion_real": "2026-06-15",
        },
        "modo": "FINIQUITO",
        "vacaciones": {"dias_pendientes": 7.5},
    })
    inp = LiquidacionInput.model_validate(inp_dict)
    assert inp.contrato.motivo_terminacion == MotivoTerminacion.RENUNCIA_VOLUNTARIA
    assert inp.vacaciones.dias_pendientes == Decimal("7.5")

def test_finiquito_sin_motivo_falla():
    inp_dict = _base_kwargs()
    inp_dict.update({
        "contrato": {
            **inp_dict["contrato"],
            "fecha_terminacion_real": "2026-06-15",  # sin motivo
        },
        "modo": "FINIQUITO",
    })
    with pytest.raises(ValidationError, match="motivo_terminacion"):
        LiquidacionInput.model_validate(inp_dict)

def test_terminacion_real_sin_motivo_falla():
    inp_dict = _base_kwargs()
    inp_dict["contrato"]["fecha_terminacion_real"] = "2026-06-15"  # sin motivo
    with pytest.raises(ValidationError, match="motivo_terminacion"):
        LiquidacionInput.model_validate(inp_dict)
```

```bash
# Pruebas de regresión obligatorias (no romper Fase 0 ni Tarea 1.C-bis)
PYTHONPATH=. pytest liquidator/tests/test_canonico/test_caso_canonico_usuario.py -v
# Esperado: 1+ passed (caso canónico PERIODICA sin nuevos campos)

PYTHONPATH=. pytest liquidator/tests/test_contracts/test_vacaciones_estado.py \
                 liquidator/tests/test_contracts/test_motivo_terminacion.py -v
# Esperado: 5 + 5 = 10+ passed

PYTHONPATH=. pytest liquidator/tests -q
# Esperado: 100% passed, 0 errors
```

**No-DoD hasta ejecutar Tarea 1.C-ter:** el motor seguirá aceptando inputs con `vacaciones` como `dict` libre (sin tipar) y no podrá distinguir motivos de terminación. Tarea 2.B-ter (Fase 2) NO puede completarse sin esta tarea porque el método `calculate_vacaciones_compensadas_finiquito` necesita `inp.contrato.motivo_terminacion` para decidir si aplica. La auditoría inmutable (Fase 3) NO se afecta; pero el sistema queda **incapaz** de liquidar finiquitos correctamente hasta cerrar Tarea 1.C-ter, 2.B-ter, 2.Z y 3.G.

**Riesgos específicos:**
- **R1:** Migrar `vacaciones: dict | None` a `VacacionesEstado | None` puede romper inputs históricos con estructura de dict inconsistente. Mitigación: revisar `examples/inputs/` y `examples/expected/`; si hay dicts legacy, ajustar manualmente antes de aplicar el cambio de tipo.
- **R2:** Cambiar `dias_pendientes` de `int` (en el addendum original) a `Decimal` puede afectar redondeos en cálculos posteriores. Mitigación: `VacacionesEstado` mantiene el tipo Decimal; el método `calculate_vacaciones_compensadas_finiquito` (Tarea 2.B-ter) usa `Decimal` end-to-end y `quantize(Decimal("1"), rounding=ROUND_HALF_UP)`. Las fracciones de día son legales en CST (Art. 189 + 190 — "un día de salario por cada día de vacaciones" interpretado con la práctica laboral colombiana que acepta medios días).
- **R3:** Inputs antiguos con `fecha_terminacion_real` sin `motivo_terminacion` ahora fallan. Mitigación: revisar `examples/inputs/` para identificar fixtures históricos que ya tengan `fecha_terminacion_real`; agregarles el `motivo_terminacion` apropiado. Si hay muchos, script de migración `scripts/migrate_terminacion_motivo.py` (Fase 1, opcional).
- **R4:** El enum `MotivoTerminacion` puede no cubrir todos los motivos legales si surge jurisprudencia nueva. Mitigación: enum es extensible; agregar un valor nuevo no rompe inputs que ya usen valores existentes; documentar en KB que cualquier motivo fuera del enum es NO VÁLIDO para v2.0.

---

#### Tarea 1.D — Refactor `JSONGenerator`

**Archivo:** `liquidator/output/json_generator.py`

**Cambios obligatorios:**
1. `__init__(self, schema_path: str | Path | None = None, params: dict | None = None)`.
2. Si `params` no se pasa, leer de `ParamsProvider.current().to_dict()`.
3. Eliminar constantes hardcodeadas (L50-55 según diag. §3.8).
4. Usar `validaciones_y_alertas` consistentemente.
5. Validar salida contra `contracts/liquidacion_result.schema.json` (si está disponible).

```python
# Esqueleto
class JSONGenerator:
    def __init__(self, schema_path: str | Path | None = None, params: dict | None = None):
        self.schema_path = Path(schema_path) if schema_path else None
        self.params = params or ParamsProvider.current().to_dict()

    def generate_output(self, calculation_result: dict) -> dict:
        out = {
            "metadata": {
                "version": __version__,
                "params_version": self.params.get("VERSION", "unknown"),
                "params_hash": self.params.get("HASH", ""),
            },
            "trabajador": calculation_result["trabajador"],
            "empleador":  calculation_result["empleador"],
            "contrato":   calculation_result["contrato"],
            "desglose":   calculation_result["desglose"],
            "validaciones_y_alertas": calculation_result.get("validaciones_y_alertas", {}),
            "compliance": calculation_result.get("compliance", {}),
        }
        if self.schema_path:
            validate(instance=out, schema=json.loads(self.schema_path.read_text()))
        return out
```

**Validación:**
```python
def test_json_generator_usa_params_inyectados():
    g = JSONGenerator(params={"SMMLV": 999, "AUXILIO_TRANS": 1, ...})
    out = g.generate_output({...})
    assert out["metadata"]["params_version"] != "unknown"

def test_json_generator_valida_contra_schema_si_existe():
    g = JSONGenerator(schema_path="contracts/liquidacion_result.schema.json")
    out = g.generate_output({...})
    # No debe lanzar
```

---

#### Tarea 1.E — Refactor `ParamsProvider` centralizado (year-aware)

**Archivo:** crear `liquidator/core/params_provider.py`.

**Decisión de diseño (Tarea 0.K + 1.E):** el proveedor de parámetros debe ser **year-aware** desde el inicio, no como refactor posterior. Las liquidaciones pueden cruzar el 1-Ene (caso canónico del plan: 2025-11-16 a 2026-06-09), por lo que el proveedor debe poder servir uno o varios `params/<año>.json` según el rango.

```python
from pathlib import Path
import json, threading
from datetime import date
from typing import Any

class ParamsProvider:
    """Acceso centralizado y year-aware a params/<año>.json.

    API:
      - ParamsProvider.current()             -> última versión disponible (año mayor)
      - ParamsProvider.for_year(year: int)   -> año explícito
      - ParamsProvider.for_date(fecha: date) -> año de la fecha
      - ParamsProvider.for_range(desde, hasta) -> dict {año: params} cubriendo el rango
    """
    _instance = None           # singleton "current" (compatibilidad)
    _lock = threading.Lock()
    _data: dict = {}
    _params_dir: Path | None = None

    @classmethod
    def _params_dir_default(cls) -> Path:
        repo = Path(__file__).resolve().parents[2]
        return repo / "params"

    @classmethod
    def current(cls) -> "ParamsProvider":
        """Compatibilidad: devuelve la última versión disponible (año mayor)."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls._load_latest()
            return cls._instance

    @classmethod
    def for_year(cls, year: int) -> "ParamsProvider":
        """Carga params/<year>.json explícitamente."""
        p = cls._params_dir_default() / f"{year}.json"
        data = json.loads(p.read_text())
        inst = cls()
        inst._data = data
        return inst

    @classmethod
    def for_date(cls, fecha: date) -> "ParamsProvider":
        return cls.for_year(fecha.year)

    @classmethod
    def for_range(cls, desde: date, hasta: date) -> dict[int, "ParamsProvider"]:
        """Devuelve {año: ParamsProvider} cubriendo todos los años del rango."""
        result: dict[int, ParamsProvider] = {}
        for year in range(desde.year, hasta.year + 1):
            result[year] = cls.for_year(year)
        return result

    @classmethod
    def _load_latest(cls) -> "ParamsProvider":
        """Carga el params/<año>.json con año mayor en params/."""
        params_dir = cls._params_dir_default()
        year_files = sorted(params_dir.glob("[0-9][0-9][0-9][0-9].json"))
        if not year_files:
            raise FileNotFoundError(f"No se encontraron params/<año>.json en {params_dir}")
        latest = year_files[-1]
        data = json.loads(latest.read_text())
        inst = cls()
        inst._data = data
        return inst

    @classmethod
    def reload(cls) -> "ParamsProvider":
        with cls._lock:
            cls._instance = None
        return cls.current()

    # Accesores tipados (del año actual del provider)
    @property
    def SMMLV(self) -> int: return int(self._data["SMMLV"])
    @property
    def AUXILIO_TRANS(self) -> int: return int(self._data["AUXILIO_TRANS"])
    @property
    def TASA_INT_CESANTIAS(self) -> float: return float(self._data["TASA_INT_CESANTIAS"])
    @property
    def TOPE_INDEMNIZACION_SMMLV(self) -> int: return int(self._data["TOPE_INDEMNIZACION_SMMLV"])

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)
```

**Uso esperado desde el motor (`liquidator/core/engine.py`):**
```python
# Liquidación que cruza años (caso canónico 2025-11-16 a 2026-06-09):
provs = ParamsProvider.for_range(inp.contrato.fecha_ingreso, inp.contrato.fecha_corte)
cesantias_2025 = calcular_cesantias(sbl=inp.salario.SBL,
                                    dias=en_segmento_2025,
                                    params=provs[2025])
cesantias_2026 = calcular_cesantias(sbl=inp.salario.SBL,
                                    dias=en_segmento_2026,
                                    params=provs[2026])
total_cesantias = cesantias_2025 + cesantias_2026
```

**Validación:**
```python
def test_params_provider_current_carga_mas_reciente():
    p = ParamsProvider.reload()
    assert p.SMMLV > 0
    # En este momento, el año mayor en params/ debe ser 2026
    assert p.SMMLV == 1750905

def test_params_provider_for_year_explicito():
    p2025 = ParamsProvider.for_year(2025)
    p2026 = ParamsProvider.for_year(2026)
    assert p2025.SMMLV == 1423500
    assert p2026.SMMLV == 1750905
    assert p2025.AUXILIO_TRANS == 200000
    assert p2026.AUXILIO_TRANS == 249095

def test_params_provider_for_date():
    from datetime import date
    p = ParamsProvider.for_date(date(2025, 12, 15))
    assert p.SMMLV == 1423500
    p = ParamsProvider.for_date(date(2026, 3, 15))
    assert p.SMMLV == 1750905

def test_params_provider_for_range_cruza_anio_nuevo():
    from datetime import date
    provs = ParamsProvider.for_range(date(2025, 11, 16), date(2026, 6, 9))
    assert set(provs.keys()) == {2025, 2026}
    assert provs[2025].SMMLV == 1423500
    assert provs[2026].SMMLV == 1750905
```

---

#### Tarea 1.F — Refactor `markdown_generator.py`

**Archivo:** `liquidator/output/markdown_generator.py`

**Cambios:**
1. Corregir `from datetime` → `from datetime import datetime, date`.
2. Validar contexto antes de renderizar.
3. Manejar estados:
   - `compliance_status == "NO_GO"` → plantilla de bloqueo.
   - `compliance_status in ("GO", "WARN", "OVERRIDE_APPROVED")` → plantilla normal con sección de advertencias.
4. No fallar si faltan campos opcionales; usar `data.get("...", default)`.
5. **No incluir nombres/documentos de trabajadores reales en logs de error** (sanitizar).

**Validación:**
```python
def test_markdown_genera_para_canonico():
    out = generate_markdown(case_canonico_result, status="GO")
    # El caso canónico tiene dos segmentos por año, ambos deben verse en el MD
    assert "2025" in out and "2026" in out  # segmentación visible
    assert "por_segmento" in out or "por segmento" in out.lower()  # sub-desglose

def test_markdown_genera_bloqueado():
    out = generate_markdown(case_con_fallo_critical, status="NO_GO")
    assert "BLOQUEADA" in out or "bloqueada" in out.lower()
```

---

#### Tarea 1.G — Refactor `pdf_generator.py`

**Archivo:** `liquidator/output/pdf_generator.py`

**Cambios:**
1. Eliminar código muerto en L151 (el `return template` antes del loop).
2. Si WeasyPrint no está disponible, **devolver error claro**, no generar `.txt` placeholder.
3. Validar header `%PDF-` después de generar.
4. Validar tamaño mínimo (>1 KB).
5. Eliminar `is_text_file = pdf_path.suffix.lower() == '.txt'` en `validate_pdf_output`.

**Validación:**
```python
def test_pdf_no_se_genera_sin_weasyprint(monkeypatch):
    monkeypatch.setattr("WeasyPrint.HTML", None)
    with pytest.raises(RuntimeError, match="WeasyPrint"):
        generate_pdf(...)
```

---

#### Tarea 1.H — Fortalecer `params_validator.py`

**Archivo:** `liquidator/params/params_validator.py`

**Cambios:** Reemplazar `return True` por validación real con `jsonschema` contra `params/2025.schema.json` (a crear).

**Validación:**
```python
def test_params_validator_detecta_smmlv_faltante(tmp_path):
    fake = tmp_path / "2025.json"
    fake.write_text("{}")  # sin SMMLV
    with pytest.raises(ValidationError):
        ParamsValidator().validate(fake)
```

---

#### Tarea 1.I — Test del caso canónico (206d, dos segmentos)

**Archivo:** crear `liquidator/tests/test_canonico/test_caso_canonico_usuario.py` (o `examples/expected/test_canonico.py`).

```python
import json
from pathlib import Path
from datetime import date
from liquidator.core.engine import LiquidacionEngine
from liquidator.core.params_provider import ParamsProvider
from decimal import Decimal

REPO = Path(__file__).resolve().parents[2]

def test_canonico_206d_dos_segmentos():
    """Caso canónico actual: 2025-11-16 a 2026-06-09, dos segmentos por año.

    Verifica que el motor:
    1. Reconoce el cruce de año (segmenta por 1-Ene).
    2. Usa params/2025.json para el segmento 2025 y params/2026.json para el 2026.
    3. Reporta desglose por segmento en el output.
    4. Totaliza correctamente entre los dos segmentos.
    Los valores numéricos exactos se calculan en Fase 2 cuando el motor esté
    completo; este test verifica la ESTRUCTURA y la segmentación, no los valores.
    """
    inp = json.loads((REPO / "examples" / "inputs" / "caso_canonico_periodico_206d.json").read_text())
    provs = ParamsProvider.for_range(
        date.fromisoformat(inp["contrato"]["fecha_ingreso"]),
        date.fromisoformat(inp["contrato"]["fecha_corte"]),
    )
    assert set(provs.keys()) == {2025, 2026}, f"Esperaba años 2025 y 2026, obtuve {set(provs.keys())}"
    engine = LiquidacionEngine(provs=provs)
    result = engine.process_input(inp)
    # Verificar estructura de salida
    assert "desglose" in result
    assert "por_segmento" in result["desglose"], "El desglose debe segmentarse por año"
    assert 2025 in result["desglose"]["por_segmento"]
    assert 2026 in result["desglose"]["por_segmento"]
    # Cesantías esperadas (ver §3, se llenan en Fase 2 con motor)
    cesantias_2025 = Decimal(str(result["desglose"]["por_segmento"]["2025"]["cesantias"]))
    cesantias_2026 = Decimal(str(result["desglose"]["por_segmento"]["2026"]["cesantias"]))
    # 2.200.000 × 46 / 360 ≈ 281.111; 2.200.000 × 160 / 360 ≈ 977.778
    # Aceptamos un margen del 5% hasta que el motor esté afinado en Fase 2.
    assert Decimal("267000") < cesantias_2025 < Decimal("295000"), f"cesantias_2025={cesantias_2025} fuera de rango"
    assert Decimal("929000") < cesantias_2026 < Decimal("1027000"), f"cesantias_2026={cesantias_2026} fuera de rango"
```

**Fixture (anonimizado) en `examples/inputs/caso_canonico_periodico_206d.json`:**
```json
{
  "trabajador": {"nombre": "ANONIMIZADO", "documento": "0"},
  "empleador":  {"nombre": "ANONIMIZADO", "documento": "1"},
  "contrato":   {"fecha_ingreso": "2025-11-16", "fecha_corte": "2026-06-09", "tipo": "INDEFINIDO", "fecha_terminacion_real": null},
  "salario":    {"SBL": 2200000, "auxilio_transporte": false, "variable": false},
  "modo":       "PERIODICA",
  "segmentos": [
    {"anio": 2025, "desde": "2025-11-16", "hasta": "2025-12-31", "params_ref": "params/2025.json"},
    {"anio": 2026, "desde": "2026-01-01", "hasta": "2026-06-09", "params_ref": "params/2026.json"}
  ]
}
```

**Validación:**
```bash
pytest liquidator/tests -q -k canonico
# Esperado: 1+ passed
```

---

#### Tarea 1.J — Cierre de Fase 1

Ejecutar suite completa:
```bash
PYTHONPATH=. uv run --with pytest --with ... pytest liquidator/tests -q
# Esperado: 100% passed, 0 errors
```

Actualizar `Contexto/KB_LLM/09_caso_canonico_usuario.md` con la salida real observada.

---

### 6.3 Riesgos Fase 1

- **R1:** Tests existentes esperan APIs distintas a las que se refactorizan. Mitigación: refactor + actualizar tests en la misma tarea (no dejar tests rotos entre commits).
- **R2:** `pyproject.toml` puede romper instalación en Windows/WSL. Mitigación: probar `pip install -e .` en WSL; documentar diferencia en `README.md` si es relevante.
- **R3:** El motor podría no manejar el caso canónico con la fórmula esperada (SBL × días / 360) por el bug del cap descrito en §3.6. Mitigación: si en este punto el cap de 360 días se activa para casos mayores, **agendar fix en Fase 2** y documentar que el caso canónico (206 días) sí pasa porque 206 < 365. No bloquear Fase 1 por ello.

---

## 7. Fase 2 — Contrato legal y cálculo correcto

> **Objetivo:** Resolver ambigüedades legales con cita explícita, integrar `NormasRepository` y `PlazosManager`, activar `severity→blocking`, e implementar `OVERRIDE_APPROVED`. Cobertura completa con tests golden.

### 7.1 DoD Fase 2

- [ ] **Decisión legal del cap de cesantías documentada** en `Contexto/KB_LLM/01_reglas_calculo.md` con cita (CST art. 253, Ley 50/1990, o jurisprudencia) y adoptada en `params/checklist.json` como regla.
- [ ] Lógica de `calculate_cesantias` corregida para respetar la fórmula legal acordada.
- [ ] `params/checklist.json` con campo `blocking` por regla, derivado de `severity` (CRITICAL/HIGH → True; MEDIUM/LOW/INFO → False).
- [ ] `OVERRIDE_APPROVED` implementado: usuario puede forzar generación pese a fallo HIGH, con `--override --override-reason "..."`, registrado en auditoría.
- [ ] `NormasRepository` y `PlazosManager` invocados en el flujo de cálculo de prestaciones (no solo importados).
- [ ] `LiquidacionEngine` retorna `compliance_status ∈ {"GO", "WARN", "NO_GO", "OVERRIDE_APPROVED"}` y nunca `WARN` (WARN se reemplaza por GO con sección de advertencias, ver diag. §6.4 y nota en §2.4).
- [ ] Tests golden creados y verdes para:
  - [ ] Finca rural periódica (caso histórico `example_finca_rural.json`).
  - [ ] Finiquito sin justa causa (caso histórico `example_finiquito.json`).
  - [ ] Salario variable.
  - [ ] Período parcial.
  - [ ] Año bisiesto (revisar `test_año_bisiesto_completo`).
  - [ ] Período > 360 días.
  - [ ] Auxilio transporte excluido.
  - [ ] Vacaciones en finiquito.
  - [ ] Vacaciones por acuerdo mutuo.
  - [ ] **Caso canónico del usuario (206 días en dos segmentos, SBL=2.200.000, cesantías TBD-motor-Fase2 (ver §3, segmento 2025 + segmento 2026)).**
- [ ] `test_casos_parametrizados[caso1-expected1]` corregido: el test tenía `expected=715.208` pero el motor produce 715.704 que sí coincide con la fórmula documentada; actualizar el expected con justificación en el commit.
- [ ] `SalarioResolver` integrado en el motor (`liquidator/core/salario_resolver.py`): para cada `SegmentoCalculo`, se usa el SBL del año del segmento siguiendo la prioridad 1) `historial_salarial` → promedio del año, 2) `sbl_por_anio[año]`, 3) `SBL` único (compatibilidad).
- [ ] **Caso canónico del usuario (206d, SBL=2.200.000 constante) sigue VERDE con el `SalarioResolver` integrado** — validación de regresión obligatoria: el resultado numérico NO debe cambiar (los tres niveles de prioridad caen al SBL único porque `sbl_por_anio` y `historial_salarial` están vacíos en el input canónico).
- [ ] **Nuevo test golden "SBL variable por año calendario"** verde: input con `sbl_por_anio={2025: 2_200_000, 2026: 2_400_000}` produce cálculos distintos por año (cesantías 2025 ≠ cesantías 2026 escaladas por días).
- [ ] `params/checklist.json` con `severity→blocking` activo por regla, derivado de la nueva regla de anualización (severity MEDIUM, no bloqueante por defecto, ya que un SBL único sigue siendo válido).
- [ ] **`calculate_vacaciones_compensadas_finiquito` implementado en `PrestacionesCalculator`** con fórmula Art. 189 + 190 CST: `(SBL / 30) × dias_pendientes` (SBL sin recargos/HHE, Art. 185). El motor lo invoca **solo** cuando `inp.modo == "FINIQUITO"` y `inp.vacaciones.dias_pendientes > 0`. **Regresión dura:** modo `PERIODICA` **NO** debe invocar este método (las vacaciones compensadas por acuerdo mutuo, Art. 189, son lógica distinta).
- [ ] Caso canónico PERIODICA (sin vacaciones) **sigue verde** (regresión cero: la nueva función no se invoca fuera de FINIQUITO).
- [ ] **Reglas de compliance `V_VACACIONES_FINIQUITO` (severity CRITICAL, blocking)** y `V_VACACIONES_DECLARADAS_FINIQUITO` (severity MEDIUM, no blocking) activas en `params/checklist.json`. La regla CRITICAL bloquea el documento si modo=FINIQUITO, `dias_pendientes > 0` y no hay renglón `vacaciones` en el desglose. La regla MEDIUM emite WARNING si modo=FINIQUITO y `vacaciones is None`.
- [ ] **Test golden "vacaciones en finiquito" ampliado** (`test_vacaciones_finiquito` del diag. §3.13): incluye sub-caso de **renuncia voluntaria** con `dias_pendientes=7.5` (Decimal) que retorna `$550.000` (redondeado HALF_UP). Total liquidación entre $4.400.000 y $4.450.000.
- [ ] Tests nuevos en `liquidator/tests/test_calculators/test_vacaciones_finiquito.py` verdes (4+ tests: caso 7.5 días, caso 0 días, evidencia legal, días negativos son no-input).
- [ ] Suite al 100%.

### 7.2 Tareas Fase 2 (orden sugerido)

#### Tarea 2.A — Decisión legal del cap de cesantías

**Archivos:** `Contexto/KB_LLM/01_reglas_calculo.md` (actualizar), `params/checklist.json` (agregar regla).

**Acción:**
1. Investigar fuente legal en `legal_docs/` y referenciar CST art. 253, Ley 50/1990 art. 99, y/o sentencias de la Corte Constitucional / Corte Suprema relevantes.
2. Documentar en `01_reglas_calculo.md` la decisión adoptada:
   - **Recomendación validada del diagnóstico §3.6:** Si la regla aplicable es `SBL × días trabajados / 360`, **eliminar el cap arbitrario de 360 para períodos mayores**. La fórmula aplica para todos los períodos.
3. Crear/actualizar regla en `params/checklist.json`:
   ```json
   {
     "id": "V_CESANTIAS_FORMULA",
     "description": "Cesantías = round(SBL × días_servicio / 360). Sin cap arbitrario.",
     "severity": "CRITICAL",
     "blocking": true,
     "rule_ref": "CST art. 253, Ley 50/1990 art. 99"
   }
   ```

**Validación:** `Contexto/KB_LLM/01_reglas_calculo.md` contiene la regla con cita y `params/checklist.json` valida con `ParamsValidator` real (Tarea 1.H).

---

#### Tarea 2.B — Corregir lógica de `calculate_cesantias`

**Archivo:** `liquidator/calculators/prestaciones.py`

**Cambio:**
```python
# ANTES (diag. §3.6):
if dias_servicio >= 365 and not self.params.get("USAR_DIAS_REALES", False):
    dias_liquidar = Decimal("360")
else:
    dias_liquidar = Decimal(str(dias_servicio))

# DESPUÉS:
dias_liquidar = Decimal(str(dias_servicio))  # siempre días reales
cesantias = (sbl * dias_liquidar / Decimal("360")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
```

**Validación:**
```python
def test_cesantias_periodo_977_dias():
    # Caso histórico finiquito: 977 días, SBL 2.950.000 → 8.005.972
    calc = PrestacionesCalculator(params={"SMMLV": 1423500, ...})
    r = calc.calculate_cesantias(sbl=2950000, dias_servicio=977)
    assert r == Decimal("8005972")
```

---

#### Tarea 2.B-bis — Calcular prestaciones con SBL del año del segmento *(absorción addendum SL2630-2024)*

>**Origen:** Addendum `addendum_sl2630_y_ipc_2026-06-09.md` §B.2 y Tarea 2.B-bis. Decisión: absorber en v2.0.0 antes del release. **Prereq:** Tarea 1.C-bis cerrada (schema `Salario` extendido). **Cambio central del motor:** el SBL deja de ser un valor único del contrato y pasa a ser **un valor por año calendario** (SL2630-2024: cada año se liquida con el promedio del salario de ESE año). El motor itera segmentos y suma.

**Archivos:**
- Crear `liquidator/core/salario_resolver.py` (nuevo módulo).
- Modificar `liquidator/core/engine.py` (usar `SalarioResolver` en cada segmento).
- Modificar `liquidator/calculators/prestaciones.py` (asegurar que `calculate_cesantias` etc. siguen recibiendo `sbl: Decimal` por segmento, sin cambios de firma).
- Crear `liquidator/tests/test_core/test_salario_resolver.py`.
- Crear `liquidator/tests/test_golden/test_salario_variable_por_anio.py`.
- Actualizar `Contexto/KB_LLM/01_reglas_calculo.md` (sección "Anualización salarial SL2630-2024").

**Diseño del `SalarioResolver`:**

```python
# liquidator/core/salario_resolver.py
from decimal import Decimal
from datetime import date

from liquidator.contracts.input_model import Salario

class SegmentoCalculo:
    """Sub-rango de un contrato que cae dentro de un único año calendario."""
    anio: int
    desde: date
    hasta: date
    sbl: Decimal
    dias: int

class SalarioResolver:
    """Selecciona el SBL correcto para un segmento de cálculo.

    Prioridad:
      1) historial_salarial → promedio del año del segmento
      2) sbl_por_anio[año del segmento]
      3) SBL único (compatibilidad con v1.x)
    """

    def __init__(self, salario: Salario):
        self.salario = salario

    def sbl_para_segmento(self, segmento: SegmentoCalculo) -> Decimal:
        # Prioridad 1: historial mensual → promedio del año del segmento
        if self.salario.historial_salarial:
            meses_del_anio = [
                m for m in self.salario.historial_salarial
                if m.año == segmento.anio
            ]
            if meses_del_anio:
                total = sum(m.valor for m in meses_del_anio)
                return (total / Decimal(len(meses_del_anio))).quantize(Decimal("1"))
        # Prioridad 2: SBL explícito por año
        if self.salario.sbl_por_anio and segmento.anio in self.salario.sbl_por_anio:
            return self.salario.sbl_por_anio[segmento.anio]
        # Prioridad 3: SBL único (compatibilidad)
        return self.salario.SBL
```

**Integración en el motor (`liquidator/core/engine.py`):**

```python
# ANTES (Tarea 2.B vigente, SBL único):
def calcular_prestaciones(self, inp, provs):
    for segmento in self._segmentar(inp):
        cesantias = calculate_cesantias(
            sbl=inp.salario.SBL,    # ← mismo SBL para todos los años
            dias=segmento.dias,
            params=provs[segmento.anio],
        )
        ...

# DESPUÉS (Tarea 2.B-bis, SBL por año):
def calcular_prestaciones(self, inp, provs):
    resolver = SalarioResolver(inp.salario)
    for segmento in self._segmentar(inp):
        sbl_del_anio = resolver.sbl_para_segmento(segmento)
        cesantias = calculate_cesantias(
            sbl=sbl_del_anio,        # ← SBL del año del segmento (SL2630-2024)
            dias=segmento.dias,
            params=provs[segmento.anio],
        )
        ...
```

**Validación (DoD Fase 2):**

```python
# tests/test_core/test_salario_resolver.py
from decimal import Decimal
from datetime import date
from liquidator.contracts.input_model import Salario, MesValor
from liquidator.core.salario_resolver import SalarioResolver, SegmentoCalculo

def _seg(anio, dias):
    return SegmentoCalculo(
        anio=anio,
        desde=date(anio, 1, 1),
        hasta=date(anio, 12, 31),
        sbl=Decimal("0"),
        dias=dias,
    )

def test_prioridad_3_sbl_unico_compatibilidad():
    s = Salario(SBL=Decimal("2200000"))
    r = SalarioResolver(s)
    assert r.sbl_para_segmento(_seg(2025, 46)) == Decimal("2200000")
    assert r.sbl_para_segmento(_seg(2026, 160)) == Decimal("2200000")

def test_prioridad_2_sbl_por_anio():
    s = Salario(
        SBL=Decimal("2200000"),
        sbl_por_anio={2025: Decimal("2200000"), 2026: Decimal("2400000")},
    )
    r = SalarioResolver(s)
    assert r.sbl_para_segmento(_seg(2025, 46)) == Decimal("2200000")
    assert r.sbl_para_segmento(_seg(2026, 160)) == Decimal("2400000")

def test_prioridad_1_historial_salarial_promedio_anual():
    s = Salario(
        SBL=Decimal("2200000"),
        historial_salarial=[
            MesValor(año=2025, mes=11, valor=Decimal("2100000")),
            MesValor(año=2025, mes=12, valor=Decimal("2300000")),
            MesValor(año=2026, mes=1,  valor=Decimal("2400000")),
        ],
    )
    r = SalarioResolver(s)
    # 2025: promedio (2.100.000 + 2.300.000) / 2 = 2.200.000
    assert r.sbl_para_segmento(_seg(2025, 46)) == Decimal("2200000")
    # 2026: solo enero → 2.400.000
    assert r.sbl_para_segmento(_seg(2026, 160)) == Decimal("2400000")

def test_historial_sin_meses_para_anio_cae_a_sbl_por_anio():
    """Si el historial no tiene meses del año, cae al siguiente nivel."""
    s = Salario(
        SBL=Decimal("2200000"),
        sbl_por_anio={2026: Decimal("2400000")},
        historial_salarial=[MesValor(año=2025, mes=6, valor=Decimal("2300000"))],
    )
    r = SalarioResolver(s)
    assert r.sbl_para_segmento(_seg(2026, 160)) == Decimal("2400000")
```

**Test golden de regresión obligatorio (caso canónico NO cambia):**

```python
# tests/test_golden/test_canonico_periodico_206d.py (modificar el existente)
def test_canonico_sin_campos_nuevos_sigue_verde():
    """El caso canónico del plan (SBL único 2.200.000) NO debe cambiar su
    resultado numérico al integrar el SalarioResolver, porque el resolver
    cae al nivel 3 (SBL único) por compatibilidad."""
    inp = json.loads((REPO / "examples" / "inputs" /
                      "caso_canonico_periodico_206d.json").read_text())
    provs = ParamsProvider.for_range(
        date.fromisoformat(inp["contrato"]["fecha_ingreso"]),
        date.fromisoformat(inp["contrato"]["fecha_corte"]),
    )
    engine = LiquidacionEngine(provs=provs)
    result = engine.process_input(inp)
    # Cesantías 2025 (46d) y 2026 (160d) con SBL=2.200.000: ver §3 del plan
    assert Decimal(str(result["desglose"]["por_segmento"]["2025"]["cesantias"])) == Decimal("281111")
    assert Decimal(str(result["desglose"]["por_segmento"]["2026"]["cesantias"])) == Decimal("977778")
```

**Test golden nuevo (SBL variable por año):**

```python
# tests/test_golden/test_salario_variable_por_anio.py
def test_sbl_variable_2025_a_2026_produce_calculos_distintos():
    """Caso nuevo: SBL cambia de 2.200.000 (2025) a 2.400.000 (2026)."""
    inp = json.loads((REPO / "examples" / "inputs" /
                      "caso_canonico_periodico_206d.json").read_text())
    inp["salario"]["sbl_por_anio"] = {
        "2025": 2200000,
        "2026": 2400000,
    }
    provs = ParamsProvider.for_range(
        date.fromisoformat(inp["contrato"]["fecha_ingreso"]),
        date.fromisoformat(inp["contrato"]["fecha_corte"]),
    )
    engine = LiquidacionEngine(provs=provs)
    result = engine.process_input(inp)
    # 2025: 2.200.000 × 46 / 360 = 281.111
    assert Decimal(str(result["desglose"]["por_segmento"]["2025"]["cesantias"])) == Decimal("281111")
    # 2026: 2.400.000 × 160 / 360 = 1.066.667 (distinto del caso canónico)
    assert Decimal(str(result["desglose"]["por_segmento"]["2026"]["cesantias"])) == Decimal("1066667")
```

**Riesgos específicos:**
- **R1:** El cambio de contrato del `engine` puede romper tests existentes. Mitigación: el test de regresión `test_canonico_sin_campos_nuevos_sigue_verde` es la red de seguridad; cualquier desviación de los valores numéricos del caso canónico significa regresión.
- **R2:** `SalarioResolver` malgasta el SBL único si se invoca con un input que no tiene los campos nuevos. Mitigación: la prioridad 3 (fallback) está implementada explícitamente y probada con `test_prioridad_3_sbl_unico_compatibilidad`.
- **R3:** `MesValor` con `mes` decimal o futuro podría distorsionar el promedio. Mitigación: validación Pydantic en Tarea 1.C-bis (`mes: int = Field(ge=1, le=12)`) + tests en `test_mesvalor_valida_rango_mes`.

---

#### Tarea 2.B-ter — `calculate_vacaciones_compensadas_finiquito` en `PrestacionesCalculator` *(absorción addendum finiquito/vacaciones 2026-06-11)*

>**Origen:** Addendum `addendum_finiquito_renuncia_vacaciones_2026-06-11.md` §B.5 y Tarea 2.B-ter. Decisión 2026-06-11: absorber en v2.0.0 antes del release. **Prereq:** Tarea 1.C-ter cerrada (schema con `motivo_terminacion` + `VacacionesEstado` tipado). **Cambio central del motor:** cuando `inp.modo == "FINIQUITO"` y `inp.vacaciones.dias_pendientes > 0`, el motor añade un renglón al desglose con la fórmula del Art. 189 párr. 1° + Art. 190 CST: `vacaciones_compensadas = (SBL / 30) × dias_pendientes`, redondeado al peso con `ROUND_HALF_UP`. El SBL para vacaciones NO incluye recargos ni horas extras (Art. 185) y NO incluye auxilio de transporte.

**Archivos:**
- Modificar `liquidator/calculators/prestaciones.py` (agregar método `calculate_vacaciones_compensadas_finiquito` en `PrestacionesCalculator`).
- Modificar `liquidator/core/engine.py` (agregar método privado `_calcular_vacaciones_si_finiquito` que invoca el anterior solo si `modo == "FINIQUITO"`).
- Crear `liquidator/tests/test_calculators/test_vacaciones_finiquito.py` (4+ tests).
- Crear `examples/inputs/finiquito_renuncia_212d.json` + `examples/expected/finiquito_renuncia_212d_result.json` (caso golden del addendum §G: SBL 2.200.000, 7.5 días, total ~$4.427.014).
- Crear `liquidator/tests/test_golden/test_finiquito_renuncia_212d.py`.
- Actualizar `Contexto/KB_LLM/01_reglas_calculo.md` (sección "Vacaciones compensadas obligatorias en finiquito" — Art. 189 + 190).

**Diseño del método en `PrestacionesCalculator`:**

```python
# liquidator/calculators/prestaciones.py
from decimal import Decimal, ROUND_HALF_UP

def calculate_vacaciones_compensadas_finiquito(
    self,
    sbl: Decimal,
    dias_pendientes: Decimal,
    params: ParamsProvider = None,
) -> dict:
    """Vacaciones no disfrutadas pagadas obligatoriamente en finiquito.

    Base legal: Art. 189 párr. 1° + Art. 190 CST.
    Fórmula: (SBL / 30) × dias_pendientes.
    El SBL para vacaciones excluye recargos, horas extras (Art. 185) y
    auxilio de transporte. Fracciones de día son legalmente válidas.

    Esta función SOLO se invoca desde el motor cuando modo == "FINIQUITO".
    El modo PERIODICA NO la invoca: las vacaciones por acuerdo mutuo
    (Art. 189, periodo vigente) son lógica distinta.
    """
    valor = (sbl / Decimal(30) * dias_pendientes).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    evidencia = self.normas_repo.cita("vacaciones_finiquito", "Art. 189-190 CST")
    return {
        "concepto": "Vacaciones compensadas (finiquito)",
        "valor": valor,
        "dias": dias_pendientes,
        "formula": "SBL / 30 × días_pendientes",
        "evidencia_legal": evidencia,
        "obligatorio_en_finiquito": True,
        "params_usados": {"SBL": sbl, "dias_pendientes": dias_pendientes},
    }
```

**Integración en el motor (`liquidator/core/engine.py`):**

```python
def _calcular_vacaciones_si_finiquito(self, inp, renglones):
    """Hook de vacaciones compensadas en finiquito (Tarea 2.B-ter).
    Idempotente: si no aplica (modo PERIODICA, sin vacaciones, dias=0),
    no añade nada al desglose. Si aplica, añade un único renglón.
    """
    if inp.modo != "FINIQUITO":
        return  # Regresión dura: PERIODICA NO paga vacaciones compensadas
    if inp.vacaciones is None:
        return  # regla V_VACACIONES_DECLARADAS_FINIQUITO (MEDIUM) lo advertirá
    if inp.vacaciones.dias_pendientes <= 0:
        logger.info("Finiquito sin vacaciones pendientes; nada que pagar")
        return
    renglon = self.prestaciones.calculate_vacaciones_compensadas_finiquito(
        sbl=inp.salario.SBL,   # para vacaciones NO suma auxilio_trans ni recargos
        dias_pendientes=inp.vacaciones.dias_pendientes,
    )
    renglones.append(renglon)
```

**Caso golden propuesto (del addendum §G, adaptado al caso canónico 2025-11-16 → 2026-06-15, 212 días):**

**Input:** `examples/inputs/finiquito_renuncia_212d.json`

```json
{
  "trabajador": {"nombre": "ANONIMIZADO", "documento": "0"},
  "empleador":  {"nombre": "ANONIMIZADO", "documento": "1"},
  "contrato":   {
    "fecha_ingreso": "2025-11-16",
    "fecha_corte":   "2026-06-15",
    "tipo": "INDEFINIDO",
    "fecha_terminacion_real": "2026-06-15",
    "motivo_terminacion": "renuncia_voluntaria"
  },
  "salario":    {
    "SBL": 2200000,
    "auxilio_transporte": false,
    "variable": false
  },
  "modo":       "FINIQUITO",
  "vacaciones": {
    "dias_pendientes": 7.5,
    "dias_disfrutados": 0
  },
  "segmentos": [
    {"anio": 2025, "desde": "2025-11-16", "hasta": "2025-12-31"},
    {"anio": 2026, "desde": "2026-01-01", "hasta": "2026-06-15"}
  ]
}
```

**Output esperado (valores clave por renglón):**

| Concepto | Valor | Días | Fórmula | Artículo |
|----------|-------|------|---------|----------|
| Cesantías seg. 2025 | $281.111 | 46 | 2.200.000 × 46 / 360 | Art. 249 CST |
| Cesantías seg. 2026 | $1.014.444 | 166 | 2.200.000 × 166 / 360 | Art. 249 CST |
| **Total cesantías** | **$1.295.555** | 212 | suma segmentos | — |
| Intereses sobre cesantías 2025 | $8.433 | 46 | 281.111 × 12% × 46/360 | Art. 99 Ley 50/1990 |
| Intereses sobre cesantías 2026 | $56.360 | 166 | 1.014.444 × 12% × 166/360 | Art. 99 Ley 50/1990 |
| Prima seg. H2-2025 | $281.111 | 46 | 2.200.000 × 46/360 | Art. 306 CST |
| Prima seg. H1-2026 | $1.014.444 | 166 | 2.200.000 × 166/360 | Art. 306 CST |
| **Vacaciones compensadas** | **$550.000** | **7.5** | **2.200.000 / 30 × 7.5** | **Art. 189-190 CST** |
| Indemnización | **N/A** | — | Renuncia voluntaria (Art. 49 num. 6, sin Art. 64) | — |
| **TOTAL LIQUIDACIÓN** | **~$4.427.014** | — | — | — |

**Validación (DoD Fase 2):**

```python
# liquidator/tests/test_calculators/test_vacaciones_finiquito.py
from decimal import Decimal
from liquidator.calculators.prestaciones import PrestacionesCalculator

def test_vacaciones_7_5_dias_sbl_2_200_000():
    """Caso real del addendum: 7.5 días de vacaciones, SBL 2.200.000."""
    calc = PrestacionesCalculator(params={...})
    r = calc.calculate_vacaciones_compensadas_finiquito(
        sbl=Decimal("2200000"), dias_pendientes=Decimal("7.5")
    )
    # (2.200.000 / 30) × 7.5 = 550.000
    assert r["valor"] == Decimal("550000")
    assert "Art. 189" in r["evidencia_legal"]
    assert r["obligatorio_en_finiquito"] is True
    assert r["dias"] == Decimal("7.5")

def test_vacaciones_cero_dias_retorna_cero():
    """dias_pendientes=0: el motor no debe invocar; si se invoca, retorna 0."""
    calc = PrestacionesCalculator(params={...})
    r = calc.calculate_vacaciones_compensadas_finiquito(
        sbl=Decimal("2200000"), dias_pendientes=Decimal("0")
    )
    assert r["valor"] == Decimal("0")

def test_vacaciones_dia_entero_sbl_1_750_905():
    """Sanity check: 1 día con SMMLV 2026."""
    calc = PrestacionesCalculator(params={...})
    r = calc.calculate_vacaciones_compensadas_finiquito(
        sbl=Decimal("1750905"), dias_pendientes=Decimal("1")
    )
    # 1.750.905 / 30 = 58.363.5 → redondeado HALF_UP a 58.364
    assert r["valor"] == Decimal("58364")

def test_vacaciones_no_incluye_auxilio_transporte():
    """El SBL del input no debe sumar auxilio_transporte.
    Aquí validamos que la función recibe SOLO el SBL como parámetro
    y que el motor NO le pasa un valor compuesto. La garantía de
    cumplimiento es por convención en engine._calcular_vacaciones_si_finiquito
    (que pasa inp.salario.SBL, NO un valor con aux_trans sumado)."""
    # Test de cobertura: el método recibe un solo Decimal `sbl` y un Decimal `dias_pendientes`.
    # No hay parámetros 'auxilio_transporte' ni 'recargo'.
    import inspect
    sig = inspect.signature(
        PrestacionesCalculator.calculate_vacaciones_compensadas_finiquito
    )
    assert "sbl" in sig.parameters
    assert "dias_pendientes" in sig.parameters
    assert "auxilio_transporte" not in sig.parameters
    assert "recargo" not in sig.parameters
```

```python
# liquidator/tests/test_golden/test_finiquito_renuncia_212d.py
import json
from decimal import Decimal
from datetime import date
from pathlib import Path

from liquidator.core.engine import LiquidacionEngine
from liquidator.core.params_provider import ParamsProvider

REPO = Path(__file__).resolve().parents[3]

def test_finiquito_renuncia_212d_total_y_vacaciones():
    """Caso golden del addendum §G: renuncia voluntaria con 7.5 días de
    vacaciones pendientes, SBL 2.200.000, 212 días (2025-11-16 → 2026-06-15)."""
    inp = json.loads((REPO / "examples" / "inputs" /
                      "finiquito_renuncia_212d.json").read_text())
    provs = ParamsProvider.for_range(
        date.fromisoformat(inp["contrato"]["fecha_ingreso"]),
        date.fromisoformat(inp["contrato"]["fecha_corte"]),
    )
    engine = LiquidacionEngine(provs=provs)
    result = engine.process_input(inp)

    # Compliance GO o WARN (indemnización N/A no es violación)
    assert result["compliance"]["status"] in ("GO", "WARN", "OVERRIDE_APPROVED")

    # Indemnización: NO debe aparecer como renglón positivo
    assert (
        "indemnizacion" not in result["desglose"]
        or result["desglose"]["indemnizacion"]["valor"] == Decimal("0")
    )

    # Vacaciones compensadas: valor exacto 550.000
    assert result["desglose"]["vacaciones"]["valor"] == Decimal("550000")
    assert result["desglose"]["vacaciones"]["dias"] == Decimal("7.5")

    # Total: entre 4.400.000 y 4.450.000 (sanity check)
    total = Decimal(str(result["total_liquidacion"]))
    assert Decimal("4400000") < total < Decimal("4450000")
```

**Regresión dura (no romper Fase 1 ni Tarea 2.B-bis):**

```python
# En test_canonico_periodico_206d.py: el caso canónico PERIODICA
# (sin vacaciones, sin motivo_terminacion) NO debe generar renglón
# de vacaciones compensadas. Test de cobertura que verifica el camino
# "modo PERIODICA → no se invoca calculate_vacaciones_compensadas_finiquito".
def test_canonico_periodico_no_paga_vacaciones_finiquito():
    inp = json.loads((REPO / "examples" / "inputs" /
                      "caso_canonico_periodico_206d.json").read_text())
    assert inp["modo"] == "PERIODICA"
    # No hay vacaciones en el input canónico
    assert "vacaciones" not in inp or inp["vacaciones"] is None
    provs = ParamsProvider.for_range(
        date.fromisoformat(inp["contrato"]["fecha_ingreso"]),
        date.fromisoformat(inp["contrato"]["fecha_corte"]),
    )
    engine = LiquidacionEngine(provs=provs)
    result = engine.process_input(inp)
    # El desglose NO debe contener "vacaciones" como renglón de finiquito
    assert "vacaciones" not in result["desglose"]
    # Total idéntico al del caso canónico (regresión cero)
```

```bash
# Suite completa Fase 2
PYTHONPATH=. pytest liquidator/tests -q
# Esperado: 100% passed, 0 errors
```

**No-DoD hasta ejecutar Tarea 2.B-ter:** el motor NO pagará vacaciones compensadas en finiquito. Si se intenta liquidar un finiquito, el desglose saldrá sin renglón de vacaciones; la regla `V_VACACIONES_FINIQUITO` (Tarea 2.Z) detectará la falta y bloqueará con CRITICAL. Esto ya es detectable por compliance; la tarea 2.B-ter es lo que **soluciona** el bloqueo. La auditoría inmutable (Fase 3) NO se afecta, pero el sistema queda **parcialmente incapaz** de liquidar finiquitos con vacaciones hasta cerrar Tarea 2.B-ter.

**Riesgos específicos:**
- **R1:** Confundir SBL de vacaciones con SBL de cesantías/prima. Las cesantías y prima incluyen auxilio de transporte (sub_sidio), pero las vacaciones Art. 189 + 190 NO. Mitigación: test `test_vacaciones_no_incluye_auxilio_transporte` que verifica por convención (el método solo recibe `sbl: Decimal` sin aux_trans; el motor le pasa `inp.salario.SBL` y nunca un valor compuesto).
- **R2:** Cambiar `dias_pendientes` de `int` a `Decimal` puede causar `TypeError` en código de cálculo que aún espera `int`. Mitigación: `VacacionesEstado` se define con `Decimal` desde Tarea 1.C-ter; los métodos que reciben días pendientes deben declararse `dias_pendientes: Decimal` explícitamente.
- **R3:** El motor puede invocar `calculate_vacaciones_compensadas_finiquito` en modo PERIODICA por error (regresión). Mitigación: guard explícito en `engine._calcular_vacaciones_si_finiquito` (`if inp.modo != "FINIQUITO": return`) + test de regresión `test_canonico_periodico_no_paga_vacaciones_finiquito`.
- **R4:** Fracción 7.5 días puede no ser aceptada por motores que asumen días enteros. Mitigación: `ROUND_HALF_UP` explícito en todos los métodos que reciben `dias_pendientes: Decimal`; tests con valores fraccionarios (7.5, 0.5) para confirmar redondeo correcto.
- **R5:** Verificación verbatim del Art. 189 CST no hecha antes de implementar. Mitigación: antes de cerrar Tarea 2.B-ter, descargar texto del Art. 189 (especialmente párr. 1°) desde https://www.suin-juriscol.gov.co/ y registrar `estado_verificacion: "VERIFICADO"` con URL y fecha de captura en `params/normas.json` (entrada `CST_189_VACACIONES`).

---

#### Tarea 2.Z — Reglas de compliance `V_VACACIONES_FINIQUITO` y `V_VACACIONES_DECLARADAS_FINIQUITO` *(absorción addendum finiquito/vacaciones 2026-06-11)*

>**Origen:** Addendum `addendum_finiquito_renuncia_vacaciones_2026-06-11.md` §C Tarea 2.Z. Decisión 2026-06-11: absorber en v2.0.0 antes del release. **Prereq:** Tarea 2.B-ter cerrada (método `calculate_vacaciones_compensadas_finiquito` integrado). **Propósito:** cerrar el loop de compliance: si el motor ya calculó las vacaciones correctamente, la regla CRITICAL pasa; si no las calculó, la regla bloquea. La regla MEDIUM advierte cuando el usuario olvidó declarar vacaciones en finiquito (compliance no puede inventar el dato).

**Archivos:**
- Modificar `params/checklist.json` (agregar entradas `V_VACACIONES_FINIQUITO` y `V_VACACIONES_DECLARADAS_FINIQUITO`).
- Modificar `liquidator/compliance/compliance_engine.py` (evaluar ambas reglas con la lógica del addendum).
- Crear `liquidator/tests/test_compliance/test_vacaciones_finiquito_compliance.py` (cubrir CRITICAL, MEDIUM, N/A).
- Actualizar `Contexto/KB_LLM/03_compliance_blocking.md` (documentar las 2 reglas nuevas).

**Reglas en `params/checklist.json`:**

```json
{
  "id": "V_VACACIONES_FINIQUITO",
  "description": "En finiquito, si hay vacaciones pendientes causadas, deben pagarse obligatoriamente (Art. 189-190 CST). La ausencia del renglón 'vacaciones' en el desglose cuando vacaciones.dias_pendientes > 0 es fallo CRITICAL.",
  "severity": "CRITICAL",
  "blocking": true,
  "rule_ref": "Art. 189-190 CST",
  "formula": "SBL / 30 × días_pendientes",
  "aplica_si": "modo == FINIQUITO AND vacaciones.dias_pendientes > 0",
  "excepcion": "Si vacaciones.dias_pendientes == 0 (todas disfrutadas), regla N/A"
},
{
  "id": "V_VACACIONES_DECLARADAS_FINIQUITO",
  "description": "En FINIQUITO se RECOMIENDA declarar vacaciones.dias_pendientes. Si no se declara (vacaciones is None), se emite WARNING (severidad MEDIUM). Si dias_pendientes == 0, NO se advierte (declaración válida de que todas se disfrutaron).",
  "severity": "MEDIUM",
  "blocking": false,
  "rule_ref": "Art. 186 CST (causación)",
  "aplica_si": "modo == FINIQUITO AND vacaciones IS NULL"
}
```

**Lógica de evaluación en `compliance_engine.py`:**

```python
# Pseudocódigo de la evaluación (extender ComplianceEngine existente)
def _evaluar_v_vacaciones_finiquito(self, input_dict, desglose, result):
    if input_dict["modo"] != "FINIQUITO":
        return None  # regla N/A
    vacaciones = input_dict.get("vacaciones")
    dias_pendientes = Decimal(0)
    if vacaciones is not None:
        dias_pendientes = Decimal(str(vacaciones.get("dias_pendientes", 0)))
    if dias_pendientes == 0:
        return None  # exención documentada
    # CRITICAL: dias_pendientes > 0 pero no hay renglón "vacaciones"
    if "vacaciones" not in desglose or Decimal(str(desglose["vacaciones"]["valor"])) == 0:
        return {
            "rule_id": "V_VACACIONES_FINIQUITO",
            "severity": "CRITICAL",
            "blocking": True,
            "message": (
                f"FINIQUITO con vacaciones.dias_pendientes={dias_pendientes} "
                f"sin renglón 'vacaciones' en el desglose. "
                f"Art. 189-190 CST exige pago obligatorio."
            ),
        }
    return None  # OK

def _evaluar_v_vacaciones_declaradas_finiquito(self, input_dict, desglose, result):
    if input_dict["modo"] != "FINIQUITO":
        return None
    if input_dict.get("vacaciones") is None:
        return {
            "rule_id": "V_VACACIONES_DECLARADAS_FINIQUITO",
            "severity": "MEDIUM",
            "blocking": False,
            "message": (
                "FINIQUITO sin vacaciones declaradas. "
                "Si hubo vacaciones pendientes, declararlas en input.vacaciones.dias_pendientes. "
                "Si todas se disfrutaron, declarar dias_pendientes=0 explícitamente."
            ),
        }
    return None
```

**Validación (DoD Fase 2):**

```python
# liquidator/tests/test_compliance/test_vacaciones_finiquito_compliance.py
import pytest
from liquidator.compliance.compliance_engine import ComplianceEngine

@pytest.fixture
def engine(checklist):
    return ComplianceEngine(checklist, evaluators={...})

def test_finiquito_con_vacaciones_y_renglon_pasa(engine, inp_renuncia_7_5):
    """Camino feliz: el motor calculó vacaciones, la regla CRITICAL pasa."""
    result = engine.evaluate(inp_renuncia_7_5, desglose_con_vacaciones_550k)
    failures = [f for f in result["failures"] if f["rule_id"] == "V_VACACIONES_FINIQUITO"]
    assert failures == []  # sin fallos CRITICAL
    assert result["status"] in ("GO", "WARN", "OVERRIDE_APPROVED")

def test_finiquito_con_vacaciones_sin_renglon_bloquea(engine, inp_renuncia_7_5):
    """Camino de fallo: el motor NO calculó vacaciones (regresión 2.B-ter)."""
    result = engine.evaluate(inp_renuncia_7_5, desglose_sin_vacaciones)
    failures = [f for f in result["failures"] if f["rule_id"] == "V_VACACIONES_FINIQUITO"]
    assert len(failures) == 1
    assert failures[0]["severity"] == "CRITICAL"
    assert failures[0]["blocking"] is True
    assert result["status"] == "NO_GO"

def test_finiquito_sin_vacaciones_declaradas_emite_warning(engine, inp_renuncia_sin_vacaciones):
    """MEDIUM: el usuario olvidó declarar vacaciones."""
    result = engine.evaluate(inp_renuncia_sin_vacaciones, desglose_basico)
    warnings = [w for w in result["warnings"] if w["rule_id"] == "V_VACACIONES_DECLARADAS_FINIQUITO"]
    assert len(warnings) == 1
    assert warnings[0]["severity"] == "MEDIUM"
    assert warnings[0]["blocking"] is False
    # status sigue GO o WARN (no bloqueante)
    assert result["status"] in ("GO", "WARN", "OVERRIDE_APPROVED")

def test_finiquito_vacaciones_cero_no_aplica_ninguna_regla(engine, inp_renuncia_vacaciones_cero):
    """dias_pendientes=0: ambas reglas N/A (todas disfrutadas)."""
    result = engine.evaluate(inp_renuncia_vacaciones_cero, desglose_sin_vacaciones)
    failures = [f for f in result["failures"] if "VACACIONES_FINIQUITO" in f["rule_id"]]
    warnings = [w for w in result["warnings"] if "VACACIONES_FINIQUITO" in w["rule_id"]]
    assert failures == []
    assert warnings == []

def test_periodica_no_evalua_reglas_finiquito(engine, inp_canonico_periodico):
    """Regresión dura: PERIODICA no debe evaluar reglas de finiquito."""
    result = engine.evaluate(inp_canonico_periodico, desglose_canonico)
    failures = [f for f in result["failures"] if "VACACIONES_FINIQUITO" in f["rule_id"]]
    warnings = [w for w in result["warnings"] if "VACACIONES_FINIQUITO" in w["rule_id"]]
    assert failures == []
    assert warnings == []
```

```bash
# Suite completa Fase 2
PYTHONPATH=. pytest liquidator/tests -q
# Esperado: 100% passed, 0 errors (5+ tests nuevos de compliance)
```

**Riesgos específicos:**
- **R1:** Las reglas de compliance asumen que `desglose["vacaciones"]` es la convención del motor. Si la convención cambia (ej. `desglose["vacaciones_finiquito"]`), las reglas no detectan el renglón. Mitigación: la regla busca tanto `desglose["vacaciones"]` como `desglose["vacaciones_finiquito"]` (defensa en profundidad); agregar test que verifique el contrato del nombre de la clave.
- **R2:** El usuario podría declarar `dias_pendientes: 0` y `dias_disfrutados: 0` con `dias_causados_proporcionales: 0` — caso edge donde ambas reglas aplican como N/A. Mitigación: la condición `dias_pendientes == 0` está explícita en `_evaluar_v_vacaciones_finiquito` y en `_evaluar_v_vacaciones_declaradas_finiquito` (si dias_pendientes == 0, no es N/A; si vacaciones is None, sí es WARNING).
- **R3:** La regla MEDIUM puede ser ruidosa si el usuario legítimamente no tiene vacaciones que pagar (ej. contrato < 1 año, sin días causados). Mitigación: la regla se aplica **solo** en modo FINIQUITO. Si el usuario no quiere el warning, puede declarar `vacaciones: {dias_pendientes: 0, dias_disfrutados: 0, dias_causados_proporcionales: 0}` explícitamente. Documentar en `Contexto/KB_LLM/04_schema_entrada.md`.

---

#### Tarea 2.C — `severity → blocking` en `params/checklist.json`

**Archivos:** `params/checklist.json` (modificar), `liquidator/compliance/compliance_engine.py` (verificar uso).

**Cambios:**
1. Agregar campo `blocking` a cada regla del checklist, derivado de `severity`:
   ```json
   {"id": "V001", "severity": "CRITICAL", "blocking": true,  ...}
   {"id": "V004", "severity": "HIGH",     "blocking": true,  ...}
   {"id": "V010", "severity": "MEDIUM",   "blocking": false, ...}
   ```
2. Verificar en `compliance_engine.py` que el campo se lee correctamente:
   ```python
   blocking = rule_info.get("blocking", rule_info.get("severity") in ("CRITICAL", "HIGH"))
   ```
3. **Eliminar el estado `WARN` del output** (mantener `GO` con sección de advertencias). Actualizar tests que esperan `WARN`.

**Validación:**
```python
def test_compliance_bloquea_critical():
    e = ComplianceEngine(checklist, evaluators)
    out = e.evaluate(input_con_fallo_critical)
    assert out["status"] == "NO_GO"
    assert out["blocking_failures"]

def test_compliance_override_aprobado():
    e = ComplianceEngine(checklist, evaluators)
    out = e.evaluate(input_con_fallo_high, override=True, override_reason="justificacion X")
    assert out["status"] == "OVERRIDE_APPROVED"
    assert out["override"]["reason"] == "justificacion X"
```

---

#### Tarea 2.D — `OVERRIDE_APPROVED` end-to-end

**Archivos:** `liquidator/cli/main.py` (verificar opciones), `liquidator/core/engine.py` (firmar override), `liquidator/audit/` (registrar).

**Comportamiento esperado:**
```bash
python -m liquidator.cli liquidar input.json --override --override-reason "Casos validados con MinTrabajo 2026-XX-XX"
# Estado: OVERRIDE_APPROVED, exit code 0, JSON con campo "override": {"reason": "...", "timestamp": "...", "user": "Jhond"}
```

**Validación:**
- Audit log contiene la entrada de override.
- Documento generado lleva sello visible: "GENERADO CON OVERRIDE — HIGH: <id_regla> — JUSTIFICACIÓN: <texto>".

---

#### Tarea 2.E — Integrar `NormasRepository` y `PlazosManager`

**Archivos:** `liquidator/legal/normas_repository.py`, `liquidator/legal/plazos_manager.py`, `liquidator/calculators/prestaciones.py`.

**Cambios:**
1. En `PrestacionesCalculator.__init__`, instanciar `NormasRepository(params)` y `PlazosManager(params)`.
2. En cada método (`calculate_cesantias`, `calculate_prima`, `calculate_intereses_cesantias`, `calculate_vacaciones`), agregar prefijo de evidencia legal:
   ```python
   evidencia = self.normas_repo.cita("cesantias", "CST art. 253")
   result["evidencia_legal"] = evidencia
   ```
3. `PlazosManager` se usa para validar fechas límite (ej.: prescripción de prestaciones).

**Validación:** Cada cálculo retorna `evidencia_legal` y los tests verifican que el ID de la norma citada existe en `legal_docs/`.

---

#### Tarea 2.F — Tests golden (10 casos)

**Directorio:** `liquidator/tests/test_golden/`

Crear un test por caso, cada uno con:
- Input fixture en `examples/inputs/<caso>.json` (anonimizado).
- Output esperado en `examples/expected/<caso>_result.json` (valores clave: cesantías, prima, intereses, total, compliance_status).

Casos (de diag. §3.13):
1. `test_canonico_periodico_206d` — caso del usuario (dos segmentos 2025-H2 + 2026-H1).
2. `test_finca_rural_periodica` — ejemplo histórico.
3. `test_finiquito_sin_justa_causa` — ejemplo histórico.
4. `test_salario_variable` — salario promedio últimos 6 meses.
5. `test_periodo_parcial` — < 30 días.
6. `test_año_bisiesto` — período incluye 29-Feb.
7. `test_periodo_mayor_360d` — > 1 año.
8. `test_auxilio_excluido` — SBL > 2 SMMLV, no aplica auxilio.
9. `test_vacaciones_finiquito` — finiquito con vacaciones pendientes.
10. `test_vacaciones_acuerdo_mutuo` — disfrute anticipado.

**Validación:**
```bash
pytest liquidator/tests/test_golden -v
# Esperado: 10 passed
```

---

#### Tarea 2.G — Corregir `test_casos_parametrizados[caso1-expected1]`

**Archivo:** `liquidator/tests/test_calculators/test_prestaciones.py`

**Cambio:**
- El test espera `715.208` pero el motor produce `715.704` que sí coincide con la fórmula documentada `(1.423.500 × 181) / 360 = 715.704`.
- Actualizar el expected a `715.704` con comentario en el commit: "Alineado con la fórmula documentada en el comentario del propio test".

```python
@pytest.mark.parametrize("sbl,dias,esperado", [
    (1_423_500, 181, 715_704),  # (1.423.500 × 181) / 360 = 715.704 (alineado con fórmula)
])
def test_casos_parametrizados(sbl, dias, esperado):
    ...
```

---

#### Tarea 2.H — Cierre de Fase 2

- Suite al 100%.
- `Contexto/KB_LLM/09_caso_canonico_usuario.md` actualizado con output real.
- Commit: `feat(fase-2): contrato legal, severity→blocking, override, normas integradas, tests golden`.

---

### 7.3 Riesgos Fase 2

- **R1:** La cita legal del cap podría no encontrarse en `legal_docs/` y requerir búsqueda externa. Mitigación: si no se encuentra, documentar como "decisión basada en interpretación estándar del CST art. 253 + práctica del Ministerio del Trabajo" y marcar para revisión.
- **R2:** Tests golden pueden revelar más bugs del motor. Mitigación: bugs en lógica se corrigen; tests con expected incorrecto se actualizan con justificación.
- **R3:** `OVERRIDE_APPROVED` puede usarse indebidamente. Mitigación: requerir `--override-reason` obligatorio (≥ 10 caracteres), registrar en audit log inmutable, agregar WARNING visible en documento.

## 7-bis. Fase 2-bis — Indexación IPC + anualización salarial (Tarea 2.X, absorción addendum SL2630-2024)

> **Origen:** Addendum `addendum_sl2630_y_ipc_2026-06-09.md` (APROBADO CON REPAROS el 2026-06-09). Decisión 2026-06-09: absorber en v2.0.0 como corrección de alcance **antes del release** (no como v2.0.1).
> **Prereq:** Fase 2 cerrada, incluyendo Tarea 2.B-bis (`SalarioResolver` integrado con regresión verde del caso canónico).
> **Reparos bloqueantes del addendum (a cerrar antes del DoD):**
>   (a) **NO usar Art. 155 CST** como sustento de prescripción — usar **Art. 488 CST**.
>   (b) Verificar **texto literal, sala y URL oficial** de SL2630-2024 antes de marcar su `texto_relevante` como cita verificada (estado inicial en código: `PENDIENTE_VERBATIM`).
>   (c) Modelar IPC como **índices acumulados**, NO como tasas anuales de inflación.

### 7-bis.1 DoD Fase 2-bis

- [ ] `liquidator/calculators/indexacion.py` implementado con `IPCIndexador` (clase nueva).
- [ ] Fuente de datos DANE en `params/ipc_dane_mensual.json` (preferible) o `params/ipc_dane_anual.json` (fallback) — formato **índice acumulado** (NO tasas anuales; si solo hay tasas, `scripts/build_ipc_index.py` debe convertirlas a índice acumulado antes de invocar `IPCIndexador`).
- [ ] `params/normas.json` con entradas nuevas: `SL2630_2024` (con `estado_verificacion` final, sala y URL verificados) y `CST_488_PRESCRIPCION` (texto literal del Art. 488 CST verificado en SUIN/CST).
- [ ] `params/checklist.json` con regla `V_INDEXACION_IPC` (severity MEDIUM, `blocking: false`).
- [ ] `liquidator/legal/normas_repository.py` carga las 2 normas nuevas y las expone vía `NormasRepository.cita(...)`.
- [ ] Compliance Engine reconoce `periodos_no_pagados: [...]` en el input, valida prescripción según Art. 488 CST y añade `<concepto>_indexado` al desglose con la VA calculada, `evidencia_legal` y advertencia si requiere verificación jurídica.
- [ ] `Contexto/KB_LLM/01_reglas_calculo.md` incluye sección "Indexación por IPC" con cita SL2630-2024 + Art. 488 CST + fórmula `VA = VH × (ÍndiceIPC_referencia / ÍndiceIPC_origen)`.
- [ ] **Cero referencias a Art. 155 CST** en `liquidator/`, `params/`, `Contexto/KB_LLM/`, `legal_docs/` (ni como sustento de prescripción ni de indexación). Verificación: `grep -rn "Art\. 155" liquidator/ params/ Contexto/KB_LLM/ legal_docs/` debe retornar 0 líneas.
- [ ] Tests verdes:
  - [ ] `liquidator/tests/test_calculators/test_indexacion.py` — `IPCIndexador.indexar(Decimal("1000000"), "2020-02-14", "2025-06-09")` retorna valor coherente con datos DANE reales en formato **índice acumulado**.
  - [ ] `liquidator/tests/test_golden/test_prescripcion_indexada.py` — prestación 2020 ($1M) → VA 2025 con IPC acumulado real.
  - [ ] El caso canónico del usuario (sin `periodos_no_pagados`) **sigue verde** (no regresión).
  - [ ] Test que rechaza explícitamente una fuente con valores entre 0 y 1 (tasa anual disfrazada de índice).
- [ ] Suite al 100%.

### 7-bis.2 Tarea 2.X — Indexación IPC para prestaciones no pagadas oportunamente

**Archivos:**
- Crear `liquidator/calculators/indexacion.py` (nuevo módulo, `IPCIndexador`).
- Crear `liquidator/tests/test_calculators/test_indexacion.py`.
- Crear `liquidator/tests/test_golden/test_prescripcion_indexada.py`.
- Crear `examples/inputs/prescripcion_indexada.json` + `examples/expected/prescripcion_indexada_result.json`.
- Modificar `params/normas.json` (entradas nuevas: `SL2630_2024`, `CST_488_PRESCRIPCION`).
- Modificar `params/checklist.json` (regla `V_INDEXACION_IPC`).
- Crear `params/ipc_dane_mensual.json` (preferible) o `params/ipc_dane_anual.json` (fallback).
- Crear `scripts/build_ipc_index.py` (conversión de tasas anuales DANE a índice acumulado, si hace falta).
- Modificar `liquidator/legal/normas_repository.py` (registrar las 2 normas nuevas).
- Modificar `liquidator/compliance/compliance_engine.py` (reconocer `periodos_no_pagados`).
- Modificar `liquidator/contracts/input_model.py` (agregar `PeriodoNoPagado` opcional al input).
- Modificar `Contexto/KB_LLM/01_reglas_calculo.md` (sección "Indexación por IPC").

**Diseño del `IPCIndexador`:**

```python
# liquidator/calculators/indexacion.py
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from pathlib import Path
import json

class IPCIndexador:
    """Indexación de valores históricos por IPC acumulado (DANE).

    La fuente de datos (params/ipc_dane_mensual.json o _anual.json) debe
    almacenar índices ACUMULADOS de precios, NO tasas anuales de inflación.
    Si solo se dispone de inflación anual, ejecutar scripts/build_ipc_index.py
    para convertir a índice acumulado antes de invocar este indexador.
    """

    def __init__(self, ipc_index: dict[str, Decimal], base_year: int = 2010):
        self.data = {k: Decimal(str(v)) for k, v in ipc_index.items()}
        self.base_year = base_year
        self._validar_no_tasas()

    def _validar_no_tasas(self) -> None:
        """Rechaza fuentes que parezcan tasas anuales (valores entre 0 y 1)."""
        for v in self.data.values():
            if Decimal("0") <= v <= Decimal("1"):
                raise ValueError(
                    f"Fuente IPC contiene valor {v} que parece tasa anual. "
                    f"Se requiere índice acumulado (>= 1)."
                )

    @classmethod
    def from_json(cls, path: str | Path, base_year: int = 2010) -> "IPCIndexador":
        data = json.loads(Path(path).read_text())
        return cls(data, base_year=base_year)

    def indice_para(self, fecha: date | str) -> Decimal:
        """Devuelve el índice acumulado para una fecha.
        Preferencia: índice mensual ('YYYY-MM'); si no, anual ('YYYY').
        Si solo hay anual y la fecha es intra-año, usar diciembre del año.
        """
        if isinstance(fecha, date):
            clave_mensual = fecha.strftime("%Y-%m")
            clave_anual = str(fecha.year)
        else:
            clave_mensual = fecha
            clave_anual = fecha[:4]
        if clave_mensual in self.data:
            return self.data[clave_mensual]
        if clave_anual in self.data:
            return self.data[clave_anual]
        raise KeyError(f"IPC no disponible para {fecha}")

    def indexar(self, vh: Decimal, fecha_origen: date | str,
                fecha_referencia: date | str) -> Decimal:
        """VA = VH × (ÍndiceIPC_referencia / ÍndiceIPC_origen).
        Aplica a prestaciones no pagadas oportunamente. NO usar inflación
        anual directa como si fuera índice acumulado.
        """
        ipc_origen = self.indice_para(fecha_origen)
        ipc_ref = self.indice_para(fecha_referencia)
        return (vh * ipc_ref / ipc_origen).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
```

**Esqueleto de `PeriodoNoPagado` (en `liquidator/contracts/input_model.py`):**

```python
class PeriodoNoPagado(BaseModel):
    concepto: Literal["cesantias", "prima", "intereses_cesantias", "vacaciones"]
    valor_historico: Decimal = Field(gt=0)
    fecha_causacion: date       # cuándo se causó la obligación
    fecha_exigibilidad: date    # cuándo se hizo exigible (inicio del cómputo de prescripción)
    fecha_referencia_indexacion: date  # hasta cuándo se indexa (default: hoy)
```

**Entradas en `params/normas.json`:**

```json
{
  "id": "SL2630_2024",
  "nombre": "Sentencia SL2630-2024 Corte Suprema de Justicia",
  "descripcion": "Criterio jurisprudencial sobre liquidación anual de prestaciones adeudadas e indexación por pérdida de poder adquisitivo.",
  "texto_relevante": "RESUMEN NO LITERAL — pendiente verificación verbatim con fuente oficial: las prestaciones adeudadas de años anteriores deben liquidarse año por año con el salario correspondiente a cada año y luego indexarse a valor presente.",
  "estado_verificacion": "PENDIENTE_VERBATIM",
  "sala": "Pendiente de verificación oficial; fuentes secundarias indican Sala de Descongestión Laboral N.º 1.",
  "url": "https://siugj.ramajudicial.gov.co/",
  "vigencia": "2024"
},
{
  "id": "CST_488_PRESCRIPCION",
  "nombre": "Código Sustantivo del Trabajo Art. 488",
  "descripcion": "Regla general de prescripción de acciones laborales: tres años desde que la obligación se hace exigible, salvo prescripciones especiales.",
  "texto_relevante": "RESUMEN NO LITERAL — verificar texto oficial en SUIN/CST: las acciones correspondientes a los derechos regulados en el CST prescriben en tres (3) años; en relación de trabajo, el término se cuenta desde que la obligación se hace exigible.",
  "estado_verificacion": "PENDIENTE_VERBATIM",
  "url": "https://www.suin-juriscol.gov.co/",
  "vigencia": "permanente"
}
```

> **CRÍTICO:** Antes de cerrar Tarea 2.X, los campos `texto_relevante`, `sala` y `url` deben ser verificados verbatim contra relatoría/SIUGJ y SUIN/CST. NO se acepta `PENDIENTE_VERBATIM` como estado final.

**Regla en `params/checklist.json`:**

```json
{
  "id": "V_INDEXACION_IPC",
  "description": "Indexación IPC para prestaciones no pagadas oportunamente: VA = VH × (ÍndiceIPC_referencia / ÍndiceIPC_causacion). Validar prescripción según Art. 488 CST cuando corresponda.",
  "severity": "MEDIUM",
  "blocking": false,
  "rule_ref": "SL2630-2024; Art. 488 CST (prescripción); DANE IPC",
  "formula": "VA = VH × (ÍndiceIPC_referencia / ÍndiceIPC_causacion)",
  "nota": "No usar tasas anuales de inflación como si fueran índices acumulados."
}
```

**Activación desde el input:** cuando el input declara `periodos_no_pagados: [...]`, el motor:
1. Valida prescripción (Art. 488 CST) — si está prescrito, registra WARNING y NO indexa.
2. Si no está prescrito, calcula VA con `IPCIndexador` y añade renglón `<concepto>_indexado` al desglose con:
   - `evidencia_legal`: "SL2630-2024; Art. 488 CST".
   - `formula`: "VA = VH × (ÍndiceIPC_ref / ÍndiceIPC_origen)".
   - Advertencia visible si la verificación jurídica es requerida (caso borderline de prescripción).

**Validación (DoD Fase 2-bis):**

```python
# tests/test_calculators/test_indexacion.py
from decimal import Decimal
from datetime import date
from liquidator.calculators.indexacion import IPCIndexador
import pytest

def test_ipc_rechaza_tasa_anual():
    """No se puede inicializar con valores entre 0 y 1 (tasa disfrazada)."""
    with pytest.raises(ValueError, match="tasa anual"):
        IPCIndexador({"2020": Decimal("0.036"), "2021": Decimal("0.054")})

def test_indexar_con_datos_mensuales():
    # Datos ficticios de prueba con base 100 en 2010-01
    idx = IPCIndexador({
        "2020-02": Decimal("131.2"),
        "2025-06": Decimal("168.5"),
    })
    va = idx.indexar(Decimal("1000000"), "2020-02-14", "2025-06-09")
    # VA = 1.000.000 × (168.5 / 131.2) ≈ 1.284.222
    assert va == Decimal("1284222")

def test_indexar_con_datos_anuales():
    idx = IPCIndexador({"2020": Decimal("131.2"), "2025": Decimal("168.5")})
    va = idx.indexar(Decimal("1000000"), date(2020, 2, 14), date(2025, 6, 9))
    assert va == Decimal("1284222")

def test_indice_para_fecha_sin_datos_falla():
    idx = IPCIndexador({"2020": Decimal("131.2")})
    with pytest.raises(KeyError):
        idx.indice_para("2019-01-01")
```

```python
# tests/test_golden/test_prescripcion_indexada.py
def test_prestacion_2020_indexada_a_2025():
    """Caso golden: prestación de $1.000.000 causada el 2020-02-14,
    pagada el 2025-06-09 con pérdida de poder adquisitivo."""
    # (Asume que params/ipc_dane_mensual.json tiene datos reales de 2020-02 y 2025-06)
    inp = json.loads((REPO / "examples" / "inputs" /
                      "prescripcion_indexada.json").read_text())
    engine = LiquidacionEngine(...)
    result = engine.process_input(inp)
    renglon = result["desglose"]["cesantia_indexada"]
    assert renglon["evidencia_legal"] == "SL2630-2024; Art. 488 CST"
    assert renglon["valor"] > Decimal("1000000")  # actualizado
    assert renglon["valor"] < Decimal("2000000")  # sanity check

def test_prestacion_prescrita_no_se_indexa_con_warning():
    """Si la exigibilidad fue hace >3 años sin interrupción, NO se indexa."""
    # fecha_exigibilidad = 2021-01-01, fecha_referencia = 2025-06-09 → > 3 años
    inp = json.loads(...)
    inp["periodos_no_pagados"][0]["fecha_exigibilidad"] = "2021-01-01"
    inp["periodos_no_pagados"][0]["fecha_referencia_indexacion"] = "2025-06-09"
    engine = LiquidacionEngine(...)
    result = engine.process_input(inp)
    # NO hay renglón indexado; hay WARNING en compliance
    assert "cesantia_indexada" not in result["desglose"]
    assert any("prescripción" in w.get("mensaje", "").lower()
               for w in result["compliance"]["warnings"])
```

```bash
# Búsqueda explícita: cero referencias a Art. 155 CST
grep -rn "Art\. 155" liquidator/ params/ Contexto/KB_LLM/ legal_docs/ || echo "OK: cero referencias a Art. 155"

# Suite completa
PYTHONPATH=. pytest liquidator/tests -q
# Esperado: 100% passed, 0 errors
```

### 7-bis.3 Riesgos Fase 2-bis

- **R1:** Datos DANE pueden no estar en formato JSON; requieren parsing de CSV/XLS o conversión de tasas anuales a índice acumulado. Mitigación: `scripts/build_ipc_index.py` en esta tarea; `IPCIndexador` rechaza valores entre 0 y 1 explícitamente (defensa en profundidad).
- **R2:** SL2630-2024 puede no estar disponible en URL pública estable. Mitigación: marcar `estado_verificacion` honestamente; si no se verifica verbatim, mantener `PENDIENTE_VERBATIM` y NO cerrar la fase hasta tener verificación.
- **R3:** Confundir inflación anual con índice IPC (error de categoría). Mitigación: tests que detectan valores entre 0 y 1 (tasa) y rechazan; documentación explícita en `IPCIndexador._validar_no_tasas()`.
- **R4:** Heredar referencia a Art. 155 CST en código, params, KB o legal_docs. Mitigación: grep obligatorio antes del cierre; nota en `Contexto/KB_LLM/00_fuente_de_verdad.md` recordando que la prescripción se rige por Art. 488 CST, no por Art. 155.
- **R5:** El input puede traer `periodos_no_pagados` con fechas inconsistentes (`fecha_causacion` > `fecha_exigibilidad` > `fecha_referencia_indexacion`). Mitigación: validación previa en Pydantic con `model_validator`; WARNING explícito al usuario.

## 8. Fase 3 — Documento generable robusto

> **Objetivo:** Separar cálculo de presentación, formalizar `document_context`, plantillas Jinja por estado, evidencia legal por renglón, validación pre-render, `liquidacion_BLOQUEADA.*` para NO_GO, auditoría inmutable por ejecución.

### 8.1 DoD Fase 3

- [ ] Estructura `document_context` formal (modelo Pydantic o dataclass).
- [ ] Plantillas Jinja separadas: `liquidator/templates/periodica.j2`, `finiquito.j2`, `blocked.j2`, `warning.j2`.
- [ ] Renderizadores separados: `markdown_renderer.py`, `pdf_renderer.py`.
- [ ] Validación pre-render: si el contexto está incompleto para el modo, error claro antes de renderizar.
- [ ] Para `compliance_status == "NO_GO"`: se genera `liquidacion_BLOQUEADA.{json,md,pdf}` con explicación de la regla fallida.
- [ ] Para `compliance_status in ("GO", "WARN", "OVERRIDE_APPROVED")`: se genera `liquidacion.{json,md,pdf}` con sección visible de advertencias.
- [ ] Cada renglón del desglose incluye `evidencia_legal` (cita CST/decreto/ley).
- [ ] Auditoría inmutable por ejecución: `audit/<timestamp>_<hash>.json` con params_hash, input_hash, output_hash, reglas_aplicadas, warnings, overrides.
- [ ] Caso canónico genera los 3 archivos correctos.
- [ ] Caso bloqueado por NO_GO genera `liquidacion_BLOQUEADA.*` con explicación.
- [ ] **`PreRenderValidator` específico por motivo** (matriz `REQUISITOS_POR_MOTIVO`): para `RENUNCIA_VOLUNTARIA` exige `vacaciones` y NO exige `indemnizacion`; para `DESPIDO_SIN_JUSTA_CAUSA` exige `vacaciones` y `indemnizacion`; etc. Validación falla con `PreRenderValidationError` claro si la combinación modo+motivo+renglones presentes no cumple el requisito.
- [ ] **Plantilla `finiquito_renuncia.j2` (o bloque condicional en `finiquito.j2`)** que renderiza la nota de **NO HAY INDEMNIZACIÓN** cuando `contrato.motivo_terminacion == "renuncia_voluntaria"`, citando Art. 49 num. 6 CST y Art. 64 CST explícitamente. Sección "Vacaciones compensadas (Art. 189-190 CST)" renderiza los días pendientes al cierre y el valor.
- [ ] Caso golden del addendum finiquito/vacaciones (`test_finiquito_renuncia_212d`, SBL 2.200.000, 7.5 días vacaciones) genera los 3 archivos correctos con la nota de no-indemnización visible.
- [ ] Suite al 100%.

### 8.2 Tareas Fase 3 (orden sugerido)

#### Tarea 3.A — `document_context` formal

**Archivo:** `liquidator/contracts/document_context.py`

```python
from pydantic import BaseModel
from datetime import datetime

class RenglonDesglose(BaseModel):
    concepto: str
    valor: int
    formula: str
    evidencia_legal: str  # "CST art. 253" o "Ley 50/1990 art. 99"
    parametros_usados: dict

class DocumentContext(BaseModel):
    metadata: dict
    input: dict  # anonimizado
    desglose: list[RenglonDesglose]
    total: int
    compliance: dict  # {status, failures, warnings, override}
    generado_en: datetime
    generado_por: str = "Jhond"
```

#### Tarea 3.B — Plantillas Jinja

**Directorio:** `liquidator/templates/`

- `periodica.j2` — comprobante periódico.
- `finiquito.j2` — carta de terminación.
- `blocked.j2` — documento de bloqueo.
- `warning.j2` — bloque de advertencias (incluido en los otros).

**Regla:** Las plantillas **no** asumen campos opcionales. Si falta evidencia_legal, error en pre-render, no en render.

#### Tarea 3.C — Renderers separados

**Archivos:** `liquidator/output/markdown_renderer.py`, `liquidator/output/pdf_renderer.py` (separar del actual `pdf_generator.py`).

#### Tarea 3.D — `liquidacion_BLOQUEADA.*` para NO_GO

**Comportamiento:**
```bash
python -m liquidator.cli liquidar input_con_fallo_critical.json
# Genera:
#   output/liquidacion_BLOQUEADA.json
#   output/liquidacion_BLOQUEADA.md
#   output/liquidacion_BLOQUEADA.pdf
# Exit code 2 (diferente de éxito)
# Mensaje: "Liquidación bloqueada por: [V_CESANTIAS_FORMULA] cesantías 1500000 != esperado 1520833"
```

#### Tarea 3.E — Auditoría inmutable

**Archivo:** `liquidator/audit/immutable_logger.py`

```python
import json, hashlib
from datetime import datetime, timezone
from pathlib import Path

def write_audit(repo_root: Path, execution: dict) -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    h = hashlib.sha256(json.dumps(execution, sort_keys=True).encode()).hexdigest()[:12]
    p = repo_root / "audit" / f"{ts}_{h}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(execution, indent=2, ensure_ascii=False))
    return p
```

**Cada ejecución guarda:** `params_version`, `params_hash`, `input_hash`, `output_hash`, `rules_applied`, `warnings`, `overrides`, `timestamp_utc`, `user`.

#### Tarea 3.F — Validación pre-render

**Archivo:** `liquidator/output/pre_render_validator.py`

Verifica antes de renderizar:
- `desglose` no vacío.
- Cada renglón tiene `evidencia_legal` no vacía.
- `total == sum(renglon.valor for renglon in desglose)`.
- Si modo = `FINIQUITO`, requiere `motivo_terminacion`.

**Validación:** Tests con contextos incompletos lanzan `PreRenderValidationError` antes de tocar plantillas.

---

#### Tarea 3.G — `PreRenderValidator` específico por motivo + plantilla `finiquito_renuncia.j2` *(absorción addendum finiquito/vacaciones 2026-06-11)*

>**Origen:** Addendum `addendum_finiquito_renuncia_vacaciones_2026-06-11.md` §C Tarea 3.G. Decisión 2026-06-11: absorber en v2.0.0 antes del release. **Prereq:** Tareas 1.C-ter, 2.B-ter y 2.Z cerradas (schema + motor + compliance). **Propósito:** cerrar el loop de presentación: ahora que el motor sabe calcular finiquito por renuncia correctamente, la plantilla debe renderizar la nota jurídica de "no indemnización" (Art. 49 num. 6 vs Art. 64) y el `PreRenderValidator` debe verificar que la combinación modo+motivo+renglones presentes cumple los requisitos legales antes de tocar el PDF.

**Archivos:**
- Modificar `liquidator/output/pre_render_validator.py` (agregar matriz `REQUISITOS_POR_MOTIVO` con la tabla del addendum §B.4).
- Crear `liquidator/templates/finiquito_renuncia.j2` (versión específica para este caso) **O** agregar bloque condicional en `liquidator/templates/finiquito.j2` (preferible por mantenibilidad — ver R6 abajo).
- Modificar `liquidator/output/markdown_renderer.py` para que la sección "Indemnización" se renderice explícitamente como `N/A — motivo renuncia` cuando aplica.
- Crear `liquidator/tests/test_output/test_pre_render_validator_por_motivo.py`.
- Crear `liquidator/tests/test_output/test_finiquito_renuncia_template.py` (verifica que la nota de no-indemnización aparece y la sección de vacaciones se renderiza).
- Actualizar `Contexto/KB_LLM/05_plantillas.md` (documentar el bloque condicional en `finiquito.j2`).

**Matriz de requisitos en `pre_render_validator.py`:**

```python
# liquidator/output/pre_render_validator.py
from enum import Enum

class MotivoTerminacion(str, Enum):
    # Reusar el enum de contratos; alias local para evitar import circular
    pass

REQUISITOS_POR_MOTIVO = {
    "renuncia_voluntaria": {
        "requiere":      ["vacaciones"],
        "no_requiere":   ["indemnizacion"],
        "nota_render":   "NO HAY INDEMNIZACIÓN: el trabajador renunció voluntariamente (Art. 49 num. 6 CST).",
    },
    "despido_sin_justa_causa": {
        "requiere":      ["vacaciones", "indemnizacion"],
        "no_requiere":   [],
        "nota_render":   "",
    },
    "despido_con_justa_causa": {
        "requiere":      ["vacaciones"],
        "no_requiere":   ["indemnizacion"],
        "nota_render":   "NO HAY INDEMNIZACIÓN: despido con causa legal (Art. 62 CST).",
    },
    "termino_fijo_vencido": {
        "requiere":      ["vacaciones"],
        "no_requiere":   ["indemnizacion"],   # salvo preaviso Art. 46
        "nota_render":   "NO HAY INDEMNIZACIÓN: contrato a término fijo vencido.",
    },
    "obra_o_labor_terminada": {
        "requiere":      ["vacaciones"],
        "no_requiere":   ["indemnizacion"],
        "nota_render":   "NO HAY INDEMNIZACIÓN: contrato por obra o labor terminada.",
    },
    "mutuo_acuerdo": {
        "requiere":      ["vacaciones"],
        "no_requiere":   ["indemnizacion"],
        "nota_render":   "NO HAY INDEMNIZACIÓN: terminación por mutuo acuerdo.",
    },
    "muerte_trabajador": {
        "requiere":      ["vacaciones"],
        "no_requiere":   ["indemnizacion"],
        "nota_render":   "Pago a herederos conforme al Art. 49 num. 5 CST y normas sucesoriales.",
    },
    "muerte_empleador": {
        "requiere":      ["vacaciones"],
        "no_requiere":   [],
        "nota_render":   "Verificar si el empleador era persona natural (Art. 49 num. 4).",
    },
    "suspension_deficitaria": {
        "requiere":      ["vacaciones"],
        "no_requiere":   ["indemnizacion"],
        "nota_render":   "",
    },
    "cierre_empresa": {
        "requiere":      ["vacaciones"],
        "no_requiere":   ["indemnizacion"],
        "nota_render":   "",
    },
}

class PreRenderValidator:
    def validar_requisitos_por_motivo(self, inp, desglose):
        """Valida que la combinación modo+motivo+renglones cumple los
        requisitos de la matriz REQUISITOS_POR_MOTIVO.
        Lanza PreRenderValidationError si falta un renglón requerido
        o si aparece un renglón marcado como 'no_requiere'.
        """
        if inp.contrato.motivo_terminacion is None:
            return  # sin motivo, no hay matriz a aplicar
        motivo = inp.contrato.motivo_terminacion.value
        requisitos = REQUISITOS_POR_MOTIVO.get(motivo)
        if requisitos is None:
            return  # motivo no catalogado: no aplicar matriz
        for req in requisitos["requiere"]:
            if req not in desglose or desglose[req]["valor"] == 0:
                raise PreRenderValidationError(
                    f"FINIQUITO por motivo '{motivo}' requiere renglón "
                    f"'{req}' en el desglose. Art. 49-64 CST."
                )
        for no_req in requisitos["no_requiere"]:
            if no_req in desglose and desglose[no_req]["valor"] > 0:
                raise PreRenderValidationError(
                    f"FINIQUITO por motivo '{motivo}' NO debe incluir "
                    f"renglón '{no_req}'. {requisitos['nota_render']}"
                )
```

**Bloque condicional en `finiquito.j2` (preferido sobre plantilla nueva — ver R6):**

```jinja
{# liquidator/templates/finiquito.j2 — bloque agregado #}

{% if contrato.motivo_terminacion == "renuncia_voluntaria" %}
## Indemnización
**NO APLICA** — El trabajador {{ trabajador.nombre }} renunció
voluntariamente al cargo, conforme al **Art. 49 numeral 6** del Código
Sustantivo del Trabajo. Por tanto, **no se genera indemnización**
conforme al **Art. 64 CST** (indemnización por despido sin justa causa,
no aplicable a renuncia del trabajador).

Base legal: Art. 49 num. 6 CST, Art. 64 CST.
{% endif %}

{% if desglose.vacaciones %}
## Vacaciones compensadas (Art. 189-190 CST)
Días pendientes al {{ contrato.fecha_terminacion_real }}:
**{{ vacaciones.dias_pendientes }}**
Valor: **{{ format_cop(desglose.vacaciones.valor) }}**
Fórmula: SBL / 30 × días_pendientes = {{ format_cop(salario.SBL) }} / 30 × {{ vacaciones.dias_pendientes }}.
{% endif %}
```

**Validación (DoD Fase 3):**

```python
# liquidator/tests/test_output/test_pre_render_validator_por_motivo.py
import pytest
from decimal import Decimal
from liquidator.output.pre_render_validator import (
    PreRenderValidator, PreRenderValidationError,
)
from liquidator.contracts.input_model import (
    LiquidacionInput, MotivoTerminacion,
)

def test_renuncia_sin_indemnizacion_pasa():
    inp = LiquidacionInput.model_validate({
        "trabajador": {"nombre": "X", "documento": "1"},
        "empleador":  {"nombre": "Y", "documento": "2"},
        "contrato": {
            "fecha_ingreso": "2025-11-16",
            "fecha_corte": "2026-06-15",
            "tipo": "INDEFINIDO",
            "motivo_terminacion": "renuncia_voluntaria",
            "fecha_terminacion_real": "2026-06-15",
        },
        "salario": {"SBL": 2200000},
        "modo": "FINIQUITO",
        "vacaciones": {"dias_pendientes": 7.5},
    })
    desglose = {
        "vacaciones": {"valor": Decimal("550000"), "dias": Decimal("7.5")},
        # NO indemnizacion (es renuncia)
    }
    PreRenderValidator().validar_requisitos_por_motivo(inp, desglose)  # no raise

def test_renuncia_con_indemnizacion_falla():
    inp = LiquidacionInput.model_validate({
        "trabajador": {"nombre": "X", "documento": "1"},
        "empleador":  {"nombre": "Y", "documento": "2"},
        "contrato": {
            "fecha_ingreso": "2025-11-16",
            "fecha_corte": "2026-06-15",
            "tipo": "INDEFINIDO",
            "motivo_terminacion": "renuncia_voluntaria",
            "fecha_terminacion_real": "2026-06-15",
        },
        "salario": {"SBL": 2200000},
        "modo": "FINIQUITO",
        "vacaciones": {"dias_pendientes": 7.5},
    })
    desglose = {
        "vacaciones": {"valor": Decimal("550000"), "dias": Decimal("7.5")},
        "indemnizacion": {"valor": Decimal("1000000")},  # NO debería estar
    }
    with pytest.raises(PreRenderValidationError, match="NO debe incluir.*indemnizacion"):
        PreRenderValidator().validar_requisitos_por_motivo(inp, desglose)

def test_despido_sin_justa_causa_sin_indemnizacion_falla():
    inp = LiquidacionInput.model_validate({
        "trabajador": {"nombre": "X", "documento": "1"},
        "empleador":  {"nombre": "Y", "documento": "2"},
        "contrato": {
            "fecha_ingreso": "2025-11-16",
            "fecha_corte": "2026-06-15",
            "tipo": "INDEFINIDO",
            "motivo_terminacion": "despido_sin_justa_causa",
            "fecha_terminacion_real": "2026-06-15",
        },
        "salario": {"SBL": 2200000},
        "modo": "FINIQUITO",
        "vacaciones": {"dias_pendientes": 0},
    })
    desglose = {
        "vacaciones": {"valor": Decimal("0")},
        # Falta indemnizacion (obligatoria para despido sin justa causa)
    }
    with pytest.raises(PreRenderValidationError, match="requiere renglón.*indemnizacion"):
        PreRenderValidator().validar_requisitos_por_motivo(inp, desglose)

def test_periodico_no_evalua_matriz():
    inp = LiquidacionInput.model_validate({
        "trabajador": {"nombre": "X", "documento": "1"},
        "empleador":  {"nombre": "Y", "documento": "2"},
        "contrato": {"fecha_ingreso": "2025-11-16", "fecha_corte": "2026-06-15", "tipo": "INDEFINIDO"},
        "salario": {"SBL": 2200000},
        "modo": "PERIODICA",
    })
    desglose = {"cesantias": {"valor": Decimal("1000000")}}
    # No raise (PERIODICA no aplica matriz)
    PreRenderValidator().validar_requisitos_por_motivo(inp, desglose)
```

```python
# liquidator/tests/test_output/test_finiquito_renuncia_template.py
def test_plantilla_renderiza_nota_no_indemnizacion():
    """Verifica que el bloque condicional del template muestra la nota jurídica."""
    contexto = {
        "contrato": {"motivo_terminacion": "renuncia_voluntaria", "fecha_terminacion_real": "2026-06-15"},
        "trabajador": {"nombre": "ANONIMIZADO"},
        "salario": {"SBL": 2200000},
        "desglose": {"vacaciones": {"valor": 550000, "dias": 7.5}},
        "vacaciones": {"dias_pendientes": 7.5},
    }
    template = env.get_template("finiquito.j2")
    rendered = template.render(contexto)
    assert "NO APLICA" in rendered
    assert "Art. 49 numeral 6" in rendered
    assert "Art. 64 CST" in rendered
    assert "Vacaciones compensadas" in rendered
    assert "550.000" in rendered  # valor con formato COP

def test_plantilla_no_muestra_nota_en_despido():
    """El bloque 'NO APLICA indemnización' solo aparece para renuncia_voluntaria."""
    contexto = {
        "contrato": {"motivo_terminacion": "despido_sin_justa_causa", "fecha_terminacion_real": "2026-06-15"},
        "trabajador": {"nombre": "ANONIMIZADO"},
        "salario": {"SBL": 2200000},
        "desglose": {},
        "vacaciones": {"dias_pendientes": 0},
    }
    rendered = env.get_template("finiquito.j2").render(contexto)
    # La nota específica de renuncia NO debe aparecer
    assert "El trabajador .* renunció" not in rendered
```

```bash
# Suite completa Fase 3
PYTHONPATH=. pytest liquidator/tests -q
# Esperado: 100% passed, 0 errors
```

**Riesgos específicos:**
- **R1:** La matriz `REQUISITOS_POR_MOTIVO` puede quedar desactualizada si se agrega un motivo nuevo al enum y se olvida agregar su entrada. Mitigación: test que enumera `MotivoTerminacion` y verifica que cada valor tiene entrada en la matriz (`test_cobertura_matriz_motivos`); falla el test si falta un motivo.
- **R2:** El bloque `{% if contrato.motivo_terminacion == "renuncia_voluntaria" %}` en Jinja compara strings; si el enum se serializa distinto (ej. `MotivoTerminacion.RENUNCIA_VOLUNTARIA` en vez de `"renuncia_voluntaria"`), el bloque nunca se renderiza. Mitigación: el template recibe `motivo_terminacion` como string (no como enum) por convención del motor; agregar test de regresión `test_plantilla_motivo_es_string`.
- **R3:** `format_cop` puede no existir en el contexto Jinja. Mitigación: registrar el filtro en el environment antes de renderizar (Fase 1 ya lo hace); test que verifica que `format_cop` está disponible.
- **R4:** La validación `validar_requisitos_por_motivo` puede romper la generación de plantillas para casos legacy (sin motivo_terminacion). Mitigación: guard `if inp.contrato.motivo_terminacion is None: return` al inicio; test de regresión `test_periodico_no_evalua_matriz`.
- **R5:** La indemnización Art. 64 CST no se implementa en Tarea 2.B-ter; por tanto, el caso `despido_sin_justa_causa` no puede pasar la validación `validar_requisitos_por_motivo` hasta que se implemente la indemnización (lo cual está fuera del scope del addendum 2026-06-11). Mitigación: documentar explícitamente en KB y en CHANGELOG que `despido_sin_justa_causa` solo funciona tras implementar indemnización (Tarea 2.W futura, fuera de v2.0).
- **R6:** Crear `finiquito_renuncia.j2` separado duplica la lógica base de `finiquito.j2`. Mitigación: preferir bloque condicional en `finiquito.j2` (más mantenible, una sola fuente de verdad para la estructura del documento). El addendum ya lo recomienda.

---

### 8.3 Riesgos Fase 3

- **R1:** WeasyPrint puede no estar disponible en WSL. Mitigación: tener fallback claro (error con instrucción de instalar `libpango`, `libcairo`); nunca disfrazar `.txt` como PDF.
- **R2:** `audit/` puede crecer mucho. Mitigación: configurar rotación o un script `scripts/rotate_audit.py` (Fase 4).
- **R3:** Plantillas Jinja pueden ejecutarse con datos reales y filtrarse al repo. Mitigación: tests renderizan con fixtures anonimizadas; CI verifica que ningún render contenga `documento` o `nombre` de ejemplos no-anonimizados.

---

## 9. Fase 4 — v2.0 release

> **Objetivo:** Empaquetado, CI, documentación y release oficiales de v2.0. **3 liquidaciones reales verificadas por Jhond** (diag. §6.8) como DoD final.

### 9.1 DoD Fase 4

- [ ] Versión en `pyproject.toml` = `2.0.0`.
- [ ] `liquidacion --version` retorna `2.0.0`.
- [ ] CI ejecuta: `python3 -m compileall liquidator` + `ruff check` + `pytest liquidator/tests -q` — todo verde.
- [ ] `mypy` configurado (no requiere 100% verde en Fase 4, pero sí ejecutándose y reportando).
- [ ] `black` configurado.
- [ ] `CHANGELOG.md` con entrada v2.0 listando breaking changes.
- [ ] `README.md` reescrito: refleja v2.0, no v1.0.0; instrucciones de instalación, uso, comandos CLI, ejemplos.
- [ ] `QWEN.md` (legacy) reemplazado o eliminado (referenciaba `settle` que no existe).
- [ ] `docs/health/system_health.json` y `docs/validation_results.json` regenerados desde CI o eliminados.
- [ ] **3 liquidaciones reales ejecutadas por Jhond** con la v2.0; resultados coinciden con cálculos manuales o con otra herramienta de referencia. Capturas/registros en `audit/`.
- [ ] Suite al 100%.

### 9.2 Tareas Fase 4

#### Tarea 4.A — Promoción a v2.0.0

**Archivos:** `pyproject.toml`, `liquidator/__init__.py`, `README.md`, `CHANGELOG.md`.

```toml
version = "2.0.0"
```

```python
__version__ = "2.0.0"
```

```markdown
## [2.0.0] - 2026-XX-XX

### Breaking changes
- Entry point cambió de `settle` a `liquidacion`.
- Schemas de entrada/salida formalizados con Pydantic; el JSON histórico puede no ser compatible.
- Estados de compliance: `WARN` eliminado, reemplazado por `GO` con sección de advertencias.
- `severity → blocking` activo por defecto; HIGH requiere `--override --override-reason`.
- `params/checklist.json` requiere campo `blocking` por regla.
- `audit/` ahora contiene JSON inmutable por ejecución.
- Comando CLI: `python -m liquidator.cli` o `liquidacion`; `settle*` deprecados.

### Added
- Caso canónico 16-Nov-2025 a 9-Jun-2026 (as-of 2026-06-09; fecha de terminación real TBD; 206 días en dos segmentos) documentado y reproducible.
- Segundo cerebro local en `Contexto/KB_LLM/`.
- 10 tests golden.
- KB freshness check.
```

#### Tarea 4.B — CI mínima

**Archivo:** `.github/workflows/ci.yml` (o script `scripts/ci.sh` si no se usa GitHub).

```yaml
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.12"}
      - run: pip install -e ".[dev]"
      - run: python -m compileall liquidator
      - run: ruff check liquidator
      - run: pytest liquidator/tests -q --tb=short
      - run: python scripts/check_kb_freshness.py
```

#### Tarea 4.C — README reescrito

Secciones obligatorias:
- Qué es y qué no es (CLI local, sin API).
- Instalación (`pip install -e .` o `uv tool install`).
- Uso (`liquidacion --help`, `liquidacion liquidar input.json`).
- Caso canónico (con output esperado).
- Estructura del proyecto.
- Cómo correr tests.
- Cómo contribuir.
- Disclaimer legal.

#### Tarea 4.D — Limpieza documental

- Eliminar `QWEN.md` o reemplazar por `CONTRIBUTING.md` específico.
- Regenerar o eliminar `docs/health/system_health.json` y `docs/validation_results.json`.
- `docs/code_quality_analysis.md`: reescribir reflejando el estado real post-Fase 4.

#### Tarea 4.E — Tag y release

```bash
git tag -a v2.0.0 -m "v2.0.0 — CLI local de liquidación con segundo cerebro local"
git push origin v2.0.0
```

(Adaptar si el repo no se sube a remoto; el tag local basta para DoD.)

#### Tarea 4.F — 3 liquidaciones reales verificadas

**Proceso manual del usuario (Jhond):**
1. Seleccionar 3 liquidaciones reales de su operación.
2. Calcular con `liquidacion liquidar real_input.json`.
3. Comparar con cálculo manual o herramienta de referencia.
4. Guardar input, output y comparativa en `audit/validacion_v2/<caso>/`.
5. Si hay discrepancia, NO se cierra Fase 4; se abre issue y se corrige.

**DoD:** 3 archivos en `audit/validacion_v2/<caso>/` con resultado coincidente.

---

### 9.3 Riesgos Fase 4

- **R1:** CI puede no estar disponible (no hay remoto). Mitigación: `scripts/ci.sh` ejecutable localmente; documentar como "CI local".
- **R2:** Las 3 liquidaciones reales pueden revelar bugs no detectados por tests sintéticos. Mitigación: tratar como golden tests adicionales (extender Fase 5 si es necesario).
- **R3:** Promoción de versión rompe scripts que importan `liquidator`. Mitigación: documentar breaking changes en CHANGELOG; si es necesario, mantener rama `v1.x` con fixes de seguridad por un ciclo.

---

## 10. Fase 5 (opcional) — Investigación de casos reales

> **Solo se ejecuta si en el trascurso de las Fases 0-4 surge información sobre casos reales disponibles** (conceptos MinTrabajo, jurisprudencia, casos contables propios). **No se ejecuta por defecto.**

### 10.1 DoD Fase 5 (si se ejecuta)

- [ ] Al menos 1 caso real anexado a `Contexto/KB_LLM/casos_reales/` con:
  - `fuente.md` — cita de la fuente (MinTrabajo, jurisprudencia, caso interno).
  - `input.json` — anonimizado.
  - `resultado_esperado.md` — valores esperados.
  - `evidencia/` — PDFs/imágenes de soporte (anonimizados).
- [ ] Test golden derivado creado y verde.
- [ ] `Contexto/KB_LLM/06_riesgos_modelo.md` actualizado con la nueva fuente.

### 10.2 Tareas Fase 5 (orden sugerido)

#### Tarea 5.A — Investigación de fuentes
- Buscar conceptos del Ministerio del Trabajo sobre liquidación de prestaciones.
- Buscar sentencias de la Corte Suprema/Corte Constitucional sobre casos típicos.
- Si el usuario (Jhond) tiene casos contables propios anonimizados, considerarlos.

#### Tarea 5.B — Anexar caso
- Crear directorio en `Contexto/KB_LLM/casos_reales/<caso_id>/`.
- Anonimizar nombres, documentos, salarios reales (usar datos sintéticos equivalentes).
- Citar fuente.

#### Tarea 5.C — Convertir en test golden
- Crear `examples/inputs/caso_real_<id>.json`.
- Crear `examples/expected/caso_real_<id>_result.json`.
- Crear `liquidator/tests/test_golden/test_caso_real_<id>.py`.

---

## 11. Cross-cutting: Reglas de operación (de diag. §5.5)

Estas reglas aplican transversalmente. Se mantienen en `AGENTS.md` y `Contexto/KB_LLM/00_fuente_de_verdad.md`.

1. Antes de calcular, leer `params/<año>.json` (todos los vigentes), `params/normas.json`, `params/plazos.json`.
2. Antes de confiar en una regla legal, buscar evidencia en `legal_docs/` o en el código que la implementa.
3. Antes de aceptar documentación, contrastarla contra código, params y tests.
4. No hardcodear SMMLV, auxilio de transporte, límites salariales, tasas o plazos.
5. No usar outputs generados como fuente de verdad.
6. No incluir nombres, documentos de identidad, salarios reales o datos sensibles en la KB, logs o repo.
7. No generar PDF si el estado de compliance es `NO_GO`.
8. No disfrazar `.txt` como PDF.
9. Separar claramente estados `GO`, `WARN`, `NO_GO` y `OVERRIDE_APPROVED`.
10. Cada documento generado debe poder auditar qué params, normas y reglas usó.
11. **Antes de aceptar como verdad cualquier afirmación del diagnóstico 2026-06-09 o de la KB, verificar contra código vivo.**
12. Reproducir el caso canónico (206 días en dos segmentos: 2025-H2 46d + 2026-H1 160d, SBL=2.200.000, cesantías TBD-motor-Fase2 (ver §3, segmento 2025 + segmento 2026)) como primera prueba de cordura antes de cualquier cambio de fase.

---

## 12. Comandos de verificación rápida

```bash
# ¿Sintaxis válida?
python3 -m compileall -q liquidator

# ¿Suite al 100%?
PYTHONPATH=. uv run --with pytest --with python-dateutil --with PyYAML \
  --with jsonschema --with pydantic --with loguru --with click \
  --with markdown --with Jinja2 pytest liquidator/tests -q

# ¿KB fresca?
python3 scripts/check_kb_freshness.py

# ¿Limpieza?
ruff check liquidator

# ¿Caso canónico?
python -m liquidator.cli liquidar examples/inputs/caso_canonico_periodico_206d.json

# ¿Versión?
liquidacion --version   # 2.0.0 al cerrar Fase 4
```

---

## 13. Definición de Done del plan completo

(Diag. §6.8 — el plan completo está "Done" cuando se cumplen **todas** estas condiciones.)

1. v2.0 está publicada (tag v2.0.0, CHANGELOG con breaking changes).
2. El caso canónico (16-Nov-2025 a 9-Jun-2026 (as-of 2026-06-09; fecha de terminación real TBD; 206 días en dos segmentos), SBL=2.200.000, cesantías TBD-motor-Fase2 (ver §3, segmento 2025 + segmento 2026)) se calcula correctamente y genera los 3 archivos esperados.
3. La suite completa de tests pasa al 100%.
4. `AGENTS.md` y `Contexto/KB_LLM/` existen y son mantenibles.
5. El usuario (Jhond) ha ejecutado al menos 3 liquidaciones reales con la nueva versión y los resultados coinciden con cálculos hechos manualmente o con otra herramienta de referencia.
6. El CHANGELOG documenta los breaking changes de v1.x a v2.0.
7. **Addendum SL2630-2024 + IPC absorbido en v2.0.0** (corrección de alcance, no v2.0.1):
   - [ ] Schema `Salario` extendido retrocompatible con `sbl_por_anio` y `historial_salarial` (Tarea 1.C-bis, Fase 1).
   - [ ] `SalarioResolver` integrado en el motor, con **regresión verde del caso canónico** (Tarea 2.B-bis, Fase 2).
   - [ ] `IPCIndexador` implementado con datos DANE en **formato índice acumulado** (NO tasas anuales); test golden de prescripción/indexación verde (Fase 2-bis, Tarea 2.X).
   - [ ] `SL2630-2024` y Art. 488 CST citados en `params/normas.json` con `estado_verificacion` final (no `PENDIENTE_VERBATIM`).
   - [ ] **Cero referencias a Art. 155 CST** en `liquidator/`, `params/`, `Contexto/KB_LLM/`, `legal_docs/` (ni como sustento de prescripción ni de indexación).
8. **Addendum finiquito por renuncia + vacaciones compensadas absorbido en v2.0.0** (corrección de alcance, no v2.0.1):
   - [ ] Schema `Contrato` extendido con `motivo_terminacion: MotivoTerminacion` (enum, 10 motivos Arts. 45-49 CST) y modelo `VacacionesEstado` tipado (Decimal para `dias_pendientes`). Caso canónico PERIODICA **sigue verde** (regresión cero). Tarea 1.C-ter cerrada (Fase 1).
   - [ ] `calculate_vacaciones_compensadas_finiquito` implementado en `PrestacionesCalculator` con fórmula Art. 189-190 CST `(SBL/30) × dias_pendientes`. El motor lo invoca **solo** en modo `FINIQUITO` con `dias_pendientes > 0`. Caso canónico PERIODICA NO paga vacaciones compensadas (regresión dura). Tarea 2.B-ter cerrada (Fase 2).
   - [ ] Reglas de compliance `V_VACACIONES_FINIQUITO` (CRITICAL, blocking) y `V_VACACIONES_DECLARADAS_FINIQUITO` (MEDIUM, no blocking) activas. La CRITICAL bloquea si `modo=FINIQUITO AND dias_pendientes > 0 AND renglón vacaciones ausente`. Tarea 2.Z cerrada (Fase 2).
   - [ ] `PreRenderValidator` con matriz `REQUISITOS_POR_MOTIVO`; plantilla `finiquito.j2` con bloque condicional que muestra "NO HAY INDEMNIZACIÓN — Art. 49 num. 6 vs Art. 64 CST" cuando `motivo_terminacion == "renuncia_voluntaria"`. Sección "Vacaciones compensadas" renderiza días pendientes y valor. Tarea 3.G cerrada (Fase 3).
   - [ ] **Verificación verbatim del Art. 189 CST párr. 1°** en SUIN (https://www.suin-juriscol.gov.co/) con `estado_verificacion: "VERIFICADO"` y URL/fecha de captura registrados en `params/normas.json` (entrada `CST_189_VACACIONES`). NO se cierra Tarea 2.B-ter con verificación pendiente. Indemnización Art. 64 CST queda **explícitamente fuera del scope** de v2.0 (referenciada en `Contexto/KB_LLM/01_reglas_calculo.md` para casos futuros).
   - [ ] Test golden del addendum (`test_finiquito_renuncia_212d`): SBL 2.200.000, 7.5 días vacaciones, total ~$4.427.014 (rango $4.400.000–$4.450.000), renglón vacaciones = $550.000, indemnización N/A. Verde en CI.
   - [ ] **Regresión dura del caso canónico PERIODICA** (206d, SBL 2.200.000, dos segmentos): **sigue verde** tras integrar todas las tareas del addendum. Verificación: `pytest liquidator/tests/test_canonico/ -q` retorna 100% passed.

---

## 14. Apéndice: archivos clave (referencia rápida)

| Propósito | Ruta |
|---|---|
| Diagnóstico fuente | `Contexto/diagnostico_liquidacion_cli_2026-06-09.md` |
| Plan (este doc) | `Plan/plan_modernizacion_v2.0_2026-06-09.md` |
| Caso canónico input | `examples/inputs/caso_canonico_periodico_206d.json` (a crear en Fase 1) |
| Caso canónico expected | `examples/expected/caso_canonico_periodico_206d_result.{json,md,pdf}` (Fase 1+) |
| KB LLM | `Contexto/KB_LLM/00..09_*.md` (Fase 0) |
| Reglas para agentes | `AGENTS.md` (Fase 0) |
| Prompts | `Contexto/prompts/*.md` (Fase 0) |
| Motor | `liquidator/core/engine.py` |
| Parser input | `liquidator/core/input_parser.py` |
| Params centralizados | `liquidator/core/params_provider.py` (Fase 1) |
| Validación input | `liquidator/validators/input_validator.py` |
| Calculadores | `liquidator/calculators/{prestaciones,indemnizacion,sbl}.py` |
| Compliance | `liquidator/compliance/compliance_engine.py` |
| Generadores | `liquidator/output/{json,markdown,pdf}_generator.py` |
| Renderers | `liquidator/output/{markdown,pdf}_renderer.py` (Fase 3) |
| CLI entry | `liquidator/cli/main.py` (Fase 1) |
| Plantillas | `liquidator/templates/{periodica,finiquito,blocked,warning}.j2` (Fase 3) |
| Schemas | `liquidator/contracts/{input,output,document_context}_model.py` (Fases 1, 3) |
| Params 2025 | `params/2025.json` |
| Normas | `params/normas.json` |
| Plazos | `params/plazos.json` |
| Checklist compliance | `params/checklist.json` |
| Tests golden | `liquidator/tests/test_golden/` (Fase 2) |
| KB freshness | `scripts/check_kb_freshness.py`, `tests/test_kb_freshness.py` (Fase 0) |
| Auditoría inmutable | `liquidator/audit/immutable_logger.py` (Fase 3) |
| Empaquetado | `pyproject.toml` (Fase 1, promovido a 2.0.0 en Fase 4) |
| CI | `.github/workflows/ci.yml` o `scripts/ci.sh` (Fase 4) |
| Changelog | `CHANGELOG.md` (Fase 4) |

### 14.1 Archivos introducidos por el addendum SL2630-2024 + IPC (Fase 1, 2 y 2-bis)

| Propósito | Ruta |
|---|---|
| Addendum origen | `Planificación/addendum_sl2630_y_ipc_2026-06-09.md` |
| `MesValor` y `Salario` extendido | `liquidator/contracts/input_model.py` (modificado en Fase 1 — Tarea 1.C-bis) |
| Tests schema salario extendido | `liquidator/tests/test_contracts/test_salario_extendido.py` (Fase 1 — Tarea 1.C-bis) |
| `SalarioResolver` (SBL por año) | `liquidator/core/salario_resolver.py` (Fase 2 — Tarea 2.B-bis) |
| Tests `SalarioResolver` | `liquidator/tests/test_core/test_salario_resolver.py` (Fase 2 — Tarea 2.B-bis) |
| Test golden SBL variable por año | `liquidator/tests/test_golden/test_salario_variable_por_anio.py` (Fase 2 — Tarea 2.B-bis) |
| `IPCIndexador` | `liquidator/calculators/indexacion.py` (Fase 2-bis — Tarea 2.X) |
| Tests IPCIndexador | `liquidator/tests/test_calculators/test_indexacion.py` (Fase 2-bis) |
| Test golden prescripción/indexación | `liquidator/tests/test_golden/test_prescripcion_indexada.py` (Fase 2-bis) |
| Fuente DANE IPC (índice acumulado) | `params/ipc_dane_mensual.json` (preferible) o `params/ipc_dane_anual.json` (Fase 2-bis) |
| Script conversión IPC | `scripts/build_ipc_index.py` (Fase 2-bis, si se parte de tasas anuales) |
| Normas SL2630-2024 + Art. 488 CST | entradas en `params/normas.json` (Fase 2-bis) |
| Regla `V_INDEXACION_IPC` | entrada en `params/checklist.json` (Fase 2-bis) |
| Esquema `PeriodoNoPagado` | `liquidator/contracts/input_model.py` (Fase 2-bis) |

### 14.2 Archivos introducidos por el addendum finiquito/vacaciones (Fases 1, 2 y 3)

| Propósito | Ruta |
|---|---|
| Addendum origen | `Planificación/addendum_finiquito_renuncia_vacaciones_2026-06-11.md` |
| Enum `MotivoTerminacion` + modelo `VacacionesEstado` + `PeriodoDisfrute` | `liquidator/contracts/input_model.py` (modificado en Fase 1 — Tarea 1.C-ter) |
| Validación cruzada `Contrato.fecha_terminacion_real` ↔ `motivo_terminacion` | `liquidator/contracts/input_model.py` (Fase 1 — Tarea 1.C-ter) |
| Validación cruzada `LiquidacionInput.modo` ↔ `contrato.motivo_terminacion` | `liquidator/contracts/input_model.py` (Fase 1 — Tarea 1.C-ter) |
| Tests schema vacaciones tipado | `liquidator/tests/test_contracts/test_vacaciones_estado.py` (Fase 1 — Tarea 1.C-ter) |
| Tests schema motivo_terminacion | `liquidator/tests/test_contracts/test_motivo_terminacion.py` (Fase 1 — Tarea 1.C-ter) |
| `calculate_vacaciones_compensadas_finiquito` (Art. 189-190 CST) | `liquidator/calculators/prestaciones.py` (Fase 2 — Tarea 2.B-ter) |
| Hook `_calcular_vacaciones_si_finiquito` | `liquidator/core/engine.py` (Fase 2 — Tarea 2.B-ter) |
| Tests unitarios vacaciones finiquito | `liquidator/tests/test_calculators/test_vacaciones_finiquito.py` (Fase 2 — Tarea 2.B-ter) |
| Test golden finiquito renuncia 212d | `liquidator/tests/test_golden/test_finiquito_renuncia_212d.py` (Fase 2 — Tarea 2.B-ter) |
| Fixture input finiquito renuncia | `examples/inputs/finiquito_renuncia_212d.json` (Fase 2 — Tarea 2.B-ter) |
| Fixture expected finiquito renuncia | `examples/expected/finiquito_renuncia_212d_result.json` (Fase 2 — Tarea 2.B-ter) |
| Regla compliance `V_VACACIONES_FINIQUITO` (CRITICAL) | entrada en `params/checklist.json` (Fase 2 — Tarea 2.Z) |
| Regla compliance `V_VACACIONES_DECLARADAS_FINIQUITO` (MEDIUM) | entrada en `params/checklist.json` (Fase 2 — Tarea 2.Z) |
| Tests compliance vacaciones finiquito | `liquidator/tests/test_compliance/test_vacaciones_finiquito_compliance.py` (Fase 2 — Tarea 2.Z) |
| Norma `CST_189_VACACIONES` (Art. 189 párr. 1°) | entrada en `params/normas.json` con `estado_verificacion: "VERIFICADO"` tras descarga SUIN (Fase 2 — Tarea 2.B-ter) |
| Matriz `REQUISITOS_POR_MOTIVO` en pre-render | `liquidator/output/pre_render_validator.py` (Fase 3 — Tarea 3.G) |
| Bloque condicional `{% if motivo_terminacion == "renuncia_voluntaria" %}` | `liquidator/templates/finiquito.j2` (Fase 3 — Tarea 3.G) |
| Tests pre-render por motivo | `liquidator/tests/test_output/test_pre_render_validator_por_motivo.py` (Fase 3 — Tarea 3.G) |
| Tests plantilla finiquito | `liquidator/tests/test_output/test_finiquito_renuncia_template.py` (Fase 3 — Tarea 3.G) |
| Documentación de vacaciones compensadas en finiquito | `Contexto/KB_LLM/01_reglas_calculo.md` (Fase 2 — Tarea 2.B-ter) |
| Documentación de las 2 reglas de compliance | `Contexto/KB_LLM/03_compliance_blocking.md` (Fase 2 — Tarea 2.Z) |
| Documentación de schema extendido | `Contexto/KB_LLM/04_schema_entrada.md` (Fase 1 — Tarea 1.C-ter) |
| Documentación de plantillas | `Contexto/KB_LLM/05_plantillas.md` (Fase 3 — Tarea 3.G) |

---

## 15. Apéndice: decisiones validadas (de diag. §6) que el plan asume

| ID | Decisión |
|---|---|
| §6.1 | Tipo de producto: CLI local, usuario único Jhond, sin API, sin validación externa. |
| §6.2 | Caso canónico: 16-Nov-2025 a 9-Jun-2026 (as-of 2026-06-09; fecha de terminación real TBD; 206 días en dos segmentos), SBL=2.200.000, cesantías TBD-motor-Fase2 (ver §3, segmento 2025 + segmento 2026). |
| §6.3 | Infraestructura 100% local. LLM solo si es local. |
| §6.4 | Compliance: CRITICAL/HIGH bloquean; HIGH con override; MEDIUM advierte; LOW/INFO solo registra. |
| §6.5 | Versión objetivo: v2.0 con breaking changes permitidos. |
| §6.6 | DoD universal: 100% de tests pasando por fase. |
| §6.7 | Fase 5 opcional, condicional a casos reales disponibles. |
| §6.8 | DoD del plan completo: v2.0 publicada + caso canónico + 3 liquidaciones reales verificadas por Jhond. |
| §6.9 | Mecanismos compensatorios por usuario único: tests exhaustivos, auditoría inmutable, compliance bloqueante, trazabilidad de fuentes. |
| §6.10 | **Addendum SL2630-2024 + IPC absorbido en v2.0.0** (corrección de alcance antes del release, no v2.0.1). Distribución: Tarea 1.C-bis → Fase 1; Tarea 2.B-bis → Fase 2; Tarea 2.X → nueva Fase 2-bis. Reparos bloqueantes: (a) NO usar Art. 155 CST para prescripción — usar Art. 488 CST; (b) SL2630-2024 debe verificarse verbatim contra relatoría/SIUGJ antes de cerrar Fase 2-bis; (c) IPC modelado como índice acumulado, no como tasa anual. |
| §6.11 | **Addendum finiquito por renuncia + vacaciones compensadas absorbido en v2.0.0** (corrección de alcance antes del release, no v2.0.1; mismo tratamiento que §6.10). Distribución: Tarea 1.C-ter → Fase 1; Tarea 2.B-ter → Fase 2; Tarea 2.Z → Fase 2; Tarea 3.G → Fase 3. NO se crea nueva fase (las tareas se anexan a fases existentes). Reparos bloqueantes: (a) **Verificar texto literal del Art. 189 CST párr. 1° en SUIN** (https://www.suin-juriscol.gov.co/) antes de cerrar Tarea 2.B-ter, registrando `estado_verificacion: "VERIFICADO"` con URL y fecha en `params/normas.json` (entrada `CST_189_VACACIONES`); (b) **El motor debe distinguir explícitamente** entre *vacaciones compensadas por acuerdo mutuo* (Art. 189, periodo vigente) y *vacaciones obligatoriamente compensadas en finiquito* (Art. 189 párr. 1° + Art. 190, terminación del contrato) — el modo `FINIQUITO` invoca `calculate_vacaciones_compensadas_finiquito` y el modo `PERIODICA` NO la invoca; (c) **Indemnización Art. 64 CST NO se implementa en v2.0** (queda referenciada y documentada en el addendum y en `Contexto/KB_LLM/01_reglas_calculo.md` para casos futuros de despido sin justa causa). **Regresión dura:** el caso canónico PERIODICA (SBL 2.200.000, 206d, dos segmentos, sin `motivo_terminacion`, sin `vacaciones`) **sigue verde** — los nuevos campos son retrocompatibles (opcionales o con default seguro). |

Si alguna de estas decisiones cambia, **el plan debe actualizarse en consecuencia** y la KB (`00_fuente_de_verdad.md` y `09_caso_canonico_usuario.md`) debe reflejarlo.

---

*Plan elaborado el 2026-06-09 a partir del diagnóstico `Contexto/diagnostico_liquidacion_cli_2026-06-09.md`. Cualquier contradicción entre este plan y el código vivo se resuelve a favor del código (regla §5.5.11 del diagnóstico).*
