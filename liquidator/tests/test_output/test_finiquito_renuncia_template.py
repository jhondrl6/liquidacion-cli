"""Tests for finiquito template with renunciation blocks (Tarea 3.G, Fase 3).

Verifica que el template comprobante_finiquito.md renderiza correctamente:
1. La nota de NO APLICA indemnización para renuncia voluntaria.
2. La sección de vacaciones compensadas (Art. 189-190 CST).
3. Que NO muestra la nota de renuncia en otros motivos.

Origen: Addendum finiquito/vacaciones 2026-06-11 §C, Tarea 3.G.
"""

import pytest
from pathlib import Path
from decimal import Decimal

from liquidator.output.template_manager import TemplateManager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"


@pytest.fixture
def manager():
    """TemplateManager with the project templates."""
    return TemplateManager(str(_TEMPLATES_DIR))


def _base_context(
    motivo: str = "renuncia_voluntaria",
    indemnizacion: float = 0,
    vacaciones_valor: float = 550000,
    vacaciones_dias: float = 7.5,
) -> dict:
    """Build minimal context for finiquito template."""
    return {
        "año": "2026",
        "fecha": "2026-06-15",
        "modo": "FINIQUITO",
        "fecha_ingreso": "16/11/2025",
        "fecha_corte": "15/06/2026",
        "nombre": "ANONIMIZADO",
        "documento": "---",
        "tipo_contrato": "indefinido",
        "reside_en_lugar": False,
        "motivo_terminacion": motivo,
        "cesantias": 0,
        "dias_ces": 0,
        "plazo_ces": "—",
        "norma_ces": "—",
        "intereses": 0,
        "dias_int": 0,
        "plazo_int": "—",
        "norma_int": "—",
        "prima": 0,
        "dias_prima": 0,
        "plazo_prima": "—",
        "norma_prima": "—",
        "vacaciones": vacaciones_valor,
        "dias_vac": vacaciones_dias,
        "norma_vac": "Art. 189-190 CST",
        "indemnizacion": indemnizacion,
        "dias_indem": 0,
        "norma_indem": "—",
        "salario_pendiente": 0,
        "dias_salario_pend": 0,
        "norma_salario": "—",
        "total": vacaciones_valor + indemnizacion,
        "observaciones": "",
        "plazos_detallados": "",
        "declaracion": "",
        "desglose_segmentado": "",
        "compliance_status": "GO",
        "desglose": {
            "vacaciones": {
                "valor": vacaciones_valor,
                "dias": vacaciones_dias,
            },
            "indemnizacion": {
                "valor": indemnizacion,
            },
        },
    }


# ---------------------------------------------------------------------------
# Tests: renuncia_voluntaria
# ---------------------------------------------------------------------------


class TestRenunciaTemplate:
    """Tests para el template con motivo renuncia_voluntaria."""

    def test_plantilla_renderiza_nota_no_indemnizacion(self, manager):
        """El bloque condicional muestra la nota jurídica de no-indemnización."""
        context = _base_context(motivo="renuncia_voluntaria")
        rendered = manager.render_template("finiquito", context)

        assert "NO APLICA" in rendered
        assert "Art. 49 numeral 6" in rendered
        assert "Art. 64 CST" in rendered
        assert "renunció" in rendered

    def test_plantilla_renderiza_vacaciones(self, manager):
        """La sección de vacaciones compensadas se renderiza."""
        context = _base_context(
            motivo="renuncia_voluntaria",
            vacaciones_valor=550000,
            vacaciones_dias=7.5,
        )
        rendered = manager.render_template("finiquito", context)

        assert "Vacaciones compensadas" in rendered
        assert "Art. 189-190 CST" in rendered

    def test_plantilla_muestra_motivo_terminacion(self, manager):
        """El motivo de terminación se muestra en los datos del trabajador."""
        context = _base_context(motivo="renuncia_voluntaria")
        rendered = manager.render_template("finiquito", context)

        assert "renuncia_voluntaria" in rendered

    def test_plantilla_indemnizacion_muestra_na_para_renuncia(self, manager):
        """En la tabla, la indemnización muestra N/A para renuncia."""
        context = _base_context(motivo="renuncia_voluntaria")
        rendered = manager.render_template("finiquito", context)

        assert "N/A — renuncia voluntaria" in rendered

    def test_plantilla_formato_cop_vacaciones(self, manager):
        """El valor de vacaciones se formatea en COP."""
        context = _base_context(
            motivo="renuncia_voluntaria",
            vacaciones_valor=550000,
        )
        rendered = manager.render_template("finiquito", context)

        assert "550.000" in rendered


# ---------------------------------------------------------------------------
# Tests: otros motivos (NO deben mostrar nota de renuncia)
# ---------------------------------------------------------------------------


class TestOtrosMotivosTemplate:
    """Tests para verificar que otros motivos NO muestran la nota de renuncia."""

    def test_despido_sin_justa_causa_no_muestra_nota_renuncia(self, manager):
        """Despido sin justa causa NO muestra la nota de renuncia."""
        context = _base_context(
            motivo="despido_sin_justa_causa",
            indemnizacion=1000000,
        )
        rendered = manager.render_template("finiquito", context)

        # NO debe aparecer la nota específica de renuncia
        assert "N/A — renuncia voluntaria" not in rendered

    def test_despido_con_justa_causa_no_muestra_nota_renuncia(self, manager):
        """Despido con justa causa NO muestra la nota de renuncia."""
        context = _base_context(
            motivo="despido_con_justa_causa",
        )
        rendered = manager.render_template("finiquito", context)

        assert "N/A — renuncia voluntaria" not in rendered


# ---------------------------------------------------------------------------
# Tests: sin motivo (caso legacy)
# ---------------------------------------------------------------------------


class TestSinMotivoTemplate:
    """Tests para templates sin motivo de terminación (caso legacy)."""

    def test_finiquito_sin_motivo_no_muestra_nota_renuncia(self, manager):
        """FINIQUITO sin motivo no muestra la nota de renuncia."""
        context = _base_context(motivo="")
        # Quitar motivo_terminacion del contexto
        context.pop("motivo_terminacion", None)
        rendered = manager.render_template("finiquito", context)

        assert "NO APLICA" not in rendered
