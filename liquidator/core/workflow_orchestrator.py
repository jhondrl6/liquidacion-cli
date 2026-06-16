"""Motor de orquestación de cálculos para la liquidación.

Tarea 2.B-bis (S27): integración de ``SalarioResolver`` para anualización
salarial SL2630-2024 — cada año calendario se liquida con el SBL de ESE año.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

try:
    from liquidator.contracts.input_model import Salario
except ImportError:
    Salario = None  # type: ignore[assignment]

from liquidator.calculators.indemnizacion_calculator import IndemnizacionCalculator
from liquidator.calculators.prestaciones_calculator import PrestacionesCalculator
from liquidator.calculators.sbl_calculator import SBLCalculator
from liquidator.calculators.vacaciones_calculator import VacacionesCalculator
from liquidator.core.salario_resolver import (
    SalarioResolver,
    SegmentoCalculo,
    segmentar_periodo,
)


@dataclass(frozen=True)
class WorkflowResult:
    calculation_results: dict[str, Any]
    compliance_payload: dict[str, Any]
    validaciones_y_alertas: dict[str, str]
    normas_aplicadas: list[str]


class WorkflowOrchestrator:
    """Coordina todos los cálculos requeridos para la liquidación."""

    def __init__(self, params: dict[str, Any]):
        self.params = params
        self.sbl_calc = SBLCalculator(params)
        self.prest_calc = PrestacionesCalculator(params)
        self.vac_calc = VacacionesCalculator(params)
        self.indemn_calc = IndemnizacionCalculator(params)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def execute(self, input_data: dict[str, Any]) -> WorkflowResult:
        modo = input_data.get("modo", "PERIÓDICA")
        fecha_ingreso = input_data.get("fecha_ingreso")
        fecha_corte = input_data.get("fecha_corte")

        # --- Resolver SBL: flat vs nested + SalarioResolver (2.B-bis) ---
        salario_mensual = self._extraer_salario_mensual(input_data)

        auxilio_transporte = input_data.get("auxilio_transporte")
        if auxilio_transporte is None:
            auxilio_transporte = self.params.get("AUXILIO_TRANS", 0)

        sbl_general_dec, alerts_general = self.sbl_calc.calculate_sbl_general(
            salario_mensual=salario_mensual,
            comisiones_promedio_mensual=input_data.get(
                "comisiones_promedio_mensual", 0
            ),
            horas_extras_promedio_mensual=input_data.get(
                "horas_extras_promedio_mensual", 0
            ),
            bonificaciones_promedio_mensual=input_data.get(
                "bonificaciones_promedio_mensual", 0
            ),
            auxilio_transporte=auxilio_transporte,
            auxilio_conectividad=input_data.get("auxilio_conectividad", 0),
            reside_en_lugar_trabajo=input_data.get("reside_en_lugar_trabajo", False),
            auxilio_conectividad_pactado=input_data.get(
                "auxilio_conectividad_pactado", True
            ),
        )

        sbl_vacaciones_dec, alerts_vacaciones = self.sbl_calc.calculate_sbl_vacaciones(
            salario_mensual=salario_mensual,
            comisiones_promedio_mensual=input_data.get(
                "comisiones_promedio_mensual", 0
            ),
        )

        sbl_prima_dec, alerts_prima = self.sbl_calc.calculate_sbl_prima(
            salario_mensual=salario_mensual,
            comisiones_promedio_mensual=input_data.get(
                "comisiones_promedio_mensual", 0
            ),
            horas_extras_promedio_mensual=input_data.get(
                "horas_extras_promedio_mensual", 0
            ),
            bonificaciones_promedio_mensual=input_data.get(
                "bonificaciones_promedio_mensual", 0
            ),
            auxilio_transporte=auxilio_transporte,
            auxilio_conectividad=input_data.get("auxilio_conectividad", 0),
            reside_en_lugar_trabajo=input_data.get("reside_en_lugar_trabajo", False),
            auxilio_conectividad_pactado=input_data.get(
                "auxilio_conectividad_pactado", True
            ),
            es_salario_variable=bool(input_data.get("salarios_historicos")),
        )

        sbl_general = int(sbl_general_dec)
        sbl_vacaciones = int(sbl_vacaciones_dec)
        sbl_prima = int(sbl_prima_dec)

        # --- 2.B-bis: segmentación por año calendario si hay Resolver ---
        salario_resolver = self._build_salario_resolver(input_data)
        if salario_resolver is not None and fecha_ingreso and fecha_corte:
            cesantias_data, intereses_data, prima_data = self._calcular_prestaciones_segmentadas(
                salario_resolver,
                fecha_ingreso,
                fecha_corte,
                modo,
            )
            dias_servicio = self.prest_calc.calculate_dias_servicio(
                fecha_ingreso, fecha_corte
            )
        else:
            dias_servicio = self.prest_calc.calculate_dias_servicio(
                fecha_ingreso, fecha_corte
            )
            cesantias_data = self.prest_calc.calculate_cesantias(
                sbl_general, dias_servicio, fecha_ingreso, fecha_corte
            )
            intereses_data = self.prest_calc.calculate_intereses_cesantias(
                cesantias_data["valor"], dias_servicio, fecha_ingreso, fecha_corte
            )
            prima_data = self.prest_calc.calculate_prima(
                sbl_prima, fecha_ingreso, fecha_corte
            )

        if modo == "FINIQUITO":
            for concepto in (cesantias_data, intereses_data, prima_data):
                concepto["plazo_pago_legal"] = fecha_corte
        modo_sin_acentos = modo.replace("Ó", "O") if isinstance(modo, str) else modo
        vacaciones_input = dict(input_data)
        vacaciones_input["modo"] = modo_sin_acentos
        vacaciones_data = self.vac_calc.calculate_vacaciones_completas(
            vacaciones_input, sbl_vacaciones
        )

        indemnizacion_pack = self.indemn_calc.calculate_indemnizacion_completa(
            input_data, sbl_general
        )

        norm_set = {
            cesantias_data.get("norma", "Art.249-250 CST"),
            intereses_data.get("norma", "Ley 50/1990 Art.99"),
            prima_data.get("norma", "Art.306-308 CST"),
        }
        if vacaciones_data.get("norma"):
            norm_set.add(vacaciones_data["norma"])
        if indemnizacion_pack["indemnizacion"].get("norma"):
            norm_set.add(indemnizacion_pack["indemnizacion"]["norma"])
        if indemnizacion_pack["salario_pendiente"].get("norma"):
            norm_set.add(indemnizacion_pack["salario_pendiente"]["norma"])

        desglose = {
            "SBL_GENERAL": sbl_general,
            "SBL_VACACIONES": sbl_vacaciones,
            "cesantias": {
                "valor": cesantias_data["valor"],
                "dias_liquidados": cesantias_data["dias_liquidados"],
                "plazo_pago_legal": cesantias_data["plazo_pago_legal"],
                "norma": cesantias_data["norma"],
            },
            "intereses_cesantias": {
                "valor": intereses_data["valor"],
                "dias_liquidados": intereses_data["dias_liquidados"],
                "plazo_pago_legal": intereses_data["plazo_pago_legal"],
                "norma": intereses_data["norma"],
            },
            "prima": {
                "valor": prima_data["valor"],
                "dias_liquidados": prima_data["dias_liquidados"],
                "plazo_pago_legal": prima_data.get("plazo_pago_legal"),
                "norma": prima_data["norma"],
            },
            "vacaciones": {
                "valor": vacaciones_data["valor"],
                "dias_liquidados": vacaciones_data["dias_liquidados"],
                "norma": vacaciones_data.get("norma", "Arts.186-192 CST"),
                "nota": vacaciones_data.get("nota", ""),
            },
        }

        calculation_results = {
            "sbl_general": sbl_general,
            "sbl_vacaciones": sbl_vacaciones,
            "cesantias": cesantias_data["valor"],
            "dias_cesantias": cesantias_data["dias_liquidados"],
            "plazo_cesantias": cesantias_data["plazo_pago_legal"],
            "intereses_cesantias": intereses_data["valor"],
            "dias_intereses": intereses_data["dias_liquidados"],
            "plazo_intereses": intereses_data["plazo_pago_legal"],
            "prima": prima_data["valor"],
            "dias_prima": prima_data["dias_liquidados"],
            "plazo_prima": prima_data.get("plazo_pago_legal"),
            "vacaciones": vacaciones_data["valor"],
            "dias_vacaciones": vacaciones_data["dias_liquidados"],
            "dias_servicio": dias_servicio,
        }

        calculation_results["desglose"] = desglose

        if modo == "FINIQUITO":
            indemnizacion = indemnizacion_pack["indemnizacion"]
            salario_pendiente = indemnizacion_pack["salario_pendiente"]
            if indemnizacion.get("aplica"):
                desglose["indemnizacion"] = {
                    "valor": indemnizacion["valor"],
                    "dias_liquidados": indemnizacion.get("dias_indemnizacion", 0),
                    "norma": indemnizacion.get("norma", "Art.64 CST"),
                    "nota": indemnizacion.get("nota", ""),
                }
                calculation_results["indemnizacion"] = indemnizacion["valor"]
            else:
                calculation_results["indemnizacion"] = 0

            desglose["salario_pendiente"] = {
                "valor": salario_pendiente.get("valor", 0),
                "dias_liquidados": salario_pendiente.get("dias_pendientes", 0),
                "norma": salario_pendiente.get("norma", "Art.65 CST"),
                "nota": salario_pendiente.get("nota", ""),
            }
            calculation_results["salario_pendiente"] = salario_pendiente.get(
                "valor", 0
            )

        alerts = self._build_alerts(
            alerts_general + alerts_vacaciones + alerts_prima,
            vacaciones_data,
            modo,
        )

        calculation_results["validaciones_y_alertas"] = alerts

        # Calcular total dinámico
        total_liquidacion = 0
        for _, datos in desglose.items():
            if isinstance(datos, dict) and "valor" in datos:
                valor = datos.get("valor", 0)
                if isinstance(valor, (int, float)) and valor > 0:
                    total_liquidacion += valor

        calculation_results["total"] = total_liquidacion
        calculation_results["total_liquidacion"] = total_liquidacion

        compliance_payload = {
            "meta": {
                "modo": modo,
                "fecha_corte": fecha_corte,
                "fecha_ingreso": fecha_ingreso,
            },
            "desglose": desglose,
        }

        return WorkflowResult(
            calculation_results=calculation_results,
            compliance_payload=compliance_payload,
            validaciones_y_alertas=alerts,
            normas_aplicadas=sorted(norm_set),
        )

    # ------------------------------------------------------------------
    # 2.B-bis — anualización salarial (SL2630-2024)
    # ------------------------------------------------------------------

    def _extraer_salario_mensual(self, input_data: dict[str, Any]) -> float:
        """Extrae ``salario_mensual`` del input, soportando formato plano y
        anidado (``salario.SBL`` de la Tarea 1.C-bis)."""
        # Forma 2 (anidada) — Pydantic Salario
        salario_obj = input_data.get("salario")
        if isinstance(salario_obj, dict) and "SBL" in salario_obj:
            return float(salario_obj["SBL"])
        # Forma 1 (plana)
        return float(input_data.get("salario_mensual", 0))

    def _build_salario_resolver(
        self, input_data: dict[str, Any]
    ) -> SalarioResolver | None:
        """Construye un ``SalarioResolver`` si el input tiene los campos
        de anualización (1.C-bis). Retorna ``None`` si no aplica."""
        salario_obj = input_data.get("salario")
        if not isinstance(salario_obj, dict):
            return None
        # Solo activamos si hay campos de anualización
        if "sbl_por_anio" not in salario_obj and "historial_salarial" not in salario_obj:
            return None
        if Salario is None:
            return None
        try:
            salario_model = Salario.model_validate(salario_obj)
            return SalarioResolver(salario_model)
        except Exception:
            return None

    def _calcular_prestaciones_segmentadas(
        self,
        resolver: SalarioResolver,
        fecha_ingreso: str,
        fecha_corte: str,
        modo: str,
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        """Calcula cesantías, intereses y prima por año calendario.

        SL2630-2024: cada año se liquida con el SBL de ESE año.
        Cesantías e intereses son estrictamente proporcionales a los días
        → se segmentan y suman.  Prima es semestral y usa el SBL del año
        de la ``fecha_corte``.
        """
        desde = datetime.strptime(fecha_ingreso, "%Y-%m-%d").date()
        hasta = datetime.strptime(fecha_corte, "%Y-%m-%d").date()
        segmentos = segmentar_periodo(desde, hasta)

        cesantias_total = 0
        dias_cesantias_total = 0

        for seg in segmentos:
            seg.sbl = resolver.sbl_para_segmento(seg)
            sbl_seg = float(seg.sbl)
            desde_str = seg.desde.isoformat()
            hasta_str = seg.hasta.isoformat()

            # Cesantías del segmento
            cdata = self.prest_calc.calculate_cesantias(
                sbl_seg, seg.dias, desde_str, hasta_str
            )
            cesantias_total += cdata["valor"]
            dias_cesantias_total += cdata["dias_liquidados"]

        # Intereses sobre cesantías: usan las cesantías TOTALES como base,
        # no la suma de intereses por segmento (fórmula legal: Art. 99
        # Ley 50/1990 = cesantías × días_totales × 12% / 360).
        dias_totales = sum(seg.dias for seg in segmentos)
        intereses_raw = self.prest_calc.calculate_intereses_cesantias(
            cesantias_total, dias_totales, fecha_ingreso, fecha_corte
        )

        # Prima: no se segmenta — usa el SBL del año de fecha_corte
        sbl_prima_seg = resolver.sbl_para_segmento(
            SegmentoCalculo(
                anio=hasta.year,
                desde=hasta,
                hasta=hasta,
                sbl=Decimal("0"),
                dias=0,
            )
        )
        sbl_prima_val = int(sbl_prima_seg)
        prima_data = self.prest_calc.calculate_prima(
            sbl_prima_val, fecha_ingreso, fecha_corte
        )

        # Armar resultados con la misma forma que el flujo plano
        cesantias_data = {
            "valor": cesantias_total,
            "dias_liquidados": dias_cesantias_total,
            "sbl_utilizado": None,
            "formula": f"Suma de {len(segmentos)} segmento(s) anual(es) — SL2630-2024",
            "plazo_pago_legal": "ver compliance engine",
            "norma": "Art. 249-250 CST; SL2630-2024",
            "metadata": {
                "fecha_ingreso": fecha_ingreso,
                "fecha_corte": fecha_corte,
                "segmentos": len(segmentos),
                "anualizacion": "SL2630-2024",
            },
        }

        intereses_data = {
            "valor": intereses_raw["valor"],
            "dias_liquidados": intereses_raw["dias_liquidados"],
            "tasa_aplicada": 0.12,
            "cesantias_base": cesantias_total,
            "formula": f"Suma de {len(segmentos)} segmento(s) anual(es) — SL2630-2024",
            "plazo_pago_legal": "ver compliance engine",
            "norma": "Ley 50/1990 Art. 99; SL2630-2024",
            "metadata": {
                "fecha_ingreso": fecha_ingreso,
                "fecha_corte": fecha_corte,
                "segmentos": len(segmentos),
            },
        }

        if modo == "FINIQUITO":
            for concepto in (cesantias_data, intereses_data, prima_data):
                concepto["plazo_pago_legal"] = fecha_corte

        return cesantias_data, intereses_data, prima_data

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------

    def _build_alerts(
        self,
        alertas_raw: list[dict[str, Any]],
        vacaciones_data: dict[str, Any],
        modo: str,
    ) -> dict[str, str]:
        alertas: dict[str, str] = {}
        mapping = {"EXCLUSION": "excluido", "WARNING": "advertencia", "INFO": "info"}

        for alerta in alertas_raw:
            concepto = alerta.get("concepto", "alerta")
            tipo = mapping.get(
                alerta.get("tipo", "INFO"), alerta.get("tipo", "info").lower()
            )
            key = f"{concepto}_{tipo}".lower()
            mensaje = alerta.get("razon") or alerta.get("nota") or ""
            if alerta.get("valor_excluido"):
                mensaje = f"{mensaje} (valor excluido: {alerta['valor_excluido']:,})"
            if alerta.get("valor") and "valor" not in mensaje:
                mensaje = f"{mensaje} (valor: {alerta['valor']:,})".strip()
            alertas[key] = mensaje.strip() or concepto

        if modo == "FINIQUITO":
            alertas.setdefault(
                "plazo_pago_inmediato",
                "Modo FINIQUITO: todas las prestaciones deben pagarse en la fecha de terminación.",
            )

        if vacaciones_data.get("nota"):
            alertas.setdefault("vacaciones_nota", vacaciones_data["nota"])

        return alertas
