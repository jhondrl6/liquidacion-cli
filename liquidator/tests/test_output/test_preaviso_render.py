"""Tests for finiquito template with preaviso blocks (Tarea 3.H, Fase 3).

Verifica que el template comprobante_finiquito.md renderiza correctamente:
1. La sección de preaviso Art. 46 CST para contrato FIJO vencido.
2. La indemnización completa cuando NO hay preaviso.
3. La nota de preaviso suficiente cuando se dio preaviso ≥ 30 días.
4. Que NO muestra sección de preaviso para INDEFINIDO u otros tipos.

Origen: Addendum preaviso 2026-06-13, Tarea 3.H.
"""

import pytest
from pathlib import Path

from liquidator.output.template_manager import TemplateManager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"


@pytest.fixture
def manager():
    """TemplateManager with the project templates."""
    return TemplateManager(str(_TEMPLATES_DIR))


def _base_context_preaviso(
    preaviso_entregado=None,
    fecha_preaviso="",
    dias_preaviso=0,
    indemnizacion_valor=0,
    dias_faltantes=30,
    tipo_contrato="fijo",
    motivo_terminacion="termino_fijo_vencido",
) -> dict:
    """Build minimal context for finiquito template with preaviso fields."""
    return {
        "año": "2026",
        "fecha": "2026-06-01",
        "modo": "FINIQUITO",
        "fecha_ingreso": "01/06/2025",
        "fecha_corte": "01/06/2026",
        "nombre": "ANONIMIZADO",
        "documento": "---",
        "tipo_contrato": tipo_contrato,
        "reside_en_lugar": False,
        "motivo_terminacion": motivo_terminacion,
        "preaviso_entregado": preaviso_entregado,
        "fecha_preaviso": fecha_preaviso,
        "dias_preaviso": dias_preaviso,
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
        "vacaciones": 0,
        "dias_vac": 0,
        "norma_vac": "—",
        "indemnizacion": 0,
        "dias_indem": 0,
        "norma_indem": "—",
        "salario_pendiente": 0,
        "dias_salario_pend": 0,
        "norma_salario": "—",
        "total": indemnizacion_valor,
        "observaciones": "",
        "plazos_detallados": "",
        "declaracion": "",
        "desglose_segmentado": "",
        "compliance_status": "GO",
        "desglose": {
            "preaviso_indemnizacion": {
                "valor": indemnizacion_valor,
                "dias_faltantes": dias_faltantes,
            },
        },
    }


# ---------------------------------------------------------------------------
# Tests: preaviso sin entrega
# ---------------------------------------------------------------------------


class TestPreavisoSinEntrega:
    """Tests para el template con preaviso NO entregado."""

    def test_sin_preaviso_muestra_indemnizacion_completa(self, manager):
        """Sin preaviso: muestra indemnización por 30 días."""
        context = _base_context_preaviso(
            preaviso_entregado=False,
            indemnizacion_valor=2200000,
            dias_faltantes=30,
        )
        rendered = manager.render_template("finiquito", context)

        assert "Preaviso entregado: **NO**" in rendered
        assert "Art. 46 CST" in rendered

    def test_sin_preaviso_muestra_formato_cop(self, manager):
        """El valor se formatea en COP con separadores de miles."""
        context = _base_context_preaviso(
            preaviso_entregado=False,
            indemnizacion_valor=2200000,
        )
        rendered = manager.render_template("finiquito", context)

        assert "2.200.000" in rendered

    def test_sin_preaviso_nota_legal(self, manager):
        """La nota de no-notificación aparece cuando no hay preaviso."""
        context = _base_context_preaviso(
            preaviso_entregado=False,
            indemnizacion_valor=2200000,
        )
        rendered = manager.render_template("finiquito", context)

        assert "notificar por escrito" in rendered
        assert "30 días" in rendered


# ---------------------------------------------------------------------------
# Tests: preaviso suficiente
# ---------------------------------------------------------------------------


