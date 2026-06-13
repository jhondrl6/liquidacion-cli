#!/usr/bin/env python3
"""KB freshness check.

Sale con código != 0 si encuentra desactualizaciones críticas entre:

  * `params/<año>.json` (SMMLV, auxilio_trans) y
    `Contexto/KB_LLM/02_parametros_vigentes.md`.
  * 10 notas KB presentes en `Contexto/KB_LLM/` (00-09).
  * `AGENTS.md` referenciando el diagnóstico vigente.

Es year-aware: itera sobre todos los `params/<YYYY>.json` presentes, de
modo que añadir `2027.json` (o cualquier año futuro) no requiere tocar
este script. La KB debe ser el archivo "02_parametros_vigentes.md"
(Tarea 0.K); se acepta el nombre legado "02_parametros_2025.md" (Tarea
0.E) por retro-compat.

Comparación de números: se ignoran separadores de miles (puntos/comas),
espacios y '$' para que `1423500` matchee tanto `1.423.500` (formato
local colombiano) como `1,423,500` como `1423500` (raw).

Uso::

    python3 scripts/check_kb_freshness.py        # exit 0 si todo OK
    echo $?                                       # 0 = fresco, 1 = desactualizado

Exit codes:
    0 — KB fresca.
    1 — Una o más desactualizaciones críticas; detalles en STDERR.
    2 — Error de E/S inesperado (params corrupto, KB inaccesible, etc.).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
KB = REPO / "Contexto" / "KB_LLM"
PARAMS = REPO / "params"
AGENTS = REPO / "AGENTS.md"
DIAGNOSTICO = "diagnostico_liquidacion_cli_2026-06-09.md"

# Acepta nombre "vigentes" (Tarea 0.K) o legado "2025" (Tarea 0.E).
KB_02_CANDIDATES = (
    KB / "02_parametros_vigentes.md",
    KB / "02_parametros_2025.md",
)

# Campos monetarios grandes a contrastar contra la KB. Tasas (0.12) y
# plazos pequeños se omiten a propósito: aparecen en prosa con formato
# variable y los falsos positivos superarían las capturas reales.
KB_RELEVANT_FIELDS = ("SMMLV", "AUXILIO_TRANS")

# 4 dígitos + .json → params/<año>.json. Filtra normas.json, plazos.json,
# schema.json, checklist.json, Respuestas.md.
PARAMS_GLOB = "[0-9][0-9][0-9][0-9].json"

# 10 notas de KB (00-09). Una por área funcional; ver plan §5.2 T0.E.
KB_NOTE_COUNT = 10


def _normalize_for_search(text: str) -> str:
    """Quita separadores de miles (puntos/comas), espacios y '$' para
    que '1423500' matchee '1.423.500', '1,423,500' y '1423500'."""
    return re.sub(r"[.,\s\$]", "", text)


def _find_kb_02() -> Path | None:
    for p in KB_02_CANDIDATES:
        if p.exists():
            return p
    return None


def _check_params_against_kb(kb_text: str) -> list[str]:
    """Verifica que cada `params/<YYYY>.json` tenga su SMMLV y
    AUXILIO_TRANS citados (en cualquier formato de número) en la KB."""
    errors: list[str] = []
    norm_kb = _normalize_for_search(kb_text)
    params_files = sorted(PARAMS.glob(PARAMS_GLOB))
    if not params_files:
        errors.append(
            f"No hay params/<año>.json en {PARAMS} (se esperaba al menos 2025/2026)"
        )
        return errors
    for params_file in params_files:
        try:
            data = json.loads(params_file.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"No se pudo leer {params_file.name}: {exc}")
            continue
        anio = params_file.stem
        for field in KB_RELEVANT_FIELDS:
            val = data.get(field)
            if val is None:
                # Campo ausente en params — no es bug de KB, es bug de params.
                errors.append(
                    f"params/{anio}.json no trae campo {field}; agregalo"
                )
                continue
            val_norm = _normalize_for_search(str(val))
            if not val_norm:
                continue
            if val_norm not in norm_kb:
                errors.append(
                    f"KB_LLM/02 no refleja {field}={val} de params/{anio}.json"
                )
    return errors


def _check_kb_notes_present() -> list[str]:
    """Las 10 notas KB (00..09) deben existir en Contexto/KB_LLM/."""
    errors: list[str] = []
    for i in range(KB_NOTE_COUNT):
        if not list(KB.glob(f"{i:02d}_*.md")):
            errors.append(f"Falta nota KB {i:02d}_*.md en {KB}")
    return errors


def _check_agents_references_diagnostico() -> list[str]:
    """AGENTS.md (regla de oro del proyecto) debe apuntar al diagnóstico
    vigente para que cualquier agente que abra el proyecto sepa dónde
    está el mapa de riesgos."""
    if not AGENTS.exists():
        return [f"AGENTS.md no existe en raíz ({AGENTS})"]
    agents_text = AGENTS.read_text()
    if DIAGNOSTICO not in agents_text:
        return [f"AGENTS.md no referencia el diagnóstico vigente ({DIAGNOSTICO})"]
    return []


def main() -> int:
    errors: list[str] = []

    kb_02 = _find_kb_02()
    if kb_02 is None:
        candidates = ", ".join(p.name for p in KB_02_CANDIDATES)
        errors.append(f"KB_LLM/02 ({candidates}) no existe")
        kb_text = ""
    else:
        kb_text = kb_02.read_text()
        errors.extend(_check_params_against_kb(kb_text))

    errors.extend(_check_kb_notes_present())
    errors.extend(_check_agents_references_diagnostico())

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print("KB fresh.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
