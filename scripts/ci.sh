#!/usr/bin/env bash
# CI local — equivalente a .github/workflows/ci.yml para entornos sin GitHub.
# Ejecutar desde la raíz del proyecto.
set -euo pipefail

echo "=== 1/5 Compile check ==="
python3 -m compileall liquidator

echo "=== 2/5 Lint (ruff) ==="
uv run --with ruff ruff check liquidator/

echo "=== 3/5 Type check (mypy) ==="
uv run --with mypy mypy liquidator/ --ignore-missing-imports || true

echo "=== 4/5 Tests (pytest) ==="
uv run --with pytest --with python-dateutil --with PyYAML \
  --with jsonschema --with pydantic --with loguru --with click \
  --with markdown --with Jinja2 --with pytest-cov \
  python3 -m pytest liquidator/tests -q --tb=short

echo "=== 5/5 KB freshness ==="
python3 scripts/check_kb_freshness.py

echo "=== CI local: OK ==="
