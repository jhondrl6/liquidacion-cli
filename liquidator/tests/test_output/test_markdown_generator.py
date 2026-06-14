"""Tests for MarkdownGenerator — v2.0 (Tarea 1.F).

Cubre:
- Generación con datos planos (legacy) — retrocompatibilidad.
- Generación con datos segmentados (JSONGenerator shape) — v2.0.
- Estados de compliance: GO, WARN, NO_GO, OVERRIDE_APPROVED.
- Bloqueo (NO_GO) sin datos de trabajador.
- Contexto inválido (meta/desglose faltante) → error descriptivo.
- Campos opcionales faltantes → no falla.
- Sanitización PII en errores.
- Plan §6.2 validación: test_markdown_genera_para_canonico,
  test_markdown_genera_bloqueado.
"""

from __future__ import annotations

import os
import tempfile
from typing import Any

import pytest

from liquidator.output.markdown_generator import MarkdownGenerator

# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

@pytest.fixture
def generator() -> MarkdownGenerator:
    return MarkdownGenerator()


@pytest.fixture
def json_data_legacy() -> dict[str, Any]:
    """Datos legacy (forma plana) para tests de retrocompatibilidad."""
    return {
        "meta": {
            "modo": "PERIÓDICA",
            "fecha_corte": "2025-11-15",
            "fecha_ingreso": "2024-11-16",
            "compliance_status": "GO",
            "fecha_generacion": "2025-11-15T10:00:00",
            "motor_version": "0.2.0-dev",
        },
        "trabajador": {
            "nombre": "Juan Pérez",
            "documento": "123456789",
            "reside_en_lugar_trabajo": True,
        },
        "empleador": {
            "nombre": "[EMPLEADOR]",
            "documento": "900123456",
        },
        "contrato": {
            "tipo": "INDEFINIDO",
            "fecha_ingreso": "2024-11-16",
            "fecha_corte": "2025-11-15",
        },
        "desglose": {
            "cesantias": {
                "valor": 2_200_000,
                "dias_liquidados": 360,
                "plazo_pago_legal": "2026-02-14",
                "norma": "Art.249-250 CST",
            },
            "intereses_cesantias": {
                "valor": 264_000,
                "dias_liquidados": 360,
                "plazo_pago_legal": "2026-01-31",
                "norma": "Ley 50/1990 Art.99",
            },
            "prima": {
                "valor": 1_100_000,
                "dias_liquidados": 180,
                "plazo_pago_legal": "2025-12-31",
                "norma": "Art.306-308 CST",
            },
            "vacaciones": {
                "valor": 0,
                "dias_liquidados": 0,
                "norma": "Arts.186-192 CST",
            },
        },
        "total_liquidacion": 3_564_000,
        "validaciones_y_alertas": {
            "auxilio_transporte_excluido": "Residencia en el lugar de trabajo (Finca).",
            "auxilio_conectividad_advertencia": (
                "Verificar si está pactado como parte del salario habitual."
            ),
        },
    }


