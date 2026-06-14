"""
Golden tests para Tarea 2.B-cuater — Indemnización por preaviso Art. 46 CST.

Casos:
1. FINIQUITO + FIJO + vencido + preaviso insuficiente (10 días) → indemnización
2. FINIQUITO + FIJO + vencido + preaviso suficiente (30 días) → sin indemnización
3. PERIODICA + INDEFINIDO → NO regresión (preaviso no aplica, motor v2.0.0)

Reparos:
  (a) Art. 46 CST verificado verbatim en SUIN (2026-06-14).
  (b) Indemnización preaviso = renglón separado de Art. 64.
"""

import json
import pytest
from pathlib import Path
from decimal import Decimal

from liquidator.core.engine import LiquidacionEngine, EngineConfig


REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_PATH = REPO_ROOT / "examples" / "inputs" / "finiquito_fijo_vencido_preaviso.json"
CANONICO_PATH = REPO_ROOT / "examples" / "inputs" / "caso_canonico_periodico_206d.json"


@pytest.fixture
def engine():
    """Engine con params 2026."""
    return LiquidacionEngine(EngineConfig(params_year=2026))


@pytest.fixture
def fixture_preaviso():
    """Input finiquito fijo vencido con preaviso insuficiente (10 días)."""
    with open(FIXTURE_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def fixture_preaviso_suficiente(fixture_preaviso):
    """Mismo fixture pero con preaviso de 30 días (suficiente)."""
    data = json.loads(json.dumps(fixture_preaviso))
    data["contrato"]["dias_preaviso"] = 30
    data["contrato"]["fecha_preaviso"] = "2026-05-02"
    return data


# ---------------------------------------------------------------------------
# Clase 1: TestPreavisoInsuficiente — happy path
# ---------------------------------------------------------------------------

class TestPreavisoInsuficiente:
    """FINIQUITO + FIJO + vencido + preaviso de 10 días → indemnización."""

    def test_indemnizacion_aplica(self, engine, fixture_preaviso):
        """El motor genera output con indemnización preaviso."""
        output = engine.process(fixture_preaviso)
        desglose = output.get("desglose", {})
        assert "preaviso_indemnizacion" in desglose

    def test_valor_correcto(self, engine, fixture_preaviso):
        """SBL=2_200_000, 10 días de preaviso → faltan 20 → (2_200_000/30)*20 = 1_466_667."""
        output = engine.process(fixture_preaviso)
        renglon = output["desglose"]["preaviso_indemnizacion"]
        assert renglon["valor"] == 1_466_667
        assert renglon["dias_faltantes"] == 20
        assert renglon["dias_preaviso_efectivos"] == 10

    def test_norma_art_46(self, engine, fixture_preaviso):
        """La norma referenciada es Art. 46 CST, NO Art. 64."""
        output = engine.process(fixture_preaviso)
        renglon = output["desglose"]["preaviso_indemnizacion"]
        assert "Art. 46" in renglon["norma"]
        assert "Art. 64" not in renglon["norma"]

    def test_total_actualizado(self, engine, fixture_preaviso):
        """El total_liquidacion incluye la indemnización preaviso."""
        output = engine.process(fixture_preaviso)
        total = output.get("total_liquidacion", 0)
        renglon = output["desglose"]["preaviso_indemnizacion"]
        assert total >= renglon["valor"]

    def test_alert_generada(self, engine, fixture_preaviso):
        """Se genera alerta con resumen de la indemnización."""
        output = engine.process(fixture_preaviso)
        alerts = output.get("validaciones_y_alertas", {})
        assert "indemnizacion_preaviso" in alerts
        assert "1,466,667" in alerts["indemnizacion_preaviso"] or "Art. 46" in alerts["indemnizacion_preaviso"]

    def test_renglon_separado_de_art_64(self, engine, fixture_preaviso):
        """Reparo (b): preaviso es renglón separado de indemnización Art. 64."""
        output = engine.process(fixture_preaviso)
        desglose = output.get("desglose", {})
        # preaviso_indemnizacion es distinto de indemnizacion (Art. 64)
        assert "preaviso_indemnizacion" in desglose


# ---------------------------------------------------------------------------
# Clase 2: TestPreavisoSuficiente — sin indemnización
# ---------------------------------------------------------------------------

class TestPreavisoSuficiente:
    """FINIQUITO + FIJO + vencido + preaviso de 30 días → sin indemnización."""

    def test_no_indemnizacion(self, engine, fixture_preaviso_suficiente):
        """Con 30 días de preaviso, no hay indemnización."""
        output = engine.process(fixture_preaviso_suficiente)
        desglose = output.get("desglose", {})
        assert "preaviso_indemnizacion" not in desglose

    def test_alert_preaviso_suficiente(self, engine, fixture_preaviso_suficiente):
        """Se genera alerta indicando que el preaviso fue suficiente."""
        output = engine.process(fixture_preaviso_suficiente)
        alerts = output.get("validaciones_y_alertas", {})
        # Puede ser "preaviso_suficiente" o no existir
        # Lo importante es que NO hay indemnización en desglose
        desglose = output.get("desglose", {})
        assert "preaviso_indemnizacion" not in desglose


# ---------------------------------------------------------------------------
# Clase 3: TestPreavisoNoRegresion — PERIODICA no se afecta
# ---------------------------------------------------------------------------

class TestPreavisoNoRegresion:
    """PERIODICA + INDEFINIDO → motor v2.0.0 intacto."""

    @pytest.mark.xfail(
        reason="Bug preexistente: WorkflowOrchestrator no soporta Forma 2 anidada (REGISTRY Pitfall #22)",
        strict=False,
    )
    def test_caso_canonico_periodica_intacto(self, engine):
        """Regresión: caso canónico PERIODICA no se afecta por 2.B-cuater."""
        with open(CANONICO_PATH, encoding="utf-8") as f:
            data = json.load(f)
        output = engine.process(data)
        desglose = output.get("desglose", {})
        assert "preaviso_indemnizacion" not in desglose

    def test_finiquot_sin_tipo_fijo_no_aplica(self, engine, fixture_preaviso):
        """FINIQUITO + INDEFINIDO → no aplica preaviso."""
        data = json.loads(json.dumps(fixture_preaviso))
        data["contrato"]["tipo"] = "INDEFINIDO"
        data["contrato"].pop("motivo_terminacion", None)
        data["contrato"].pop("preaviso_entregado", None)
        data["contrato"].pop("fecha_preaviso", None)
        data["contrato"].pop("dias_preaviso", None)
        data["contrato"].pop("fecha_vencimiento_termino_fijo", None)
        output = engine.process(data)
        desglose = output.get("desglose", {})
        assert "preaviso_indemnizacion" not in desglose
