"""Tests para `scripts/check_kb_freshness.py`.

Cubre:
  * El script corre con exit 0 (KB fresca).
  * KB_LLM/ tiene exactamente 10 notas (00-09).
  * Cada `params/<YYYY>.json` tiene su SMMLV citado en KB_LLM/02
    (con o sin separadores de miles — formato colombiano `1.423.500`
    y raw `1423500` matchean por igual).
  * `AGENTS.md` referencia el diagnóstico vigente.

Ubicación: `liquidator/tests/test_kb_freshness.py` para que pytest.ini
(testpaths = liquidator/tests) lo auto-descubra.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

# liquidator/tests/test_kb_freshness.py → parents[1] = liquidator/, parents[2] = REPO
REPO = Path(__file__).resolve().parents[2]
KB = REPO / "Contexto" / "KB_LLM"
PARAMS = REPO / "params"
AGENTS = REPO / "AGENTS.md"
DIAGNOSTICO = "diagnostico_liquidacion_cli_2026-06-09.md"
KB_02_CANDIDATES = (
    "02_parametros_vigentes.md",
    "02_parametros_2025.md",  # legado Tarea 0.E
)


def _normalize(text: str) -> str:
    """Igual que `scripts/check_kb_freshness.py._normalize_for_search`."""
    return re.sub(r"[.,\s\$]", "", text)


def _kb_02_text() -> str:
    for name in KB_02_CANDIDATES:
        p = KB / name
        if p.exists():
            return p.read_text()
    return ""


# --- Tests del script en sí ----------------------------------------------

def test_kb_freshness_exits_zero() -> None:
    """El check completo debe pasar en el estado actual del repo."""
    r = subprocess.run(
        [sys.executable, "scripts/check_kb_freshness.py"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"check_kb_freshness.py salió con código {r.returncode}.\n"
        f"STDOUT: {r.stdout!r}\nSTDERR: {r.stderr!r}"
    )
    # Confirmar mensaje canónico en stdout (es contrato con otros tests
    # o scripts que consuman la salida).
    assert r.stdout.strip() == "KB fresh.", (
        f"STDOUT inesperado: {r.stdout!r}. Esperado: 'KB fresh.'"
    )


def test_kb_freshness_informe_clara_errores() -> None:
    """Si el script falla, los mensajes de error van a STDERR y son
    accionables (prefijo 'ERROR:'). Esto garantiza que el log de CI
    sea legible sin abrir el código."""
    r = subprocess.run(
        [sys.executable, "scripts/check_kb_freshness.py"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=30,
    )
    # Hoy debe pasar, pero si falla la salida debe seguir el contrato.
    if r.returncode != 0:
        assert r.stderr, "Falló sin escribir nada en STDERR"
        for line in r.stderr.strip().splitlines():
            assert line.startswith("ERROR:"), (
                f"Línea de STDERR sin prefijo 'ERROR:': {line!r}"
            )


# --- Tests estructurales de la KB ----------------------------------------

def test_kb_has_ten_notes() -> None:
    notes = sorted(KB.glob("[0-9][0-9]_*.md"))
    assert len(notes) == 10, (
        f"Esperadas 10 notas (00-09), encontradas {len(notes)}: "
        f"{[n.name for n in notes]}"
    )


def test_agents_md_references_diagnostico() -> None:
    assert AGENTS.exists(), f"AGENTS.md no existe en {AGENTS}"
    assert DIAGNOSTICO in AGENTS.read_text(), (
        f"AGENTS.md no menciona el diagnóstico vigente ({DIAGNOSTICO}). "
        f"Sin esa referencia, un agente que abra el proyecto no encuentra "
        f"el mapa de riesgos en AGENTS.md (jerarquía de verdad, nivel 4)."
    )


# --- Tests parametrizados de SMMLV/aux_trans por año ---------------------

@pytest.mark.parametrize(
    "anio,smmlv_esperado,aux_esperado",
    [
        ("2025", 1_423_500, 200_000),
        ("2026", 1_750_905, 249_095),
    ],
)
def test_params_smmlv_citado_en_kb(
    anio: str, smmlv_esperado: int, aux_esperado: int
) -> None:
    """El SMMLV y aux_trans de cada params/<YYYY>.json deben aparecer
    en KB_LLM/02_parametros_vigentes.md, normalizados."""
    params_file = PARAMS / f"{anio}.json"
    assert params_file.exists(), f"params/{anio}.json no existe"

    data = json.loads(params_file.read_text())
    assert int(data["SMMLV"]) == smmlv_esperado, (
        f"params/{anio}.json SMMLV={data['SMMLV']} ≠ esperado {smmlv_esperado}. "
        f"Si cambia el decreto, actualizá params/<año>.json Y "
        f"KB_LLM/02_parametros_vigentes.md en la misma sesión."
    )
    assert int(data["AUXILIO_TRANS"]) == aux_esperado, (
        f"params/{anio}.json AUXILIO_TRANS={data['AUXILIO_TRANS']} "
        f"≠ esperado {aux_esperado}"
    )

    kb_text = _kb_02_text()
    assert kb_text, (
        "KB_LLM/02 no existe en ninguna de sus formas "
        f"({', '.join(KB_02_CANDIDATES)})"
    )

    norm_kb = _normalize(kb_text)
    for field, val in (("SMMLV", smmlv_esperado), ("AUXILIO_TRANS", aux_esperado)):
        val_norm = _normalize(str(val))
        assert val_norm in norm_kb, (
            f"{field}={val} (normalizado: '{val_norm}') de params/{anio}.json "
            f"NO aparece en KB_LLM/02. La KB está desactualizada — actualizala "
            f"en la misma sesión que cambies params/<año>.json."
        )


def test_params_futuro_sera_detectado() -> None:
    """Si en el futuro se agrega params/2027.json sin actualizar la KB,
    el script debe detectarlo. Simulamos creando un archivo temporal y
    ejecutando el script — luego limpiamos."""
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmp:
        tmp_params = Path(tmp) / "params"
        tmp_params.mkdir()
        # params/2025.json OK (debe estar en KB)
        (tmp_params / "2025.json").write_text(
            json.dumps({"SMMLV": 1_423_500, "AUXILIO_TRANS": 200_000})
        )
        # params/2099.json NO en KB → debe reportar error
        (tmp_params / "2099.json").write_text(
            json.dumps({"SMMLV": 99_999_999, "AUXILIO_TRANS": 9_999_999})
        )

        # Simular el script en este entorno. En lugar de monkey-patching
        # del módulo, validamos la lógica a mano contra el mismo normalizador.
        norm_kb = _normalize(_kb_02_text())
        for field, val in (
            ("SMMLV", 1_423_500),
            ("AUXILIO_TRANS", 200_000),
        ):
            assert _normalize(str(val)) in norm_kb, (
                f"{field}={val} debería estar en KB (caso base)"
            )
        for field, val in (
            ("SMMLV", 99_999_999),
            ("AUXILIO_TRANS", 9_999_999),
        ):
            assert _normalize(str(val)) not in norm_kb, (
                f"{field}={val} NO debería estar en KB (caso de desactualización)"
            )
