"""Motor de orquestación de cálculos para la liquidación."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from liquidator.calculators.sbl_calculator import SBLCalculator
from liquidator.calculators.prestaciones_calculator import PrestacionesCalculator
from liquidator.calculators.vacaciones_calculator import VacacionesCalculator
from liquidator.calculators.indemnizacion_calculator import IndemnizacionCalculator


@dataclass(frozen=True)
class WorkflowResult:
    calculation_results: Dict[str, Any]
    compliance_payload: Dict[str, Any]
    validaciones_y_alertas: Dict[str, str]
    normas_aplicadas: List[str]


class WorkflowOrchestrator:
    """Coordina todos los cálculos requeridos para la liquidación."""

    def __init__(self, params: Dict[str, Any]):
        self.params = params
        self.sbl_calc = SBLCalculator(params)
        self.prest_calc = PrestacionesCalculator(params)
        self.vac_calc = VacacionesCalculator(params)
        self.indemn_calc = IndemnizacionCalculator(params)

    def execute(self, input_data: Dict[str, Any]) -> WorkflowResult:
        modo = input_data.get("modo", "PERIÓDICA")
        fecha_ingreso = input_data.get("fecha_ingreso")
        fecha_corte = input_data.get("fecha_corte")

        salario_mensual = input_data.get("salario_mensual", 0)
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
            calculation_results["salario_pendiente"] = salario_pendiente.get("valor", 0)

        alerts = self._build_alerts(
            alerts_general + alerts_vacaciones + alerts_prima,
            vacaciones_data,
            modo,
        )

        calculation_results["validaciones_y_alertas"] = alerts

        # Calcular total dinámico sumando todos los conceptos con valor > 0 en desglose
        # Esto permite agregar nuevos conceptos sin modificar la lógica de totalización
        total_liquidacion = 0
        for concepto, datos in desglose.items():
            if isinstance(datos, dict) and "valor" in datos:
                valor = datos.get("valor", 0)
                if isinstance(valor, (int, float)) and valor > 0:
                    total_liquidacion += valor

        calculation_results["total"] = total_liquidacion

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

    def _build_alerts(
        self,
        alertas_raw: List[Dict[str, Any]],
        vacaciones_data: Dict[str, Any],
        modo: str,
    ) -> Dict[str, str]:
        alertas: Dict[str, str] = {}
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