class TestPreavisoSuficiente:
    """Tests para el template con preaviso ≥ 30 días."""

    def test_preaviso_suficiente_no_indemnizacion(self, manager):
        """Preaviso de 31 días: no aplica indemnización."""
        context = _base_context_preaviso(
            preaviso_entregado=True,
            fecha_preaviso="2026-05-01",
            dias_preaviso=31,
            indemnizacion_valor=0,
            dias_faltantes=0,
        )
        rendered = manager.render_template("finiquito", context)

        assert "Preaviso entregado: **SÍ**" in rendered
        assert "suficiente" in rendered.lower()

    def test_preaviso_suficiente_muestra_fecha(self, manager):
        """Preaviso con fecha muestra la fecha de preaviso."""
        context = _base_context_preaviso(
            preaviso_entregado=True,
            fecha_preaviso="2026-05-01",
            dias_preaviso=31,
            indemnizacion_valor=0,
            dias_faltantes=0,
        )
        rendered = manager.render_template("finiquito", context)

        assert "2026-05-01" in rendered


# ---------------------------------------------------------------------------
# Tests: preaviso parcial (insuficiente)
# ---------------------------------------------------------------------------


class TestPreavisoParcial:
    """Tests para preaviso entregado pero insuficiente (< 30 días)."""

    def test_preaviso_parcial_muestra_indemnizacion(self, manager):
        """10 días de preaviso → faltan 20 → indemnización parcial."""
        context = _base_context_preaviso(
            preaviso_entregado=True,
            fecha_preaviso="2026-05-22",
            dias_preaviso=10,
            indemnizacion_valor=1466667,
            dias_faltantes=20,
        )
        rendered = manager.render_template("finiquito", context)

        assert "Preaviso insuficiente" in rendered
        assert "1.466.667" in rendered

    def test_preaviso_parcial_muestra_dias_faltantes(self, manager):
        """Muestra los días faltantes en la fórmula."""
        context = _base_context_preaviso(
            preaviso_entregado=True,
            indemnizacion_valor=733333,
            dias_faltantes=10,
        )
        rendered = manager.render_template("finiquito", context)

        assert "10" in rendered  # dias_faltantes en la fórmula


# ---------------------------------------------------------------------------
# Tests: NO mostrar preaviso en otros tipos de contrato
# ---------------------------------------------------------------------------


class TestNoPreavisoOtrosTipos:
    """Verifica que la sección de preaviso NO aparece para INDEFINIDO, etc."""

    def test_indefinido_no_muestra_preaviso(self, manager):
        """INDEFINIDO + renuncia NO renderiza sección de preaviso."""
        context = _base_context_preaviso(
            tipo_contrato="indefinido",
            motivo_terminacion="renuncia_voluntaria",
            preaviso_entregado=False,
            indemnizacion_valor=0,
        )
        rendered = manager.render_template("finiquito", context)

        assert "Preaviso (Art. 46 CST)" not in rendered

    def test_indefinido_despido_no_muestra_preaviso(self, manager):
        """INDEFINIDO + despido NO renderiza sección de preaviso."""
        context = _base_context_preaviso(
            tipo_contrato="indefinido",
            motivo_terminacion="despido_sin_justa_causa",
            preaviso_entregado=False,
            indemnizacion_valor=0,
        )
        rendered = manager.render_template("finiquito", context)

        assert "Preaviso (Art. 46 CST)" not in rendered

    def test_fijo_otro_motivo_no_muestra_preaviso(self, manager):
        """FIJO + renuncia (no 'termino_fijo_vencido') NO muestra preaviso."""
        context = _base_context_preaviso(
            tipo_contrato="fijo",
            motivo_terminacion="renuncia_voluntaria",
            preaviso_entregado=False,
            indemnizacion_valor=0,
        )
        rendered = manager.render_template("finiquito", context)

        assert "Preaviso (Art. 46 CST)" not in rendered


# ---------------------------------------------------------------------------
# Tests: sin desglose (legacy, sin preaviso_indemnizacion)
# ---------------------------------------------------------------------------


class TestPreavisoSinDesglose:
    """Tests con contexto sin clave preaviso_indemnizacion en desglose."""

    def test_fijo_vencido_sin_desglose_preaviso(self, manager):
        """FIJO vencido sin preaviso_indemnizacion en desglose: no crashea."""
        context = _base_context_preaviso(
            preaviso_entregado=False,
        )
        # Quitar preaviso_indemnizacion del desglose
        context["desglose"] = {}
        rendered = manager.render_template("finiquito", context)

        assert "Preaviso (Art. 46 CST)" in rendered
        assert "Preaviso entregado: **NO**" in rendered
        # No debería mostrar el valor (no hay desglose)
        assert "Fórmula: SBL / 30 × 30" not in rendered
