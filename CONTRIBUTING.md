# Contributing to liquidacion_cli

> CLI local de liquidación de prestaciones sociales con segundo cerebro local.
> v2.0.0 · Python 3.12+ · WSL

## Cómo contribuir

### 1. Clonar y preparar el entorno

```bash
git clone <repo-url>
cd liquidacion_cli
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

### 2. Reglas inamovibles

Antes de tocar código, leé `AGENTS.md` — define la jerarquía de verdad y las
12 reglas operativas. Resumen:

- **No hardcodear** SMMLV, auxilio de transporte, límites, tasas ni plazos.
  Todo parámetro se lee de `params/<año>.json`, `params/normas.json` o
  `params/plazos.json`.
- **Verificar contra código vivo** antes de aceptar cualquier afirmación
  de la documentación. Si código y docs discrepan, **gana el código**.
- **No generar PDF si compliance = `NO_GO`** (AGENTS.md regla #7).
- **Toda regla legal nueva debe tener evidencia** en `legal_docs/` o cita
  verificada en SUIN (`https://www.suin-juriscol.gov.co/`).
- **Una fase por sesión** — convención del proyecto.

### 3. Flujo de trabajo

1. **Leé el REGISTRY** (`Planificación/REGISTRY.md`) para saber el estado
   actual y la próxima tarea pendiente.
2. **Ejecutá el caso canónico** como prueba de cordura antes de cualquier
   cambio:
   ```bash
   python -m liquidator.cli liquidar examples/inputs/caso_canonico_periodico_206d.json
   ```
3. **Hacé el cambio** siguiendo la fase/tarea del plan
   (`Planificación/plan_modernizacion_v2.0_2026-06-09.md`).
4. **Corré la suite completa** — debe pasar al 100% antes de cerrar:
   ```bash
   uv run --with pytest --with python-dateutil --with PyYAML \
     --with jsonschema --with pydantic --with loguru --with click \
     --with markdown --with Jinja2 pytest liquidator/tests -q
   ```
5. **Corré CI local**:
   ```bash
   bash scripts/ci.sh
   ```
6. **Actualizá REGISTRY.md** al cerrar la sesión (sección "Regla de cierre").
7. **Si cerrás una fase**, agregá entrada en `CHANGELOG.md` bajo
   `[Unreleased]`.

### 4. Estructura del proyecto

```
liquidacion_cli/
├── AGENTS.md                  # Jerarquía de verdad + reglas para agentes
├── README.md                  # Contrato v2.0
├── CHANGELOG.md               # Historial de versiones
├── pyproject.toml             # Empaquetado PEP 621
├── pytest.ini                 # Configuración de pytest
├── liquidator/                # Código fuente
│   ├── cli/                   # Entry point (Click/Typer)
│   ├── core/                  # Motor de liquidación
│   ├── calculators/           # Cálculos legales
│   ├── contracts/             # Schemas Pydantic (input/output)
│   ├── compliance/            # Motor de compliance + rule evaluator
│   ├── output/                # Generadores JSON/MD/PDF
│   ├── audit/                 # Trazabilidad inmutable
│   ├── templates/             # Plantillas Jinja2 (Markdown)
│   └── tests/                 # Suite de tests (13 categorías)
├── params/                    # Parámetros versionados (SMMLV, normas, plazos, IPC)
├── Contexto/                  # KB local + diagnóstico
│   └── KB_LLM/                # 11 notas de conocimiento
├── examples/                  # Inputs y golden files
├── scripts/                   # Utilidades (CI, freshness, build IPC)
└── Planificación/             # Plan v2.0 + REGISTRY + addenda
```

### 5. Convenciones

- **Python 3.12**. Tipado con Pydantic v2 para schemas de entrada/salida.
- **Pytest** para tests. Usar `uv run --with pytest` en WSL (sandbox).
- **ruff** para linting y formato (configurado en `pyproject.toml`).
- **mypy** para type checking estático.
- **Commit messages**: subject < 100 chars (limitación WSL sandbox).
  Detalle extendido en REGISTRY/CHANGELOG.
- **No incluir datos sensibles** (nombres reales, documentos, salarios)
  en el repo, KB, logs o tests. Usar `[ANONIMIZADO]` o datos sintéticos.
- **Prescripción de prestaciones = Art. 488 CST**, NO Art. 155.
- **Indemnización Art. 64 CST** NO está implementada en v2.0.

### 6. Preguntas frecuentes

**¿Cómo ejecuto un solo archivo de tests?**
```bash
uv run --with pytest --with python-dateutil --with PyYAML \
  --with jsonschema --with pydantic --with loguru --with click \
  --with markdown --with Jinja2 pytest liquidator/tests/test_calculators/test_prestaciones.py -q
```

**¿Cómo verifico que la KB está fresca?**
```bash
python3 scripts/check_kb_freshness.py
```

**¿Cómo sé qué parámetros están vigentes?**
Revisá `params/2025.json`, `params/2026.json`, `params/normas.json` y
`params/plazos.json`. La KB (`Contexto/KB_LLM/02_parametros_vigentes.md`)
tiene un resumen legible.

**¿Qué hago si un test de compliance falla?**
Revisá `params/checklist.json` — las reglas CRITICAL y HIGH bloquean.
Usá `--override --override-reason "motivo"` si es un override aprobado.

---

Ver también: `README.md`, `AGENTS.md`, `CHANGELOG.md`, `DISCLAIMER.md`.
