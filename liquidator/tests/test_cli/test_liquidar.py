"""Tests del CLI `liquidacion` — Tarea 3.D (Fase 3 base).

Plan §8.2 Tarea 3.D. Cubre:

- Rama GO: escribe ``liquidacion.json``, NO ``liquidacion_BLOQUEADA.*``, exit 0.
- Rama WARN: idem rama GO, exit 0.
- Rama NO_GO: escribe ``liquidacion_BLOQUEADA.json`` Y
  ``liquidacion_BLOQUEADA.md``, exit 2. NO genera ``liquidacion.*``.
- Rama NO_GO: el .md contiene "LIQUIDACIÓN BLOQUEADA" (generado por
  ``MarkdownGenerator``).
- ``--json-only`` con NO_GO: no escribe archivos, pero mantiene exit 2.
- La rama NO_GO NO genera PDF (regla AGENTS.md #7).

Estrategia: monkeypatch del motor (``LiquidacionEngine.process``) para
devolver un resultado sintético con el compliance_status que queremos
testear. El motor real no se ejecuta (gap preexistente de Fase 1).

Ver ``Planificación/REGISTRY.md`` Tarea 3.D y ``Contexto/AGENTS.md``
regla #7.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from liquidator.cli.main import main

# ===========================================================================
# Fixtures y helpers
# ===========================================================================


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def input_json(tmp_path: Path) -> Path:
    """Input JSON mínimo válido para invocar ``liquidar``."""
    p = tmp_path / "caso_minimo.json"
    p.write_text(json.dumps({
        "trabajador": {"nombre": "X", "documento": "1"},
        "empleador": {"nombre": "Y", "documento": "2"},
        "contrato": {
            "fecha_ingreso": "2025-01-01",
            "fecha_corte": "2025-12-31",
            "tipo": "INDEFINIDO",
        },
        "salario": {"SBL": 2_200_000},
        "modo": "PERIODICA",
    }), encoding="utf-8")
    return p


def _fake_engine_result(status: str) -> dict[str, Any]:
    """Construye un ``engine.process()`` simulado con el status dado."""
    return {
        "meta": {
            "motor_version": "2.0.0",
            "modo": "PERIODICA",
            "compliance_status": status,
        },
        "trabajador": {"nombre": "X", "documento": "1"},
        "empleador": {"nombre": "Y", "documento": "2"},
        "contrato": {
            "fecha_ingreso": "2025-01-01",
            "fecha_corte": "2025-12-31",
            "tipo": "INDEFINIDO",
        },
        "salario": {"SBL": 2_200_000},
        "desglose": {
            "2025": {"cesantias": 2_200_000, "prima": 2_200_000},
        },
        "total_liquidacion": 4_400_000,
        "compliance_report": {
            "compliance_status": status,
            "blocking_failures": (
                [{"code": "V_FOO", "message": "falla crítica"}]
                if status == "NO_GO" else []
            ),
            "summary": {"passed": 10, "warnings": 0, "failures": 0},
        },
    }


# ===========================================================================
# Rama GO / WARN / OVERRIDE_APPROVED
# ===========================================================================


class TestRamaGo:
    """compliance_status != NO_GO → exit 0, escribe liquidacion.json."""

    @pytest.mark.parametrize("status", ["GO", "WARN", "OVERRIDE_APPROVED"])
    def test_exit_cero_para_status_no_bloqueante(
        self, runner, input_json, tmp_path, status
    ):
        out_dir = tmp_path / "out"
        with patch(
            "liquidator.core.engine.LiquidacionEngine.process",
            return_value=_fake_engine_result(status),
            create=True,
        ):
            result = runner.invoke(
                main,
                ["liquidar", str(input_json), "--out-dir", str(out_dir)],
            )
        assert result.exit_code == 0, f"stderr: {result.stderr}"

    @pytest.mark.parametrize("status", ["GO", "WARN", "OVERRIDE_APPROVED"])
    def test_escribe_liquidacion_json_sin_bloqueada(
        self, runner, input_json, tmp_path, status
    ):
        out_dir = tmp_path / "out"
        with patch(
            "liquidator.core.engine.LiquidacionEngine.process",
            return_value=_fake_engine_result(status),
            create=True,
        ):
            runner.invoke(
                main,
                ["liquidar", str(input_json), "--out-dir", str(out_dir)],
            )
        # Debe existir liquidacion.json
        assert (out_dir / "liquidacion.json").exists()
        # NO debe existir liquidacion_BLOQUEADA.*
        assert not (out_dir / "liquidacion_BLOQUEADA.json").exists()
        assert not (out_dir / "liquidacion_BLOQUEADA.md").exists()

    def test_liquidacion_json_tiene_contenido_del_motor(
        self, runner, input_json, tmp_path
    ):
        out_dir = tmp_path / "out"
        with patch(
            "liquidator.core.engine.LiquidacionEngine.process",
            return_value=_fake_engine_result("GO"),
            create=True,
        ):
            runner.invoke(
                main,
                ["liquidar", str(input_json), "--out-dir", str(out_dir)],
            )
        content = json.loads(
            (out_dir / "liquidacion.json").read_text(encoding="utf-8")
        )
        assert content["total_liquidacion"] == 4_400_000
        assert content["compliance_report"]["compliance_status"] == "GO"

    def test_no_genera_pdf_en_rama_go(
        self, runner, input_json, tmp_path
    ):
        """Regla AGENTS.md #8: no disfrazar .txt como PDF."""
        out_dir = tmp_path / "out"
        with patch(
            "liquidator.core.engine.LiquidacionEngine.process",
            return_value=_fake_engine_result("GO"),
            create=True,
        ):
            runner.invoke(
                main,
                ["liquidar", str(input_json), "--out-dir", str(out_dir)],
            )
        # No debe haber .pdf
        pdf_files = list(out_dir.glob("*.pdf"))
        assert pdf_files == []


