"""PreRender Validator Module — Tarea 3.G (Fase 3).

Valida que la combinación modo + motivo_terminación + renglones presentes
en el desglose cumple los requisitos legales antes de renderizar el documento.

Origen: Addendum finiquito/vacaciones 2026-06-11 §C, Tarea 3.G.
Matriz REQUISITOS_POR_MOTIVO: tabla de requisitos por motivo de terminación.

Uso:
    from liquidator.output.pre_render_validator import (
        PreRenderValidator, PreRenderValidationError, REQUISITOS_POR_MOTIVO
    )
    validator = PreRenderValidator()
    validator.validar_requisitos_por_motivo(inp, desglose)
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class PreRenderValidationError(Exception):
    """Error de validación pre-render por motivo de terminación.

    Se lanza cuando la combinación modo + motivo + renglones no cumple
    los requisitos legales de la matriz REQUISITOS_POR_MOTIVO.
    """
    pass


# ---------------------------------------------------------------------------
# Matriz de requisitos por motivo de terminación
# ---------------------------------------------------------------------------
# Cada entrada define:
#   - requiere: lista de renglones que DEBEN estar presentes con valor > 0
#   - no_requiere: lista de renglones que NO DEBEN estar presentes (o deben
#     tener valor == 0). Si aparece un renglón de esta lista, se lanza error.
#   - nota_render: texto jurídico para la plantilla (cita legal).
#
# NOTA: 'indemnizacion_despido' se usa para termino_fijo_vencido en vez de
# 'indemnizacion' porque la indemnización por despido (Art. 64) NO aplica,
# pero la indemnización por preaviso (Art. 46) SÍ puede aplicar.

REQUISITOS_POR_MOTIVO: Dict[str, Dict[str, Any]] = {
    "renuncia_voluntaria": {
        "requiere": ["vacaciones"],
        "no_requiere": ["indemnizacion"],
        "nota_render": (
            "NO HAY INDEMNIZACIÓN: el trabajador renunció voluntariamente "
            "(Art. 49 num. 6 CST). No se genera indemnización conforme al "
            "Art. 64 CST (indemnización por despido sin justa causa, "
            "no aplicable a renuncia del trabajador)."
        ),
    },
    "despido_sin_justa_causa": {
        "requiere": ["vacaciones", "indemnizacion"],
        "no_requiere": [],
        "nota_render": "",
    },
    "despido_con_justa_causa": {
        "requiere": ["vacaciones"],
        "no_requiere": ["indemnizacion"],
        "nota_render": (
            "NO HAY INDEMNIZACIÓN: despido con causa legal (Art. 62 CST)."
        ),
    },
    "termino_fijo_vencido": {
        "requiere": ["vacaciones", "preaviso_check"],
        "no_requiere": ["indemnizacion_despido"],
        "nota_render": (
            "NO HAY INDEMNIZACIÓN POR DESPIDO: contrato a término fijo "
            "vencido. Verificar preaviso Art. 46 CST (si < 30 días → "
            "indemnización preaviso)."
        ),
    },
    "obra_o_labor_terminada": {
        "requiere": ["vacaciones"],
        "no_requiere": ["indemnizacion"],
        "nota_render": (
            "NO HAY INDEMNIZACIÓN: contrato por obra o labor terminada."
        ),
    },
    "mutuo_acuerdo": {
        "requiere": ["vacaciones"],
        "no_requiere": ["indemnizacion"],
        "nota_render": (
            "NO HAY INDEMNIZACIÓN: terminación por mutuo acuerdo."
        ),
    },
    "muerte_trabajador": {
        "requiere": ["vacaciones"],
        "no_requiere": ["indemnizacion"],
        "nota_render": (
            "Pago a herederos conforme al Art. 49 num. 5 CST y normas "
            "sucesoriales."
        ),
    },
    "muerte_empleador": {
        "requiere": ["vacaciones"],
        "no_requiere": [],
        "nota_render": (
            "Verificar si el empleador era persona natural (Art. 49 num. 4)."
        ),
    },
    "suspension_deficitaria": {
        "requiere": ["vacaciones"],
        "no_requiere": ["indemnizacion"],
        "nota_render": "",
    },
    "cierre_empresa": {
        "requiere": ["vacaciones"],
        "no_requiere": ["indemnizacion"],
        "nota_render": "",
    },
}


def obtener_nota_render(motivo: str) -> Optional[str]:
    """Retorna la nota jurídica para un motivo dado, o None si no existe."""
    entrada = REQUISITOS_POR_MOTIVO.get(motivo)
    if entrada is None:
        return None
    nota = entrada.get("nota_render", "")
    return nota if nota else None


class PreRenderValidator:
    """Valida que el desglose cumple los requisitos legales por motivo.

    Antes de renderizar un documento de liquidación, verifica que la
    combinación modo + motivo_terminación + renglones presentes cumple
    los requisitos de la matriz REQUISITOS_POR_MOTIVO.
    """

    def validar_requisitos_por_motivo(
        self,
        inp: Any,
        desglose: Dict[str, Any],
    ) -> None:
        """Valida requisitos de la matriz REQUISITOS_POR_MOTIVO.

        Args:
            inp: LiquidacionInput (Pydantic model). Debe tener
                 contrato.motivo_terminacion.
            desglose: dict con renglones del desglose. Cada clave es un
                      concepto (str) y cada valor es un dict con al menos
                      'valor' (int|Decimal).

        Raises:
            PreRenderValidationError: si falta un renglón requerido o
                si aparece un renglón marcado como no_requiere.
        """
        motivo_enum = getattr(inp.contrato, "motivo_terminacion", None)
        if motivo_enum is None:
            return  # sin motivo, no hay matriz a aplicar

        motivo = motivo_enum.value if hasattr(motivo_enum, "value") else str(motivo_enum)

        requisitos = REQUISITOS_POR_MOTIVO.get(motivo)
        if requisitos is None:
            return  # motivo no catalogado: no aplicar matriz

        # Verificar renglones requeridos
        for req in requisitos["requiere"]:
            renglon = desglose.get(req)
            if renglon is None:
                raise PreRenderValidationError(
                    f"FINIQUITO por motivo '{motivo}' requiere renglón "
                    f"'{req}' en el desglose. Art. 49-64 CST."
                )
            valor = renglon.get("valor", 0) if isinstance(renglon, dict) else renglon
            if valor == 0:
                raise PreRenderValidationError(
                    f"FINIQUITO por motivo '{motivo}' requiere renglón "
                    f"'{req}' con valor > 0 en el desglose. Art. 49-64 CST."
                )

        # Verificar renglones que NO deben estar
        for no_req in requisitos["no_requiere"]:
            renglon = desglose.get(no_req)
            if renglon is None:
                continue  # no está, OK
            valor = renglon.get("valor", 0) if isinstance(renglon, dict) else renglon
            if valor > 0:
                raise PreRenderValidationError(
                    f"FINIQUITO por motivo '{motivo}' NO debe incluir "
                    f"renglón '{no_req}'. {requisitos['nota_render']}"
                )