@pytest.fixture
def json_data_segmented() -> dict[str, Any]:
    """Datos segmentados (JSONGenerator shape) para tests v2.0."""
    return {
        "meta": {
            "modo": "PERIODICA",
            "fecha_generacion": "2026-06-09T10:00:00",
            "motor_version": "0.2.0-dev",
            "generator_version": "0.2.0-dev",
            "params_version": "2026-06-09",
            "params_hash": "sha256:abc123",
            "input_hash": "sha256:def456",
            "output_hash": "sha256:ghi789",
            "compliance_status": "GO",
            "referencias_normativas": [
                "DECRETO_1469_2025",
                "DECRETO_159_2026",
            ],
            "plantilla_version": None,
            "parametros_por_segmento": {
                "2025": {
                    "params_version": "2025-01-01",
                    "rango": "2025-11-16 → 2025-12-31",
                    "dias": 46,
                    "params_ref": "params/2025.json",
                },
                "2026": {
                    "params_version": "2026-06-09",
                    "rango": "2026-01-01 → 2026-06-09",
                    "dias": 160,
                    "params_ref": "params/2026.json",
                },
            },
        },
        "trabajador": {
            "nombre": "[ANONIMIZADO]",
            "documento": "123456789",
        },
        "empleador": {
            "nombre": "[ANONIMIZADO]",
            "documento": "900123456",
        },
        "contrato": {
            "fecha_ingreso": "2025-11-16",
            "fecha_corte": "2026-06-09",
            "tipo": "INDEFINIDO",
        },
        "parametros": {
            "SMMLV": 1_750_905,
            "AUXILIO_TRANS": 249_095,
            "version": "2026-06-09",
        },
        "desglose": {
            "2025": {
                "cesantias": 281_111,
                "intereses_cesantias": 33_733,
                "prima": 281_111,
                "vacaciones": 140_555,
                "indemnizacion": None,
                "recargo_dominical": 0,
            },
            "2026": {
                "cesantias": 977_777,
                "intereses_cesantias": 117_333,
                "prima": 977_777,
                "vacaciones": 488_888,
                "indemnizacion": None,
                "recargo_dominical": 0,
            },
        },
        "total_liquidacion": 3_298_285,
        "validaciones_y_alertas": {
            "auxilio_transporte_excluido": "Residencia en el lugar de trabajo.",
        },
        "normas_aplicadas": [
            "Art.249-250 CST",
            "Ley 50/1990 Art.99",
            "Art.306-308 CST",
        ],
        "compliance_report": {
            "compliance_status": "GO",
            "summary": {"passed": 10, "warnings": 1, "failures": 0},
            "checks": [],
            "blocking_failures": [],
        },
    }


# ------------------------------------------------------------------
# Generación legacy (forma plana)
# ------------------------------------------------------------------

class TestMarkdownLegacy:
    """Tests con datos planos legacy (retrocompatibilidad)."""

    def test_generate_markdown_periodica(
        self,
        generator: MarkdownGenerator,
        json_data_legacy: dict[str, Any],
    ) -> None:
        md = generator.generate_markdown(json_data_legacy)

        assert "LIQUIDACIÓN PERIÓDICA" in md
        assert "DATOS DEL TRABAJADOR" in md
        assert "DETALLE DE PRESTACIONES" in md
        assert "TOTAL LIQUIDACIÓN PERIÓDICA" in md
        assert "OBSERVACIONES" in md
        assert "PLAZOS LEGALES DE PAGO" in md
        assert "DECLARACIÓN LEGAL" in md

        # Formatos de moneda
        assert "$2.200.000" in md  # cesantías
        assert "$264.000" in md    # intereses
        assert "$1.100.000" in md  # prima
        assert "$3.564.000" in md  # total

        # Datos del trabajador
        assert "Juan Pérez" in md
        assert "123456789" in md
        assert "indefinido" in md
        assert "Sí" in md  # reside_en_lugar

        # Observaciones
        assert "Residencia en el lugar de trabajo" in md

    def test_generate_markdown_finiquito(
        self,
        generator: MarkdownGenerator,
        json_data_legacy: dict[str, Any],
    ) -> None:
        data = dict(json_data_legacy)
        data["meta"] = dict(data["meta"])
        data["meta"]["modo"] = "FINIQUITO"
        data["desglose"] = dict(data["desglose"])
        data["desglose"]["indemnizacion"] = {
            "valor": 4_400_000,
            "dias_liquidados": 360,
            "norma": "Art.64 CST",
        }
        data["desglose"]["salario_pendiente"] = {
            "valor": 0,
            "dias_liquidados": 0,
            "norma": "Art.65 CST",
        }

        md = generator.generate_markdown(data)

        assert "LIQUIDACIÓN POR FINIQUITO" in md
        assert "TOTAL LIQUIDACIÓN POR FINIQUITO" in md
        assert "Indemnización" in md
        assert "Salario pendiente" in md

    def test_save_markdown(
        self,
        generator: MarkdownGenerator,
        json_data_legacy: dict[str, Any],
    ) -> None:
        md = generator.generate_markdown(json_data_legacy)

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".md"
        ) as f:
            temp_path = f.name

        try:
            result = generator.save_markdown(md, temp_path)
            assert result is True
            assert os.path.exists(temp_path)
            with open(temp_path, encoding="utf-8") as f:
                content = f.read()
            assert "LIQUIDACIÓN PERIÓDICA" in content
            assert "$3.564.000" in content
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