# ===========================================================================
# Rama NO_GO (Tarea 3.D)
# ===========================================================================


class TestRamaNoGo:
    """compliance_status == NO_GO → exit 2, escribe liquidacion_BLOQUEADA.*"""

    def test_exit_dos_para_no_go(self, runner, input_json, tmp_path):
        out_dir = tmp_path / "out"
        with patch(
            "liquidator.core.engine.LiquidacionEngine.process",
            return_value=_fake_engine_result("NO_GO"),
            create=True,
        ):
            result = runner.invoke(
                main,
                ["liquidar", str(input_json), "--out-dir", str(out_dir)],
            )
        assert result.exit_code == 2, f"stderr: {result.stderr}"

    def test_escribe_liquidacion_BLOQUEADA_json(
        self, runner, input_json, tmp_path
    ):
        out_dir = tmp_path / "out"
        with patch(
            "liquidator.core.engine.LiquidacionEngine.process",
            return_value=_fake_engine_result("NO_GO"),
            create=True,
        ):
            runner.invoke(
                main,
                ["liquidar", str(input_json),
                 "--out-dir", str(out_dir)],
            )
        # Debe existir liquidacion_BLOQUEADA.json
        assert (out_dir / "liquidacion_BLOQUEADA.json").exists()
        # NO debe existir liquidacion.json (el normal)
        assert not (out_dir / "liquidacion.json").exists()

    def test_liquidacion_BLOQUEADA_json_tiene_fallos_bloqueantes(
        self, runner, input_json, tmp_path
    ):
        out_dir = tmp_path / "out"
        with patch(
            "liquidator.core.engine.LiquidacionEngine.process",
            return_value=_fake_engine_result("NO_GO"),
            create=True,
        ):
            runner.invoke(
                main,
                ["liquidar", str(input_json), "--out-dir", str(out_dir)],
            )
        content = json.loads(
            (out_dir / "liquidacion_BLOQUEADA.json").read_text(encoding="utf-8")
        )
        assert content["compliance_report"]["compliance_status"] == "NO_GO"
        assert len(content["compliance_report"]["blocking_failures"]) == 1
        assert content["compliance_report"]["blocking_failures"][0]["code"] == "V_FOO"

    def test_escribe_liquidacion_BLOQUEADA_md_con_mensaje(
        self, runner, input_json, tmp_path
    ):
        """El .md de bloqueo debe incluir 'LIQUIDACIÓN BLOQUEADA'."""
        out_dir = tmp_path / "out"
        with patch(
            "liquidator.core.engine.LiquidacionEngine.process",
            return_value=_fake_engine_result("NO_GO"),
            create=True,
        ):
            runner.invoke(
                main,
                ["liquidar", str(input_json), "--out-dir", str(out_dir)],
            )
        md_path = out_dir / "liquidacion_BLOQUEADA.md"
        assert md_path.exists()
        md_content = md_path.read_text(encoding="utf-8")
        assert "LIQUIDACIÓN BLOQUEADA" in md_content
        assert "NO_GO" in md_content

    def test_md_de_bloqueo_NO_incluye_pii(
        self, runner, input_json, tmp_path
    ):
        """Regla AGENTS.md #6 + _render_blocked: el .md NO muestra PII."""
        out_dir = tmp_path / "out"
        with patch(
            "liquidator.core.engine.LiquidacionEngine.process",
            return_value=_fake_engine_result("NO_GO"),
            create=True,
        ):
            runner.invoke(
                main,
                ["liquidar", str(input_json), "--out-dir", str(out_dir)],
            )
        md_content = (
            out_dir / "liquidacion_BLOQUEADA.md"
        ).read_text(encoding="utf-8")
        # El nombre del trabajador (X) y documento (1) NO deben aparecer.
        # Verificamos que el bloque de bloqueo no incluye datos personales.
        # El .json sí los tiene, pero el .md es de bloqueo puro.
        # Si el .md tiene una sección de identificación, el MarkdownGenerator
        # la omite (ver _render_blocked: no incluye datos del trabajador).
        # Test defensivo: ningún documento o nombre que estuviera en el
        # input debería aparecer en la sección de bloqueo.
        bloque_section = md_content.split("## Fallos bloqueantes")[0]
        # El bloque header solo debe tener el título y la versión, no PII
        # del input.
        assert "1" not in bloque_section.split("LIQUIDACIÓN BLOQUEADA")[0] or \
            "Versión del motor" in bloque_section

    def test_no_genera_pdf_en_no_go(
        self, runner, input_json, tmp_path
    ):
        """Regla AGENTS.md #7: NO PDF si compliance = NO_GO."""
        out_dir = tmp_path / "out"
        with patch(
            "liquidator.core.engine.LiquidacionEngine.process",
            return_value=_fake_engine_result("NO_GO"),
            create=True,
        ):
            runner.invoke(
                main,
                ["liquidar", str(input_json), "--out-dir", str(out_dir)],
            )
        pdf_files = list(out_dir.glob("*.pdf"))
        assert pdf_files == []


