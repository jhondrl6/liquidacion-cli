# liquidator/calculators/indemnizacion_calculator.py
"""
Módulo para el cálculo de indemnizaciones según la normativa colombiana.
Este módulo implementa las reglas para calcular indemnizaciones por terminación
sin justa causa, aplicación de topes legales y cálculo de salarios pendientes.
"""

from typing import Dict, Any
from ..utils.date_utils import (
    calculate_days_between,
    calculate_years_of_service,
)
from ..utils.currency_utils import round_currency
from ..legal.topes_manager import TopesManager


class IndemnizacionCalculator:
    """
    Calculador de indemnizaciones según normativa colombiana.
    Responsabilidades:
    - Calcular indemnización por terminación sin justa causa
    - Aplicar tope de 20 SMMLV
    - Diferenciar entre contratos indefinidos y a término fijo
    - Calcular salarios pendientes
    """

    def __init__(self, params: Dict[str, Any]):
        """
        Inicializa el calculador con los parámetros legales vigentes.

        Args:
            params: Diccionario con parámetros legales (SMMLV, topes, etc.)
        """
        self.params = params
        self.topes_manager = TopesManager(params)

    def calculate_indemnizacion_sin_justa_causa(
        self,
        sbl_general: float,
        fecha_ingreso: str,
        fecha_corte: str,
        tipo_contrato: str,
        motivo_terminacion: str,
    ) -> Dict[str, Any]:
        """
        Calcula la indemnización por terminación sin justa causa.

        Reglas según Art. 64 CST:
        - Contrato indefinido: 30 días de salario por año de servicio, o fracción
        - Contrato a término fijo: Salario proporcional al tiempo no cumplido

        Args:
            sbl_general: Salario Base de Liquidación general
            fecha_ingreso: Fecha de ingreso del trabajador (YYYY-MM-DD)
            fecha_corte: Fecha de terminación del contrato (YYYY-MM-DD)
            tipo_contrato: "indefinido" o "fijo"
            motivo_terminacion: Motivo de la terminación del contrato

        Returns:
            Dict[str, Any]: Resultado con valor, días, y metadatos
        """
        resultado = {
            "valor": 0.0,
            "dias_indemnizacion": 0,
            "tipo_calculo": "",
            "aplica": False,
            "norma": "Art.64 CST",
            "nota": "",
        }

        # Verificar si aplica indemnización
        if not self._aplica_indemnizacion(motivo_terminacion):
            resultado["nota"] = (
                "No aplica indemnización para este motivo de terminación"
            )
            return resultado

        resultado["aplica"] = True

        if tipo_contrato.lower() == "indefinido":
            return self._calculate_indemnizacion_indefinido(
                sbl_general, fecha_ingreso, fecha_corte
            )
        elif tipo_contrato.lower() in ["fijo", "termino_fijo", "a_termino_fijo"]:
            return self._calculate_indemnizacion_termino_fijo(
                sbl_general, fecha_ingreso, fecha_corte
            )
        else:
            raise ValueError(f"Tipo de contrato no válido: {tipo_contrato}")

    def _aplica_indemnizacion(self, motivo_terminacion: str) -> bool:
        """
        Determina si aplica indemnización según el motivo de terminación.

        Aplica indemnización para:
        - Sin justa causa
        - Por parte del empleador sin justa causa
        - Por fuerza mayor (con límites)

        No aplica para:
        - Justa causa
        - Renuncia voluntaria
        - Mutuo acuerdo (dependiendo de condiciones)

        Args:
            motivo_terminacion: Motivo de la terminación del contrato

        Returns:
            bool: True si aplica indemnización, False en caso contrario
        """
        motivos_sin_indemnizacion = [
            "justa_causa",
            "justa causa",
            "renuncia",
            "renuncia_voluntaria",
            "muerte",
            "incapacidad_absoluta",
        ]

        motivo_lower = motivo_terminacion.lower().strip()
        return motivo_lower not in motivos_sin_indemnizacion

    def _calculate_indemnizacion_indefinido(
        self, sbl_general: float, fecha_ingreso: str, fecha_corte: str
    ) -> Dict[str, Any]:
        """
        Calcula indemnización para contrato indefinido.

        Fórmula: 30 días de salario por año de servicio o fracción

        Args:
            sbl_general: Salario Base de Liquidación general
            fecha_ingreso: Fecha de ingreso del trabajador (YYYY-MM-DD)
            fecha_corte: Fecha de terminación del contrato (YYYY-MM-DD)

        Returns:
            Dict[str, Any]: Resultado con valor, días, y metadatos
        """
        dias_servicio = calculate_days_between(fecha_ingreso, fecha_corte)
        years_service = calculate_years_of_service(fecha_ingreso, fecha_corte)

        # Cálculo: 30 días por año de servicio o fracción
        dias_indemnizacion = 0
        if years_service >= 1:
            dias_indemnizacion = int(years_service) * 30
            # Si hay fracción de año, se cuentan 30 días adicionales
            if (years_service - int(years_service)) > 0:
                dias_indemnizacion += 30
        else:
            # Menos de un año: proporcional al tiempo trabajado (máximo 30 días)
            dias_indemnizacion = min(30, dias_servicio)

        # Calcular valor antes del tope
        # 30 días por mes
        valor_bruto = (sbl_general * dias_indemnizacion) / 30

        # Aplicar tope de 20 SMMLV
        valor_con_tope = self.apply_tope_20_smmlv(valor_bruto, sbl_general)

        return {
            "valor": round_currency(
                valor_con_tope, self.params.get("REDONDEO", 0)
            ),
            "dias_indemnizacion": dias_indemnizacion,
            "tipo_calculo": "indefinido",
            "aplica": True,
            "valor_bruto": round_currency(
                valor_bruto, self.params.get("REDONDEO", 0)
            ),
            "tope_aplicado": valor_con_tope != valor_bruto,
            "norma": "Art.64 CST",
            "nota": (
                f"Indemnización contrato indefinido: {dias_indemnizacion} días. "
                f"Tope 20 SMMLV aplicado."
            ),
        }

    def _calculate_indemnizacion_termino_fijo(
        self, sbl_general: float, fecha_ingreso: str, fecha_corte: str
    ) -> Dict[str, Any]:
        """
        Calcula indemnización para contrato a término fijo.

        Fórmula: Salario proporcional al tiempo no cumplido

        Args:
            sbl_general: Salario Base de Liquidación general
            fecha_ingreso: Fecha de ingreso del trabajador (YYYY-MM-DD)
            fecha_corte: Fecha de terminación del contrato (YYYY-MM-DD)

        Returns:
            Dict[str, Any]: Resultado con valor, días, y metadatos
        """
        # NOTA: Para contrato a término fijo, se necesitaría la fecha de finalización
        # original del contrato. Como no está en los parámetros de entrada, se asume
        # que el tiempo no cumplido es el total del contrato.

        dias_servicio = calculate_days_between(fecha_ingreso, fecha_corte)

        # Asumimos un año de contrato para el cálculo (ejemplo)
        dias_contrato_total = 360
        dias_no_cumplidos = dias_contrato_total - dias_servicio

        if dias_no_cumplidos <= 0:
            return {
                "valor": 0.0,
                "dias_indemnizacion": 0,
                "tipo_calculo": "termino_fijo",
                "aplica": False,
                "norma": "Art.64 CST",
                "nota": "Contrato cumplido en su totalidad, no aplica indemnización",
            }

        # Calcular valor proporcional
        # 30 días por mes
        valor_bruto = (sbl_general * dias_no_cumplidos) / 30

        # Aplicar tope de 20 SMMLV
        valor_con_tope = self.apply_tope_20_smmlv(valor_bruto, sbl_general)

        return {
            "valor": round_currency(
                valor_con_tope, self.params.get("REDONDEO", 0)
            ),
            "dias_indemnizacion": dias_no_cumplidos,
            "tipo_calculo": "termino_fijo",
            "aplica": True,
            "valor_bruto": round_currency(
                valor_bruto, self.params.get("REDONDEO", 0)
            ),
            "tope_aplicado": valor_con_tope != valor_bruto,
            "norma": "Art.64 CST",
            "nota": (
                f"Indemnización contrato a término fijo: {dias_no_cumplidos} días no cumplidos. "
                f"Tope 20 SMMLV aplicado."
            ),
        }

    def apply_tope_20_smmlv(
        self, valor_indemnizacion: float, sbl_general: float
    ) -> float:
        """
        Aplica el tope legal de 20 SMMLV a la indemnización.

        Según Art. 64 CST, la indemnización no puede exceder 20 SMMLV.

        Args:
            valor_indemnizacion: Valor calculado de la indemnización
            sbl_general: Salario Base de Liquidación general

        Returns:
            float: Valor de indemnización con tope aplicado si es necesario
        """
        smmlv = self.params.get("SMMLV", 1423500)
        tope_smmlv = self.params.get("TOPE_INDEMNIZACION_SMMLV", 20)
        tope_valor = smmlv * tope_smmlv

        # Si el SBL supera el tope, el máximo es 20 SMMLV
        if sbl_general > smmlv:
            return min(valor_indemnizacion, tope_valor)

        # Si el SBL no supera el SMMLV, no hay tope
        return valor_indemnizacion

    def calculate_salario_pendiente(
        self,
        salario_mensual: float,
        dias_pendientes: int,
        recargos_pendientes: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Calcula el salario pendiente por pagar.

        Fórmula: salario_diario * dias_pendientes + recargos_pendientes

        Args:
            salario_mensual: Salario mensual del trabajador
            dias_pendientes: Días de salario adeudados
            recargos_pendientes: Valor de recargos (nocturnos, dominicales, etc.)

        Returns:
            Dict[str, Any]: Resultado con valor y desglose
        """
        if dias_pendientes < 0:
            raise ValueError("Días pendientes no pueden ser negativos")

        if salario_mensual <= 0:
            raise ValueError("Salario mensual debe ser mayor a cero")

        salario_diario = salario_mensual / 30  # 30 días promedio por mes
        valor_base = salario_diario * dias_pendientes
        valor_total = valor_base + recargos_pendientes

        return {
            "valor": round_currency(valor_total, self.params.get("REDONDEO", 0)),
            "valor_base": round_currency(valor_base, self.params.get("REDONDEO", 0)),
            "recargos": round_currency(
                recargos_pendientes, self.params.get("REDONDEO", 0)
            ),
            "dias_pendientes": dias_pendientes,
            "salario_diario": round_currency(
                salario_diario, self.params.get("REDONDEO", 0)
            ),
            "norma": "Art.65 CST",
            "nota": "Salario pendiente por días no pagados",
        }

    def calculate_indemnizacion_completa(
        self, input_data: Dict[str, Any], sbl_general: float
    ) -> Dict[str, Any]:
        """
        Calcula el resultado completo de indemnización para la liquidación.

        Args:
            input_data: Datos de entrada del trabajador
            sbl_general: Salario Base de Liquidación general

        Returns:
            Dict[str, Any]: Resultado completo con indemnización y salario pendiente
        """
        modo = input_data.get("modo", "PERIODICA")

        resultado = {
            "indemnizacion": {
                "valor": 0.0,
                "aplica": False,
                "nota": "No aplica en modo PERIÓDICA",
            },
            "salario_pendiente": {
                "valor": 0.0,
                "aplica": False,
                "nota": "No calculado",
            },
        }

        if modo.upper() != "FINIQUITO":
            return resultado

        # Calcular indemnización
        tipo_contrato = input_data.get("tipo_contrato", "indefinido")
        motivo_terminacion = input_data.get("motivo_terminacion", "")

        indemnizacion = self.calculate_indemnizacion_sin_justa_causa(
            sbl_general,
            input_data.get("fecha_ingreso"),
            input_data.get("fecha_corte"),
            tipo_contrato,
            motivo_terminacion,
        )

        resultado["indemnizacion"] = indemnizacion

        # Calcular salario pendiente si aplica
        salario_pendiente_dias = input_data.get("salario_pendiente_dias", 0)
        salario_pendiente_valor = input_data.get("salario_pendiente", 0.0)

        if salario_pendiente_dias > 0:
            salario_pendiente = self.calculate_salario_pendiente(
                input_data.get("salario_mensual", 0),
                salario_pendiente_dias,
                (
                    salario_pendiente_valor
                    - (
                        input_data.get("salario_mensual", 0)
                        / 30
                        * salario_pendiente_dias
                    )
                    if salario_pendiente_valor > 0
                    else 0
                ),
            )
            resultado["salario_pendiente"] = salario_pendiente

        return resultado