# ------------------------------------------------------------------
# Generación segmentada (JSONGenerator shape)
# ------------------------------------------------------------------

class TestMarkdownSegmentado:
    """Tests con datos segmentados del JSONGenerator."""

    def test_segmentado_muestra_anios(
        self,
        generator: MarkdownGenerator,
        json_data_segmented: dict[str, Any],
    ) -> None:
        md = generator.generate_markdown(json_data_segmented)
        assert "2025" in md
        assert "2026" in md

    def test_segmentado_muestra_por_segmento(
        self,
        generator: MarkdownGenerator,
        json_data_segmented: dict[str, Any],
    ) -> None:
        md = generator.generate_markdown(json_data_segmented)
        assert "por segmento" in md.lower()

    def test_segmentado_contiene_desglose_segmentado(
        self,
        generator: MarkdownGenerator,
        json_data_segmented: dict[str, Any],
    ) -> None:
        md = generator.generate_markdown(json_data_segmented)
        assert "DESGLOSE POR SEGMENTO" in md

    def test_segmentado_nombres_anonimizados(
        self,
        generator: MarkdownGenerator,
        json_data_segmented: dict[str, Any],
    ) -> None:
        md = generator.generate_markdown(json_data_segmented)
        assert "[ANONIMIZADO]" in md


# ------------------------------------------------------------------
# Estados de compliance
# ------------------------------------------------------------------

class TestComplianceStates:
    """Manejo de estados de compliance (GO/WARN/NO_GO/OVERRIDE_APPROVED)."""

    def test_no_go_genera_bloqueo(
        self,
        generator: MarkdownGenerator,
        json_data_segmented: dict[str, Any],
    ) -> None:
        md = generator.generate_markdown(
            json_data_segmented, status="NO_GO"
        )
        assert "BLOQUEADA" in md or "bloqueada" in md.lower()
        assert "LIQUIDACIÓN BLOQUEADA" in md
        assert "NO_GO" in md

    def test_no_go_no_incluye_datos_trabajador(
        self,
        generator: MarkdownGenerator,
        json_data_segmented: dict[str, Any],
    ) -> None:
        md = generator.generate_markdown(
            json_data_segmented, status="NO_GO"
        )
        assert "[ANONIMIZADO]" not in md
        assert "123456789" not in md

    def test_no_go_incluye_resumen_compliance(
        self,
        generator: MarkdownGenerator,
        json_data_segmented: dict[str, Any],
    ) -> None:
        md = generator.generate_markdown(
            json_data_segmented, status="NO_GO"
        )
        assert "Resumen de compliance" in md
        assert "Fallos bloqueantes" in md

    def test_warn_no_bloquea(
        self,
        generator: MarkdownGenerator,
        json_data_segmented: dict[str, Any],
    ) -> None:
        md = generator.generate_markdown(
            json_data_segmented, status="WARN"
        )
        assert "LIQUIDACIÓN PERIÓDICA" in md
        assert "BLOQUEADA" not in md

    def test_override_approved_no_bloquea(
        self,
        generator: MarkdownGenerator,
        json_data_segmented: dict[str, Any],
    ) -> None:
        md = generator.generate_markdown(
            json_data_segmented, status="OVERRIDE_APPROVED"
        )
        assert "LIQUIDACIÓN PERIÓDICA" in md
        assert "BLOQUEADA" not in md

    def test_status_lee_de_meta_si_no_explicito(
        self,
        generator: MarkdownGenerator,
        json_data_segmented: dict[str, Any],
    ) -> None:
        md = generator.generate_markdown(json_data_segmented)
        assert "LIQUIDACIÓN PERIÓDICA" in md
        assert "BLOQUEADA" not in md

    def test_no_go_desde_meta(
        self,
        generator: MarkdownGenerator,
        json_data_segmented: dict[str, Any],
    ) -> None:
        data = dict(json_data_segmented)
        data["meta"] = dict(data["meta"])
        data["meta"]["compliance_status"] = "NO_GO"
        md = generator.generate_markdown(data)
        assert "LIQUIDACIÓN BLOQUEADA" in md


