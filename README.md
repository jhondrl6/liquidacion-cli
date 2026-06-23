# `liquidacion-cli` v2.0

CLI local para liquidación de prestaciones sociales y nómina colombiana. Calcula liquidaciones periódicas, de finiquito y de vacaciones conforme al CST 2025-2026, ejecuta un motor de compliance con 15 reglas (V001-V015) y emite tres artefactos por ejecución: JSON + Markdown + PDF.

> **v2.0.0** — release estabilizado. La rama es `master`. Para el detalle histórico del proyecto ver `Planificación/plan_modernizacion_v2.0_2026-06-09.md` y `Planificación/REGISTRY.md`.

---

## ¿Qué es?

- **CLI local, usuario único, sin servidor.** Pensado para correr en una máquina de trabajo con acceso a `params/` y al caso canónico versionado.
- **Motor de liquidación de prestaciones** que implementa: cesantías, intereses sobre cesantías, prima de servicios, vacaciones, indemnización por despido (Art. 64 CST — referenciada), vacaciones compensadas en finiquito (Art. 189-190 CST), indemnización por preaviso en contratos a término fijo (Art. 46 CST) e indexación IPC de prestaciones prescritas (SL2630-2024 + Art. 488 CST).
- **Motor de compliance declarativo** alimentado por `params/checklist.json` (15 reglas V001-V015 con `severity` y `blocking`). Estados posibles: `GO`, `WARN` (soportado en schema por retrocompatibilidad), `NO_GO`, `OVERRIDE_APPROVED`. El CHANGELOG v2.0 documenta WARN como "eliminado" en favor de `GO` con sección de advertencias; el Literal de Pydantic aún lo acepta.
- **Segundo cerebro local** en `Contexto/KB_LLM/` (11 notas sustantivas, 00-09) que documenta reglas de cálculo, params vigentes, compliance, riesgos conocidos y el caso canónico.
- **Auditoría inmutable por ejecución** en `audit/<timestamp>_<hash>.json` con `params_hash`, `input_hash`, `output_hash`, reglas aplicadas, warnings y overrides.

## ¿Qué NO es?