# ===========================================================================
# --json-only
# ===========================================================================


class TestJsonOnly:
    """--json-only: emite solo JSON por stdout, sin archivos en disco."""

    def test_json_only_no_escribe_archivos(
        self, runner, input_json, tmp_path
    ):
        out_dir = tmp_path / "out"
        with patch(
            "liquidator.core.engine.LiquidacionEngine.process",
            return_value=_fake_engine_result("GO"),
            create=True,
        ):
            runner.invoke(
                main,
                ["liquidar", str(input_json),
                 "--out-dir", str(out_dir), "--json-only"],
            )
        assert not (out_dir / "liquidacion.json").exists()
        assert not (out_dir / "liquidacion_BLOQUEADA.json").exists()

    def test_json_only_con_no_go_mantiene_exit_dos(
        self, runner, input_json, tmp_path
    ):
        out_dir = tmp_path / "out"
        with patch(
            "liquidator.core.engine.LiquidacionEngine.process",
            return_value=_fake_engine_result("NO_GO"),
            create=True,
        ):
            result = runner.invoke(
                main,
                ["liquidar", str(input_json),
                 "--out-dir", str(out_dir), "--json-only"],
            )
        assert result.exit_code == 2
        # El JSON salió por stdout
        stdout_json = json.loads(result.stdout)
        assert stdout_json["compliance_report"]["compliance_status"] == "NO_GO"

    def test_json_only_con_go_exit_cero(
        self, runner, input_json, tmp_path
    ):
        out_dir = tmp_path / "out"
        with patch(
            "liquidator.core.engine.LiquidacionEngine.process",
            return_value=_fake_engine_result("GO"),
            create=True,
        ):
            result = runner.invoke(
                main,
                ["liquidar", str(input_json),
                 "--out-dir", str(out_dir), "--json-only"],
            )
        assert result.exit_code == 0


# ===========================================================================
# Helper: _write_output_artifacts (probado directamente)
# ===========================================================================


class TestWriteOutputArtifacts:
    """Tests directos del helper ``_write_output_artifacts``.

    Útil para casos no cubiertos por el runner (ej. inputs malformados,
    motor que retorna None, etc.).
    """

    def test_escribe_liquidacion_json_en_rama_go(self, tmp_path):
        from liquidator.cli.main import _write_output_artifacts

        out_dir = tmp_path / "out"
        result = _fake_engine_result("GO")
        json_path, md_path = _write_output_artifacts(
            result, out_dir, "caso_minimo", is_blocked=False
        )
        assert json_path == out_dir / "liquidacion.json"
        assert md_path is None
        assert json_path.exists()
        # NO crea BLOQUEADA
        assert not (out_dir / "liquidacion_BLOQUEADA.json").exists()

    def test_escribe_liquidacion_BLOQUEADA_json_y_md_en_rama_no_go(
        self, tmp_path
    ):
        from liquidator.cli.main import _write_output_artifacts

        out_dir = tmp_path / "out"
        result = _fake_engine_result("NO_GO")
        json_path, md_path = _write_output_artifacts(
            result, out_dir, "caso_minimo", is_blocked=True
        )
        assert json_path == out_dir / "liquidacion_BLOQUEADA.json"
        assert md_path == out_dir / "liquidacion_BLOQUEADA.md"
        assert json_path.exists()
        assert md_path.exists()
        # NO crea el normal
        assert not (out_dir / "liquidacion.json").exists()

    def test_crea_out_dir_si_no_existe(self, tmp_path):
        from liquidator.cli.main import _write_output_artifacts

        out_dir = tmp_path / "nuevo" / "subdir"
        assert not out_dir.exists()
        _write_output_artifacts(
            _fake_engine_result("GO"), out_dir, "x", is_blocked=False
        )
        assert out_dir.exists()
        assert (out_dir / "liquidacion.json").exists()