# ------------------------------------------------------------------
# Plan §6.2 — Tests de validación requeridos
# ------------------------------------------------------------------

class TestPlanValidation:
    """Tests que el plan §6.2 pide explícitamente para Tarea 1.F."""

    def test_markdown_genera_para_canonico(
        self,
        generator: MarkdownGenerator,
        json_data_segmented: dict[str, Any],
    ) -> None:
        out = generator.generate_markdown(
            json_data_segmented, status="GO"
        )
        assert "2025" in out and "2026" in out
        assert ("por_segmento" in out
                or "por segmento" in out.lower())

    def test_markdown_genera_bloqueado(
        self,
        generator: MarkdownGenerator,
        json_data_segmented: dict[str, Any],
    ) -> None:
        data = dict(json_data_segmented)
        data["compliance_report"] = {
            "compliance_status": "NO_GO",
            "summary": {"passed": 5, "warnings": 2, "failures": 1},
            "blocking_failures": [
                {"code": "V001", "message": "SMMLV no definido"},
            ],
        }
        out = generator.generate_markdown(data, status="NO_GO")
        assert "BLOQUEADA" in out or "bloqueada" in out.lower()


# ------------------------------------------------------------------
# Robustez: campos faltantes, errores de contexto
# ------------------------------------------------------------------

class TestRobustness:
    """No fallar si faltan campos opcionales."""

    def test_faltan_datos_minimos_genera_error_contexto(
        self, generator: MarkdownGenerator,
    ) -> None:
        md = generator.generate_markdown({})
        assert "ERROR DE CONTEXTO" in md

    def test_desglose_vacio_no_falla(
        self,
        generator: MarkdownGenerator,
        json_data_legacy: dict[str, Any],
    ) -> None:
        data = dict(json_data_legacy)
        data["desglose"] = {}
        md = generator.generate_markdown(data)
        assert "LIQUIDACIÓN PERIÓDICA" in md
        assert "$0" in md

    def test_falta_contrato_usa_meta_como_fallback(
        self,
        generator: MarkdownGenerator,
        json_data_legacy: dict[str, Any],
    ) -> None:
        data = dict(json_data_legacy)
        data.pop("contrato", None)
        md = generator.generate_markdown(data)
        assert "LIQUIDACIÓN PERIÓDICA" in md
        assert "2025-11-15" in md
        assert "2024-11-16" in md

    def test_validaciones_y_alertas_vacio_no_falla(
        self,
        generator: MarkdownGenerator,
        json_data_segmented: dict[str, Any],
    ) -> None:
        data = dict(json_data_segmented)
        data["validaciones_y_alertas"] = {}
        md = generator.generate_markdown(data)
        assert "Ninguna observación" in md

    def test_trabajador_sin_reside_en_lugar(
        self,
        generator: MarkdownGenerator,
        json_data_legacy: dict[str, Any],
    ) -> None:
        data = dict(json_data_legacy)
        data["trabajador"] = {"nombre": "X", "documento": "1"}
        md = generator.generate_markdown(data)
        assert "No" in md