- **No es una API ni servicio web.** No expone endpoints, ni HTTP, ni gRPC.
- **No es multiusuario ni SaaS.** Es una herramienta de escritorio / CLI para un solo operador.
- **No usa LLM comercial en la nube.** Ningún cálculo depende de un LLM remoto.
- **No es un sistema contable.** No lleva libros, ni PUC, ni retenciones en la fuente automáticas.
- **No reemplaza asesoría jurídica o contable profesional.** Es una herramienta de cálculo y auditoría. Ver [Disclaimer legal](#disclaimer-legal).

---

## Requisitos

- **Python ≥ 3.11** (desarrollado y verificado en 3.12)
- `pip` o [`uv`](https://docs.astral.sh/uv/) (recomendado)
- En WSL: el sandbox bloquea `python3` directo — usar `uv run --with <pkg> python3 <script>` (ver `AGENTS.md` regla de operación).

## Instalación

### Opción A — `pip` editable (recomendado para desarrollo)

```bash
git clone https://github.com/jhondrl6/liquidacion-cli.git
cd liquidacion-cli
pip install -e .
# opcional: dependencias de desarrollo
pip install -e ".[dev]"
```

El entry point `liquidacion` queda disponible en el `PATH`.

### Opción B — `uv tool install` (instalación aislada)

```bash
git clone https://github.com/jhondrl6/liquidacion-cli.git
cd liquidacion-cli
uv tool install .
```

El binario `liquidacion` queda en `~/.local/bin/`.

### Verificación post-instalación

```bash
liquidacion --version   # debe imprimir 2.0.0
liquidacion --help
```

---

## Uso

```text
liquidacion [SUBCOMANDO] [OPCIONES] [ARGUMENTOS]

Subcomandos:
  liquidar     Liquida a partir de un JSON de entrada. Genera artefactos.
  validate     Valida un JSON de entrada sin ejecutar el motor.
  info         Muestra parámetros vigentes y estado del sistema.

Opciones globales:
  --version    Imprime la versión (2.0.0) y sale.
  --help       Muestra la ayuda del subcomando.
```

### `liquidacion liquidar` — ejecutar una liquidación

```bash
# Caso canónico (206d, 2 segmentos, SBL $2.200.000)
liquidacion liquidar examples/inputs/caso_canonico_periodico_206d.json

# Renuncia con vacaciones compensadas (Art. 189 CST)
liquidacion liquidar examples/inputs/finiquito_renuncia_212d.json

# Finiquito en contrato a término fijo vencido, sin preaviso (Art. 46)
liquidacion liquidar examples/inputs/finiquito_fijo_vencido_preaviso.json

# Indexación IPC de cesantías prescritas (SL2630-2024 + Art. 488)
liquidacion liquidar examples/inputs/prescripcion_indexada.json

# Salida a directorio específico, solo JSON por stdout
liquidacion liquidar examples/inputs/caso_canonico_periodico_206d.json \
    --out-dir output/mi_caso --json-only

# Override de un fallo HIGH (registrado en auditoría)
liquidacion liquidar examples/inputs/caso_canonico_periodico_206d.json \
    --override --override-reason "Decisión documentada en caso X"
```

**Artefactos generados** en `--out-dir` (default: `output/`):

| Estado compliance | Archivos emitidos | Exit code | PDF |
|---|---|---|---|
| `GO` / `WARN` / `OVERRIDE_APPROVED` | `liquidacion.json` | `0` | no (CLI solo emite JSON; el `PDFGenerator` se invoca programáticamente — ver `bin/liquidar.py`) |
| `NO_GO` | `liquidacion_BLOQUEADA.json` + `liquidacion_BLOQUEADA.md` | `2` | **no** (regla AGENTS.md #7) |

> Hay además un wrapper legacy en `bin/liquidar.py` (argparse, ASCII-only, sin subcomandos) que invoca el motor y emite PDF directamente. Conservar solo para flujos que requieren PDF sin orquestar el CLI nuevo.

### `liquidacion validate` — validar entrada sin calcular

```bash
liquidacion validate examples/inputs/test_minimo_valid.json --params-year 2025
# Imprime campos requeridos, modo, fechas, advertencias; sale con código 0.
```

### `liquidacion info` — parámetros y estado del sistema

```bash
liquidacion info                # muestra params de 2025 y 2026
liquidacion info --year 2026    # muestra solo el año indicado
```

---

## Caso canónico

El **ancla de validación continua** del proyecto. Debe poder ejecutarse y verificarse en cada fase cerrada (regla del plan §3).

**Entrada** (`examples/inputs/caso_canonico_periodico_206d.json`):

```json
{
  "trabajador": {"nombre": "[ANONIMIZADO]", "documento": "[ANONIMIZADO]"},
  "empleador":  {"nombre": "[ANONIMIZADO]", "documento": "[ANONIMIZADO]"},
  "contrato":   {"fecha_ingreso": "2025-11-16", "fecha_corte": "2026-06-09",
                 "tipo": "INDEFINIDO", "fecha_terminacion_real": null},
  "salario":    {"SBL": 2200000, "auxilio_transporte": false, "variable": false},
  "modo":       "PERIODICA",
  "segmentos": [
    {"anio": 2025, "desde": "2025-11-16", "hasta": "2025-12-31", "params_ref": "params/2025.json"},
    {"anio": 2026, "desde": "2026-01-01", "hasta": "2026-06-09", "params_ref": "params/2026.json"}
  ]
}
```

**Datos derivados**:

- 206 días en dos segmentos: 2025-H2 (46d) + 2026-H1 (160d)
- SBL constante: `$2.200.000` (no afectado por cambios de SMMLV)
- Modo: `PERIODICA`
- Parametría por segmento: `params/2025.json` (D. 1572/2024) y `params/2026.json` (D. 159/2026, D. 1469/2025 suspendido provisionalmente — ver `R-LEG-07` en KB)

**Salida esperada** (shape de `liquidacion.json`):

```json
{
  "meta": {
    "modo": "PERIODICA",
    "fecha_generacion": "<ISO-8601>",
    "params_version": "2025-10-31",
    "parametros_por_segmento": {"2025": "2025-10-31", "2026": "2026-06-09"}
  },
  "trabajador": {...},
  "parametros": {
    "SMMLV": 1423500, "AUXILIO_TRANS": 200000,
    "LIMITE_AUXILIO": 2847000, "TASA_INT_CESANTIAS": 0.12
  },
  "desglose": {
    "SBL_GENERAL": 2200000,
    "cesantias": {"valor": 281111, "dias_liquidados": 46, "anio": 2025, "norma": "Art.249-250 CST"},
    "cesantias": {"valor": 977778, "dias_liquidados": 160, "anio": 2026, "norma": "Art.249-250 CST"},
    "prima":  {"valor_h2_2025": ..., "valor_h1_2026": ..., "norma": "Art.306-308 CST"},
    "intereses_cesantias": {"valor": ..., "norma": "Ley 50/1990 Art.99"},
    "vacaciones": null
  },
  "total_liquidacion": { "...": "suma de renglones" },
  "validaciones_y_alertas": [...],
  "normas_aplicadas": [...],
  "compliance_report": {
    "compliance_status": "GO",
    "summary": {"passed": 15, "warnings": 0, "failures": 0}
  }
}
```

> Los valores numéricos exactos se generan por el motor (Tarea 1.D) y se validan contra los golden tests en `liquidator/tests/test_golden/`. Si los params anuales cambian, se regenera el golden file.

---

## Estructura del proyecto

```text
liquidacion_cli/
├── pyproject.toml                 # PEP 621, version 2.0.0, entry point "liquidacion"
├── AGENTS.md                      # Jerarquía de verdad + 12 reglas inamovibles (para agentes)
├── README.md                      # Este archivo
├── CHANGELOG.md                   # Entrada v2.0 con breaking changes
├── DISCLAIMER.md                  # Disclaimer legal completo
├── liquidator/                    # Paquete principal
│   ├── __init__.py                # __version__ = "2.0.0"
│   ├── cli/main.py                # Entry point Click (liquidar/validate/info)
│   ├── contracts/                 # Schemas Pydantic v2 (input_model, output_model, document_context)
│   ├── core/                      # Motor (engine, input_parser, params_provider, salario_resolver, workflow_orchestrator)
│   ├── calculators/               # prestaciones, indemnizacion, sbl, indexacion, vacaciones, preaviso
│   ├── compliance/                # Motor de compliance (rule_evaluator, reglas V001-V015)
│   ├── validators/                # Validación de entrada
│   ├── legal/                     # Normas, plazos, topes
│   ├── output/                    # Generadores JSON, Markdown, PDF
│   ├── audit/                     # Auditoría inmutable (logger, hash, trail, versioning)
│   ├── templates/                 # Plantillas .md con bloques Jinja (comprobante_periodica, comprobante_finiquito, partials/, styles/)
│   └── tests/                     # 13 categorías de tests (audit, calculators, cli, compliance, contracts, core, golden, integration, legal, output, params, utils, validators + test_kb_freshness.py standalone)
├── params/
│   ├── 2025.json                  # SMMLV, aux_trans, topes (Decreto 1572/2024)
│   ├── 2026.json                  # (Decreto 159/2026; D. 1469/2025 suspendido — R-LEG-07)
│   ├── normas.json                # Citas legales con URL SUIN y estado_verificacion
│   ├── plazos.json                # Plazos de pago por concepto
│   ├── checklist.json             # 15 reglas V001-V015 (severity + blocking)
│   ├── schema.json                # JSON Schema legacy (en transición a Pydantic)
│   ├── ipc_dane_mensual.json      # 204 índices IPC DANE (base 100 en 2010-01)
│   └── ipc_variacion_anual_dane.csv
├── examples/
│   ├── inputs/                    # 6 casos de prueba documentados
│   └── expected/                  # Golden files de salida esperada
├── Contexto/
│   ├── KB_LLM/                    # Segundo cerebro local (11 notas)
│   │   ├── 00_fuente_de_verdad.md
│   │   ├── 01_reglas_calculo.md
│   │   ├── 02_parametros_vigentes.md
│   │   ├── 03_compliance_blocking.md
│   │   ├── 04_schema_entrada.md
│   │   ├── 05_plantillas.md
│   │   ├── 05_schema_salida.md
│   │   ├── 06_riesgos_modelo.md
│   │   ├── 07_checklist_generacion_liquidacion.md
│   │   ├── 08_arquitectura_segundo_cerebro.md
│   │   └── 09_caso_canonico_usuario.md
│   └── prompts/                   # Prompts base para agentes
├── Planificación/
│   ├── plan_modernizacion_v2.0_2026-06-09.md  # Plan completo (~4.000 líneas)
│   ├── REGISTRY.md                # Estado actual + tabla de fases
│   ├── REGISTRY_LOG.md            # Histórico de cierres de sesión (archivado)
│   ├── addendum_sl2630_y_ipc_2026-06-09.md
│   ├── addendum_finiquito_renuncia_vacaciones_2026-06-11.md
│   └── addendum_fase3_arquitectura_2026-06-14.md
├── scripts/
│   ├── ci.sh                      # CI local (compileall + ruff + pytest + kb_freshness)
│   ├── check_kb_freshness.py      # Validador de freshness de KB
│   ├── build_ipc_index.py         # Generador/validador de IPC DANE
│   └── update_params.py           # Utilidad de actualización de params
├── .github/workflows/ci.yml       # CI GitHub Actions
├── audit/                         # Auditoría inmutable por ejecución (gitignored)
├── output/                        # Artefactos generados (gitignored)
├── artifacts/                     # Auditoría operativa (gitignored)
├── docs/                          # Docs generadas / históricas (no fuente de verdad)
└── config/                        # Configuración YAML legacy (en transición)
```

---

## Cómo correr los tests

### Suite completa

```bash
# Con uv (recomendado en WSL por sandbox)
PYTHONPATH=. uv run --with pytest --with python-dateutil --with PyYAML \
  --with jsonschema --with pydantic --with loguru --with click \
  --with markdown --with Jinja2 \
  pytest liquidator/tests -q

# Con pip editable
pip install -e ".[dev]"
pytest liquidator/tests -q
```

Baseline al cierre de Fase 4 (S38): **650 passed / 42 failed / 1 xfail / 15 errors** (los 42 fallos y 15 errores son preexistentes de fases previas, asignados a bugs heredados; ver `Planificación/REGISTRY.md` §Pendientes).

### Suites específicas

```bash
# Compliance
pytest liquidator/tests/test_compliance -q

# Golden tests (caso canónico + casos reales)
pytest liquidator/tests/test_golden -q

# Schemas Pydantic
pytest liquidator/tests/test_contracts -q

# Calculadores legales
pytest liquidator/tests/test_calculators -q

# CLI
pytest liquidator/tests/test_cli -q
```

### Checks de calidad

```bash
python3 -m compileall -q liquidator    # 0 errores de sintaxis
ruff check liquidator                  # 0 errores (S38: 1143→0)
python3 scripts/check_kb_freshness.py  # KB no stale
```

### CI local (sin GitHub Actions)

```bash
bash scripts/ci.sh
```

Equivalente local al workflow `.github/workflows/ci.yml`: compileall + ruff + pytest + kb_freshness.

---

## Cómo contribuir

Este proyecto sigue la **convención 1 fase por sesión** (plan §4). Cada sesión cierra como máximo una fase y produce:

1. **Validación del DoD contra código vivo** (regla §5.5.11 del diagnóstico: si código y plan discrepan, código gana).
2. **Actualización de `Planificación/REGISTRY.md`** — estado, fase, log de cierre.
3. **Entrada en `CHANGELOG.md`** bajo `[Unreleased]` si se cerró una fase.
4. **Sincronización de `Contexto/KB_LLM/`** si hubo cambio en `params/` o reglas.
5. **Verificación del addenda** correspondiente si se tocó su alcance.

### Antes de empezar

1. Leer `Planificación/REGISTRY.md` (sección "Handoff", 8 checks).
2. Leer `AGENTS.md` (12 reglas inamovibles + trampas conocidas).
3. Si la tarea toca cálculo o compliance → leer `Contexto/KB_LLM/01_reglas_calculo.md` y `03_compliance_blocking.md`.
4. Si la tarea toca input/salida → leer `04_schema_entrada.md` y `05_plantillas.md`.
5. Si la tarea toca riesgos → leer `06_riesgos_modelo.md`.

### Al cerrar sesión

Ejecutar los 5 pasos de cierre documentados en `Planificación/REGISTRY.md` §"Regla de cierre de sesión". **No cerrar sesión sin completarlos.**

### Convenciones de código

- **Python 3.11+**, type hints obligatorios en código nuevo.
- **Pydantic v2** para todos los modelos de entrada/salida.
- **Click** para el CLI (no Typer, no argparse).
- **Jinja2** dentro de plantillas `.md` (no archivos `.j2` separados — divergencia D1 documentada en `addendum_fase3_arquitectura_2026-06-14.md`).
- **No hardcodear** SMMLV, aux_trans, tasas ni plazos. Todo va en `params/<año>.json`.
- **No incluir PII real** (nombres, documentos, salarios) en ejemplos, tests, KB ni logs.
- **pytest** como framework; los tests viven junto al código en `liquidator/tests/`.

---

## Disclaimer legal

> **Esta herramienta es de carácter informativo y de apoyo al cálculo.**
> No constituye asesoría jurídica, contable, tributaria ni financiera.
> Las fórmulas implementadas reflejan la normatividad laboral colombiana
> vigente al momento del release (CST, Ley 50/1990, Ley 2466/2025,
> decretos anuales del SMMLV y auxilio de transporte, SL2630-2024),
> pero pueden no cubrir la totalidad de situaciones particulares
> (convenciones colectivas, regímenes de excepción, sentencias
> judiciales posteriores al release).
>
> **El uso de esta herramienta es responsabilidad exclusiva del usuario.**
> Antes de tomar decisiones con efectos legales o patrimoniales, valide
> los resultados con un profesional habilitado (abogado laboralista,
> contador, revisor fiscal) y contraste con la normatividad vigente en
> [`www.suin-juriscol.gov.co`](https://www.suin-juriscol.gov.co/).
>
> Ver el disclaimer completo en [`DISCLAIMER.md`](./DISCLAIMER.md).

---

## Licencia

MIT — ver [`LICENSE`](./LICENSE).

## Referencias

- **Plan de modernización v2.0:** [`Planificación/plan_modernizacion_v2.0_2026-06-09.md`](./Planificación/plan_modernizacion_v2.0_2026-06-09.md)
- **Estado del proyecto:** [`Planificación/REGISTRY.md`](./Planificación/REGISTRY.md)
- **Reglas para agentes:** [`AGENTS.md`](./AGENTS.md)
- **Segundo cerebro local:** [`Contexto/KB_LLM/`](./Contexto/KB_LLM/)
- **Diagnóstico fuente (2026-06-09):** `docs/audit/diagnosticos/diagnostico_inicial_2026-06-09.md`
- **Repositorio:** [github.com/jhondrl6/liquidacion-cli](https://github.com/jhondrl6/liquidacion-cli)

---

**Versión:** 2.0.0
**Última actualización del README:** ver `git log -1 -- README.md`
