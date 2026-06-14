"""
Calculador de Salario Base de Liquidación (SBL)
Implementa las diferentes variantes de SBL según el concepto a liquidar.

Referencia Legal:
- SBL_GENERAL: Incluye todos los componentes salariales habituales
- SBL_VACACIONES: Excluye horas extras, recargos y auxilios (Art. 192 CST)
- SBL_PRIMA: Similar a SBL_GENERAL o con reglas específicas según variabilidad
"""

from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from ..utils.constants import DEFAULT_SMMLV


class SBLCalculator:
    """
    Calculador de Salario Base de Liquidación en sus diferentes modalidades.
    """

    def __init__(self, params: dict):
        """
        Inicializa el calculador con parámetros legales.

        Args:
            params: Diccionario con parámetros legales (SMMLV, límites, etc.)
        """
        self.params = params
        self.smmlv = params.get("SMMLV", DEFAULT_SMMLV)
        self.limite_auxilio = params.get("LIMITE_AUXILIO", 2 * self.smmlv)
        self.alertas: list[dict[str, Any]] = []

    def calculate_sbl_general(
        self,
        salario_mensual: int,
        comisiones_promedio_mensual: float = 0,
        horas_extras_promedio_mensual: float = 0,
        bonificaciones_promedio_mensual: float = 0,
        auxilio_transporte: int = 0,
        auxilio_conectividad: int = 0,
        reside_en_lugar_trabajo: bool = False,
        auxilio_conectividad_pactado: bool = False,
    ) -> tuple[Decimal, list[dict[str, Any]]]:
        """
        Calcula el SBL_GENERAL para cesantías, prima e indemnización.

        Incluye:
        - Salario base mensual
        - Comisiones promedio
        - Horas extras promedio
        - Bonificaciones promedio
        - Auxilio de transporte (condicional)
        - Auxilio de conectividad (condicional)

        Args:
            salario_mensual: Salario base mensual pactado
            comisiones_promedio_mensual: Promedio mensual de comisiones
            horas_extras_promedio_mensual: Promedio mensual de horas extras
            bonificaciones_promedio_mensual: Promedio mensual de bonificaciones
            auxilio_transporte: Valor del auxilio de transporte
            auxilio_conectividad: Valor del auxilio de conectividad
            reside_en_lugar_trabajo: Si el trabajador reside en el lugar de trabajo
            auxilio_conectividad_pactado: Si el auxilio está pactado como salario

        Returns:
            Tuple con:
            - SBL_GENERAL calculado
            - Lista de alertas generadas
        """
        alertas = []
        componentes = {
            "salario_base": Decimal(str(salario_mensual)),
            "comisiones": Decimal(str(comisiones_promedio_mensual)),
            "horas_extras": Decimal(str(horas_extras_promedio_mensual)),
            "bonificaciones": Decimal(str(bonificaciones_promedio_mensual)),
            "auxilio_transporte": Decimal("0"),
            "auxilio_conectividad": Decimal("0"),
        }

        # Validar y aplicar auxilio de transporte
        if auxilio_transporte > 0:
            if reside_en_lugar_trabajo:
                alertas.append(
                    {
                        "tipo": "EXCLUSION",
                        "concepto": "auxilio_transporte",
                        "razon": "Trabajador reside en el lugar de trabajo (Finca Rural)",
                        "valor_excluido": auxilio_transporte,
                        "norma": "Jurisprudencia CST - Auxilio Transporte Finca Rural",
                    }
                )
            elif salario_mensual >= self.limite_auxilio:
                alertas.append(
                    {
                        "tipo": "EXCLUSION",
                        "concepto": "auxilio_transporte",
                        "razon": f"Salario excede o es igual límite de 2 SMMLV ({self.limite_auxilio:,})",
                        "valor_excluido": auxilio_transporte,
                        "norma": "Art. 7 Ley 1 de 1963, modificado por Art. 2 Ley 2101 de 2021",
                    }
                )
            else:
                componentes["auxilio_transporte"] = Decimal(str(auxilio_transporte))

        # Validar y aplicar auxilio de transporte
        if auxilio_conectividad > 0:
            if not auxilio_conectividad_pactado:
                alertas.append(
                    {
                        "tipo": "WARNING",
                        "concepto": "auxilio_conectividad",
                        "razon": "Auxilio de transporte NO está explícitamente pactado como parte del salario habitual. Debe excluirse del SBL si es un beneficio no constitutivo de salario.",
                        "valor": auxilio_conectividad,
                        "norma": "Art. 128 CST - Factor Salarial",
                    }
                )
                # NO incluir si no está pactado
            else:
                if salario_mensual >= self.limite_auxilio:
                    alertas.append(
                        {
                            "tipo": "EXCLUSION",
                            "concepto": "auxilio_conectividad",
                            "razon": f"Salario excede límite de 2 SMMLV ({self.limite_auxilio:,})",
                            "valor_excluido": auxilio_conectividad,
                            "norma": "Art. 7 Ley 1 de 1963 (aplicación analógica)",
                        }
                    )
                else:
                    componentes["auxilio_conectividad"] = Decimal(
                        str(auxilio_conectividad)
                    )
                    alertas.append(
                        {
                            "tipo": "INFO",
                            "concepto": "auxilio_conectividad",
                            "razon": "Auxilio de transporte incluido por estar pactado como salario",
                            "valor": auxilio_conectividad,
                            "norma": "Art. 128 CST",
                        }
                    )

        # Calcular SBL_GENERAL
        sbl_general = sum(componentes.values())
        sbl_general = Decimal(str(sbl_general))

        # Redondear según parámetros
        redondeo = self.params.get("REDONDEO", 0)
        if redondeo == 0:
            sbl_general = sbl_general.quantize(Decimal("1"), rounding=ROUND_HALF_UP)

        self.alertas.extend(alertas)

        return sbl_general, alertas

    def calculate_sbl_vacaciones(
        self, salario_mensual: int, comisiones_promedio_mensual: float = 0
    ) -> tuple[Decimal, list[dict[str, Any]]]:
        """
        Calcula el SBL_VACACIONES.

        Incluye SOLO:
        - Salario base mensual
        - Comisiones promedio

        Excluye explícitamente:
        - Horas extras
        - Recargos nocturnos/dominicales/festivos
        - Auxilio de transporte
        - Auxilio de conectividad

        Referencia: Arts. 186-192 CST

        Args:
            salario_mensual: Salario base mensual pactado
            comisiones_promedio_mensual: Promedio mensual de comisiones

        Returns:
            Tuple con:
            - SBL_VACACIONES calculado
            - Lista de alertas (generalmente vacía para este cálculo)
        """
        alertas = []

        sbl_vacaciones = Decimal(str(salario_mensual)) + Decimal(
            str(comisiones_promedio_mensual)
        )

        # Redondear según parámetros
        redondeo = self.params.get("REDONDEO", 0)
        if redondeo == 0:
            sbl_vacaciones = sbl_vacaciones.quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )

        alertas.append(
            {
                "tipo": "INFO",
                "concepto": "sbl_vacaciones",
                "razon": "SBL para vacaciones excluye horas extras, recargos y auxilios",
                "norma": "Arts. 186-192 CST",
            }
        )

        return sbl_vacaciones, alertas

    def calculate_sbl_prima(
        self,
        salario_mensual: int,
        comisiones_promedio_mensual: float = 0,
        horas_extras_promedio_mensual: float = 0,
        bonificaciones_promedio_mensual: float = 0,
        auxilio_transporte: int = 0,
        auxilio_conectividad: int = 0,
        reside_en_lugar_trabajo: bool = False,
        auxilio_conectividad_pactado: bool = False,
        es_salario_variable: bool = False,
    ) -> tuple[Decimal, list[dict]]:
        """
        Calcula el SBL_PRIMA para prima de servicios.

        Por defecto, usa las mismas reglas que SBL_GENERAL.
        Si el salario es variable, puede requerir promediación semestral específica.

        Referencia: Art. 306-308 CST

        Args:
            salario_mensual: Salario base mensual pactado
            comisiones_promedio_mensual: Promedio mensual de comisiones
            horas_extras_promedio_mensual: Promedio mensual de horas extras
            bonificaciones_promedio_mensual: Promedio mensual de bonificaciones
            auxilio_transporte: Valor del auxilio de transporte
            auxilio_conectividad: Valor del auxilio de conectividad
            reside_en_lugar_trabajo: Si el trabajador reside en el lugar de trabajo
            auxilio_conectividad_pactado: Si el auxilio está pactado como salario
            es_salario_variable: Si el salario tiene componentes variables

        Returns:
            Tuple con:
            - SBL_PRIMA calculado
            - Lista de alertas generadas
        """
        # Para prima, usamos las mismas reglas que SBL_GENERAL
        sbl_prima, alertas = self.calculate_sbl_general(
            salario_mensual=salario_mensual,
            comisiones_promedio_mensual=comisiones_promedio_mensual,
            horas_extras_promedio_mensual=horas_extras_promedio_mensual,
            bonificaciones_promedio_mensual=bonificaciones_promedio_mensual,
            auxilio_transporte=auxilio_transporte,
            auxilio_conectividad=auxilio_conectividad,
            reside_en_lugar_trabajo=reside_en_lugar_trabajo,
            auxilio_conectividad_pactado=auxilio_conectividad_pactado,
        )

        if es_salario_variable:
            alertas.append(
                {
                    "tipo": "INFO",
                    "concepto": "sbl_prima",
                    "razon": "Salario variable: se usa promedio del semestre correspondiente",
                    "norma": "Art. 307 CST",
                }
            )

        return sbl_prima, alertas

    def apply_auxilio_rules(
        self,
        salario_mensual: int,
        auxilio_transporte: int,
        auxilio_conectividad: int,
        reside_en_lugar_trabajo: bool,
        auxilio_conectividad_pactado: bool,
    ) -> dict:
        """
        Aplica y valida las reglas de auxilio de transporte y conectividad.

        Args:
            salario_mensual: Salario base mensual
            auxilio_transporte: Valor del auxilio de transporte
            auxilio_conectividad: Valor del auxilio de conectividad
            reside_en_lugar_trabajo: Si reside en lugar de trabajo
            auxilio_conectividad_pactado: Si auxilio está pactado

        Returns:
            Dict con resultado de validación y alertas
        """
        resultado: dict[str, Any] = {
            "auxilio_transporte_aplica": False,
            "auxilio_transporte_valor": 0,
            "auxilio_conectividad_aplica": False,
            "auxilio_conectividad_valor": 0,
            "alertas": [],
        }

        # Validar auxilio de transporte
        if auxilio_transporte > 0:
            if reside_en_lugar_trabajo:
                resultado["alertas"].append(
                    {
                        "tipo": "EXCLUSION",
                        "concepto": "auxilio_transporte",
                        "razon": "Residencia en lugar de trabajo (Finca Rural)",
                        "norma": "Jurisprudencia CST",
                    }
                )
            elif salario_mensual > self.limite_auxilio:
                resultado["alertas"].append(
                    {
                        "tipo": "EXCLUSION",
                        "concepto": "auxilio_transporte",
                        "razon": f"Salario excede 2 SMMLV ({self.limite_auxilio:,})",
                        "norma": "Ley 1/1963 Art. 7, mod. Ley 2101/2021",
                    }
                )
            else:
                resultado["auxilio_transporte_aplica"] = True
                resultado["auxilio_transporte_valor"] = auxilio_transporte

        # Validar auxilio de conectividad
        if auxilio_conectividad > 0:
            if not auxilio_conectividad_pactado:
                resultado["alertas"].append(
                    {
                        "tipo": "WARNING",
                        "concepto": "auxilio_conectividad",
                        "razon": "NO pactado como salario habitual - debe excluirse",
                        "valor": auxilio_conectividad,
                        "norma": "Art. 128 CST",
                    }
                )
            elif salario_mensual > self.limite_auxilio:
                resultado["alertas"].append(
                    {
                        "tipo": "EXCLUSION",
                        "concepto": "auxilio_conectividad",
                        "razon": f"Salario excede 2 SMMLV ({self.limite_auxilio:,})",
                        "norma": "Aplicación analógica Ley 1/1963",
                    }
                )
            else:
                resultado["auxilio_conectividad_aplica"] = True
                resultado["auxilio_conectividad_valor"] = auxilio_conectividad

        return resultado

    def calculate_promedio_variable(
        self, salarios_historicos: list[dict[str, float]], meses_requeridos: int = 12
    ) -> tuple[Decimal, list[dict]]:
        """
        Calcula el promedio de salarios variables para los últimos N meses.

        Usado cuando el trabajador tiene componentes salariales variables
        (comisiones, horas extras fluctuantes, etc.)

        Referencia: Jurisprudencia CSJ 2025 - Promediación salario variable

        Args:
            salarios_historicos: Lista de dicts con 'periodo' (YYYY-MM) y 'valor'
            meses_requeridos: Número de meses a promediar (default: 12)

        Returns:
            Tuple con:
            - Promedio calculado
            - Lista de alertas sobre el cálculo
        """
        alertas = []

        if not salarios_historicos:
            alertas.append(
                {
                    "tipo": "ERROR",
                    "concepto": "promedio_variable",
                    "razon": "No hay histórico de salarios para calcular promedio",
                    "norma": "Jurisprudencia CSJ 2025",
                }
            )
            return Decimal("0"), alertas

        # Ordenar por periodo descendente
        historicos_ordenados = sorted(
            salarios_historicos, key=lambda x: x["periodo"], reverse=True
        )

        # Tomar últimos N meses disponibles
        meses_disponibles = min(len(historicos_ordenados), meses_requeridos)
        ultimos_meses = historicos_ordenados[:meses_disponibles]

        if meses_disponibles < meses_requeridos:
            alertas.append(
                {
                    "tipo": "WARNING",
                    "concepto": "promedio_variable",
                    "razon": f"Solo {meses_disponibles} meses disponibles (se requieren {meses_requeridos})",
                    "norma": "Jurisprudencia CSJ 2025",
                }
            )

        # Calcular promedio
        suma_total = sum(Decimal(str(mes["valor"])) for mes in ultimos_meses)
        promedio = suma_total / Decimal(str(meses_disponibles))

        # Redondear
        redondeo = self.params.get("REDONDEO", 0)
        if redondeo == 0:
            promedio = promedio.quantize(Decimal("1"), rounding=ROUND_HALF_UP)

        alertas.append(
            {
                "tipo": "INFO",
                "concepto": "promedio_variable",
                "razon": f"Promedio calculado sobre {meses_disponibles} meses",
                "periodos": [mes["periodo"] for mes in ultimos_meses],
                "norma": "Jurisprudencia CSJ 2025",
            }
        )

        return promedio, alertas

    def get_alertas(self) -> list[dict]:
        """
        Retorna todas las alertas generadas durante los cálculos.

        Returns:
            Lista de alertas
        """
        return self.alertas

    def reset_alertas(self):
        """
        Limpia las alertas acumuladas.
        """
        self.alertas = []