# ------------------------------------------------------------------
# Helpers (tests unitarios de métodos internos)
# ------------------------------------------------------------------

class TestHelpers:
    """Tests de métodos auxiliares."""

    def test_format_observaciones(self, generator: MarkdownGenerator) -> None:
        validaciones = {"a": "Mensaje A.", "b": "Mensaje B."}
        result = generator._format_observaciones(validaciones)
        assert "- Mensaje A." in result
        assert "- Mensaje B." in result

    def test_format_observaciones_empty(self, generator: MarkdownGenerator) -> None:
        assert generator._format_observaciones({}) == "Ninguna observación."

    def test_format_plazos_periodica(
        self,
        generator: MarkdownGenerator,
        json_data_legacy: dict[str, Any],
    ) -> None:
        result = generator._format_plazos(
            json_data_legacy["desglose"], "PERIODICA"
        )
        assert "- Cesantías: 2026-02-14 (Art.249-250 CST)" in result
        assert "- Intereses sobre cesantías: 2026-01-31" in result
        assert "- Prima de servicios: 2025-12-31 (Art.306-308 CST)" in result

    def test_format_plazos_finiquito(
        self,
        generator: MarkdownGenerator,
        json_data_legacy: dict[str, Any],
    ) -> None:
        desglose = dict(json_data_legacy["desglose"])
        desglose["indemnizacion"] = {
            "valor": 0, "dias_liquidados": 0, "norma": "Art.64 CST",
        }
        desglose["salario_pendiente"] = {
            "valor": 0, "dias_liquidados": 0, "norma": "Art.65 CST",
        }
        result = generator._format_plazos(desglose, "FINIQUITO")
        assert "Indemnización: Pago inmediato" in result
        assert "Salario pendiente: Pago inmediato" in result

    def test_get_declaracion_periodica(self, generator: MarkdownGenerator) -> None:
        result = generator._get_declaracion("PERIODICA")
        assert "prestaciones sociales causadas" in result
        assert "cesantías serán consignadas" in result

    def test_get_declaracion_finiquito(self, generator: MarkdownGenerator) -> None:
        result = generator._get_declaracion("FINIQUITO")
        assert "totalidad de las prestaciones" in result
        assert "trabajador declara haber recibido" in result

    def test_fmt_currency(self, generator: MarkdownGenerator) -> None:
        assert generator._fmt_currency(2_200_000) == "$2.200.000"
        assert generator._fmt_currency(0) == "$0"
        assert generator._fmt_currency(1_750_905) == "$1.750.905"

    def test_fmt_date_iso(self, generator: MarkdownGenerator) -> None:
        assert generator._fmt_date("2025-11-15") == "2025-11-15"
        assert generator._fmt_date("2025-11-15T00:00:00") == "2025-11-15"
        assert generator._fmt_date("") == ""


# ------------------------------------------------------------------
# Sanitización PII
# ------------------------------------------------------------------

class TestPII:
    """Verifica que NO se filtren datos personales en errores."""

    def test_error_contexto_no_incluye_nombre(
        self, generator: MarkdownGenerator,
    ) -> None:
        bad_data = {
            "trabajador": {"nombre": "Juan Pérez", "documento": "123"},
        }
        md = generator.generate_markdown(bad_data)
        assert "ERROR DE CONTEXTO" in md
        assert "Juan Pérez" not in md
        assert "123" not in md

    def test_bloqueo_no_incluye_pii(
        self,
        generator: MarkdownGenerator,
        json_data_segmented: dict[str, Any],
    ) -> None:
        data = dict(json_data_segmented)
        data["trabajador"] = {
            "nombre": "María García",
            "documento": "987654321",
        }
        md = generator.generate_markdown(data, status="NO_GO")
        assert "María García" not in md
        assert "987654321" not in md
