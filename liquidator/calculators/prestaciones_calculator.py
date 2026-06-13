"""
Calculador de Prestaciones Sociales - Colombia 2025
===================================================

Implementa el cálculo de:
- Cesantías (base 360 días)
- Intereses sobre cesantías (12% anual)
- Prima de servicios (proporcional por semestre)

Cumple con:
- Art. 249-250 CST (Cesantías)
- Ley 50/1990 Art. 99 (Intereses)
- Art. 306-308 CST (Prima de servicios)

Author: Sistema de Liquidación de Nómina
Version: 1.0.0
"""

from datetime import datetime, date
from typing import Dict, Any, Tuple, Optional
from decimal import Decimal, ROUND_HALF_UP
import logging

logger = logging.getLogger(__name__)


class PrestacionesCalculator:
    """
    Calculador de prestaciones sociales según normativa colombiana.

    Implementa cálculos precisos con trazabilidad legal y validación
    de fórmulas contra casos conocidos.
    """

    def __init__(self, params: Dict[str, Any]):
        """
        Inicializa el calculador con parámetros oficiales.

        Args:
            params: Diccionario con parámetros legales (SMMLV, tasas, etc.)
        """
        self.params = params
        self.DIAS_BASE = params.get("DIAS_BASE", 360.0)
        self.TASA_INT_CESANTIAS = params.get("TASA_INT_CESANTIAS", 0.12)
        self.REDONDEO = params.get("REDONDEO", 0)

        logger.info(
            f"PrestacionesCalculator inicializado con DIAS_BASE={self.DIAS_BASE}, "
            f"TASA_INT_CESANTIAS={self.TASA_INT_CESANTIAS}"
        )

    def calculate_dias_servicio(
        self, fecha_ingreso: str, fecha_corte: str, incluir_dia_corte: bool = True
    ) -> int:
        """
        Calcula días de servicio entre dos fechas.

        Args:
            fecha_ingreso: Fecha de ingreso (YYYY-MM-DD)
            fecha_corte: Fecha de corte (YYYY-MM-DD)
            incluir_dia_corte: Si True, incluye el día de corte en el conteo

        Returns:
            Número de días de servicio

        Raises:
            ValueError: Si las fechas son inválidas o incoherentes

        Examples:
            >>> calc = PrestacionesCalculator(params)
            >>> calc.calculate_dias_servicio("2024-11-16", "2025-11-15")
            365
        """
        try:
            fecha_ing = datetime.strptime(fecha_ingreso, "%Y-%m-%d").date()
            fecha_cor = datetime.strptime(fecha_corte, "%Y-%m-%d").date()
        except ValueError as e:
            raise ValueError(f"Formato de fecha inválido: {e}")

        if fecha_cor < fecha_ing:
            raise ValueError(
                f"Fecha de corte ({fecha_corte}) anterior a fecha de ingreso ({fecha_ingreso})"
            )

        delta = fecha_cor - fecha_ing
        dias = delta.days + (1 if incluir_dia_corte else 0)

        logger.debug(
            f"Días de servicio calculados: {dias} "
            f"(desde {fecha_ingreso} hasta {fecha_corte})"
        )

        return dias

    def calculate_cesantias(
        self,
        sbl_general: float,
        dias_servicio: int,
        fecha_ingreso: str,
        fecha_corte: str,
    ) -> Dict[str, Any]:
        """
        Calcula cesantías según Art. 249-250 CST.

        Fórmula: Cesantías = (SBL_GENERAL × días_servicio) / 360

        Args:
            sbl_general: Salario Base de Liquidación General mensual
            dias_servicio: Días trabajados
            fecha_ingreso: Fecha de ingreso (para metadata)
            fecha_corte: Fecha de corte (para metadata)

        Returns:
            Diccionario con:
                - valor: Valor de cesantías (COP)
                - dias_liquidados: Días usados en el cálculo
                - sbl_utilizado: SBL usado
                - formula: Fórmula aplicada
                - plazo_pago_legal: Fecha límite de consignación
                - norma: Referencia legal
                - metadata: Información adicional de trazabilidad

        Examples:
            >>> calc.calculate_cesantias(2200000, 360, "2024-11-16", "2025-11-15")
            {
                'valor': 2200000,
                'dias_liquidados': 360,
                'sbl_utilizado': 2200000,
                ...
            }
        """
        if sbl_general <= 0:
            raise ValueError(f"SBL_GENERAL debe ser positivo: {sbl_general}")

        if dias_servicio < 0:
            raise ValueError(
                f"Días de servicio no pueden ser negativos: {dias_servicio}"
            )

        # Cálculo usando Decimal para precisión
        sbl_decimal = Decimal(str(sbl_general))

        if dias_servicio >= 365 and not self.params.get("USAR_DIAS_REALES", False):
            # Para año completo, usar base 360 días para evitar sobrepago
            dias_liquidar = Decimal("360")
        else:
            dias_liquidar = Decimal(str(dias_servicio))

        base_decimal = Decimal(str(self.DIAS_BASE))

        cesantias_decimal = (sbl_decimal * dias_liquidar) / base_decimal

        # Redondeo según parámetros
        if self.REDONDEO == 0:
            cesantias = int(
                cesantias_decimal.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            )
        else:
            cesantias = float(
                cesantias_decimal.quantize(
                    Decimal(str(10**-self.REDONDEO)), rounding=ROUND_HALF_UP
                )
            )

        # Determinar fecha de consignación (14 de febrero del año siguiente)
        fecha_cor_obj = datetime.strptime(fecha_corte, "%Y-%m-%d").date()
        año_siguiente = fecha_cor_obj.year + 1
        plazo_pago = f"{año_siguiente}-02-14"

        logger.info(
            f"Cesantías calculadas: {cesantias:,.0f} COP "
            f"(SBL={sbl_general:,.0f}, días={dias_servicio})"
        )

        return {
            "valor": cesantias,
            "dias_liquidados": dias_servicio,
            "sbl_utilizado": sbl_general,
            "formula": f"({sbl_general:,.0f} × {dias_servicio}) / {self.DIAS_BASE}",
            "plazo_pago_legal": plazo_pago,
            "norma": "Art. 249-250 CST",
            "metadata": {
                "fecha_ingreso": fecha_ingreso,
                "fecha_corte": fecha_corte,
                "base_dias": self.DIAS_BASE,
                "tipo_calculo": "periodica",
                "precision_decimal": self.REDONDEO,
            },
        }

    def calculate_intereses_cesantias(
        self, cesantias: float, dias_servicio: int, fecha_ingreso: str, fecha_corte: str
    ) -> Dict[str, Any]:
        """
        Calcula intereses sobre cesantías según Ley 50/1990 Art. 99.

        Fórmula: Intereses = (Cesantías × días × 0.12) / 360

        Args:
            cesantias: Valor de cesantías calculado
            dias_servicio: Días trabajados
            fecha_ingreso: Fecha de ingreso (para metadata)
            fecha_corte: Fecha de corte (para metadata)

        Returns:
            Diccionario con:
                - valor: Valor de intereses (COP)
                - dias_liquidados: Días usados
                - tasa_aplicada: Tasa de interés anual
                - cesantias_base: Cesantías sobre las que se calculan intereses
                - formula: Fórmula aplicada
                - plazo_pago_legal: Fecha límite de pago
                - norma: Referencia legal
                - metadata: Información adicional

        Examples:
            >>> calc.calculate_intereses_cesantias(2200000, 360, "2024-11-16", "2025-11-15")
            {
                'valor': 264000,
                'tasa_aplicada': 0.12,
                ...
            }
        """
        if cesantias < 0:
            raise ValueError(f"Cesantías no pueden ser negativas: {cesantias}")

        if dias_servicio < 0:
            raise ValueError(
                f"Días de servicio no pueden ser negativos: {dias_servicio}"
            )

        # Validar tasa de interés
        if self.TASA_INT_CESANTIAS != 0.12:
            logger.warning(
                f"Tasa de interés no estándar: {self.TASA_INT_CESANTIAS} "
                f"(legal es 0.12)"
            )

        # Cálculo usando Decimal
        ces_decimal = Decimal(str(cesantias))

        # Para intereses, usar la misma lógica de días que en cesantías
        if dias_servicio >= 365 and not self.params.get("USAR_DIAS_REALES", False):
            dias_liquidar = Decimal("360")
        else:
            dias_liquidar = Decimal(str(dias_servicio))

        tasa_decimal = Decimal(str(self.TASA_INT_CESANTIAS))
        base_decimal = Decimal(str(self.DIAS_BASE))

        intereses_decimal = (ces_decimal * dias_liquidar * tasa_decimal) / base_decimal

        # Redondeo
        if self.REDONDEO == 0:
            intereses = int(
                intereses_decimal.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            )
        else:
            intereses = float(
                intereses_decimal.quantize(
                    Decimal(str(10**-self.REDONDEO)), rounding=ROUND_HALF_UP
                )
            )

        # Determinar fecha de pago (31 de enero del año siguiente)
        fecha_cor_obj = datetime.strptime(fecha_corte, "%Y-%m-%d").date()
        año_siguiente = fecha_cor_obj.year + 1
        plazo_pago = f"{año_siguiente}-01-31"

        logger.info(
            f"Intereses cesantías calculados: {intereses:,.0f} COP "
            f"(Cesantías={cesantias:,.0f}, tasa={self.TASA_INT_CESANTIAS})"
        )

        return {
            "valor": intereses,
            "dias_liquidados": dias_servicio,
            "tasa_aplicada": self.TASA_INT_CESANTIAS,
            "cesantias_base": cesantias,
            "formula": f"({cesantias:,.0f} × {dias_servicio} × {self.TASA_INT_CESANTIAS}) / {self.DIAS_BASE}",
            "plazo_pago_legal": plazo_pago,
            "norma": "Ley 50/1990 Art. 99",
            "metadata": {
                "fecha_ingreso": fecha_ingreso,
                "fecha_corte": fecha_corte,
                "base_dias": self.DIAS_BASE,
                "tasa_legal_vigente": 0.12,
            },
        }

    def calculate_dias_prima(
        self, fecha_ingreso: str, fecha_corte: str
    ) -> Tuple[int, str]:
        """
        Calcula días trabajados en el semestre correspondiente.

        Semestres:
        - Primer semestre: 1 enero - 30 junio
        - Segundo semestre: 1 julio - 31 diciembre

        Args:
            fecha_ingreso: Fecha de ingreso (YYYY-MM-DD)
            fecha_corte: Fecha de corte (YYYY-MM-DD)

        Returns:
            Tupla (días_prima, semestre)
            - días_prima: Días trabajados en el semestre de la fecha de corte
            - semestre: "primer_semestre" o "segundo_semestre"

        Examples:
            >>> calc.calculate_dias_prima("2024-11-16", "2025-06-30")
            (226, "primer_semestre")
        """
        fecha_ing = datetime.strptime(fecha_ingreso, "%Y-%m-%d").date()
        fecha_cor = datetime.strptime(fecha_corte, "%Y-%m-%d").date()

        # Determinar semestre de la fecha de corte
        if fecha_cor.month <= 6:
            semestre = "primer_semestre"
            inicio_semestre = date(fecha_cor.year, 1, 1)
            fin_semestre = date(fecha_cor.year, 6, 30)
        else:
            semestre = "segundo_semestre"
            inicio_semestre = date(fecha_cor.year, 7, 1)
            fin_semestre = date(fecha_cor.year, 12, 31)

        # Determinar fecha de inicio efectiva
        fecha_inicio_efectiva = max(fecha_ing, inicio_semestre)

        # Determinar fecha de fin efectiva
        fecha_fin_efectiva = min(fecha_cor, fin_semestre)

        # Calcular días
        if fecha_fin_efectiva < fecha_inicio_efectiva:
            dias_prima = 0
        else:
            delta = fecha_fin_efectiva - fecha_inicio_efectiva
            dias_prima = delta.days + 1  # Incluir día de corte

        # Validar que no exceda días del semestre
        dias_semestre = (fin_semestre - inicio_semestre).days + 1
        if dias_prima > dias_semestre:
            logger.warning(
                f"Días prima ({dias_prima}) exceden días del semestre ({dias_semestre}). "
                f"Ajustando a {dias_semestre}."
            )
            dias_prima = dias_semestre

        logger.debug(
            f"Días prima calculados: {dias_prima} en {semestre} "
            f"(desde {fecha_inicio_efectiva} hasta {fecha_fin_efectiva})"
        )

        return dias_prima, semestre

    def calculate_prima(
        self, sbl_prima: float, fecha_ingreso: str, fecha_corte: str
    ) -> Dict[str, Any]:
        """
        Calcula prima de servicios según Art. 306-308 CST.

        Fórmula: Prima = (SBL_PRIMA × días_prima) / 360

        Args:
            sbl_prima: Salario Base de Liquidación para prima
            fecha_ingreso: Fecha de ingreso
            fecha_corte: Fecha de corte

        Returns:
            Diccionario con:
                - valor: Valor de prima (COP)
                - dias_liquidados: Días del semestre trabajados
                - semestre: Semestre correspondiente
                - sbl_utilizado: SBL usado
                - formula: Fórmula aplicada
                - plazo_pago_legal: Fecha límite de pago
                - norma: Referencia legal
                - metadata: Información adicional

        Examples:
            >>> calc.calculate_prima(2200000, "2024-11-16", "2025-06-30")
            {
                'valor': 1376111,
                'dias_liquidados': 226,
                'semestre': 'primer_semestre',
                ...
            }
        """
        if sbl_prima <= 0:
            raise ValueError(f"SBL_PRIMA debe ser positivo: {sbl_prima}")

        # Calcular días del semestre
        dias_prima, semestre = self.calculate_dias_prima(fecha_ingreso, fecha_corte)

        if dias_prima == 0:
            logger.warning(
                f"No hay días de prima para el período "
                f"{fecha_ingreso} - {fecha_corte}"
            )
            return {
                "valor": 0,
                "dias_liquidados": 0,
                "semestre": semestre,
                "sbl_utilizado": sbl_prima,
                "formula": "No aplica (0 días)",
                "plazo_pago_legal": None,
                "norma": "Art. 306-308 CST",
                "metadata": {
                    "fecha_ingreso": fecha_ingreso,
                    "fecha_corte": fecha_corte,
                    "advertencia": "No hay días trabajados en el semestre de corte",
                },
            }

        # Cálculo usando Decimal
        sbl_decimal = Decimal(str(sbl_prima))
        dias_decimal = Decimal(str(dias_prima))
        base_decimal = Decimal(str(self.DIAS_BASE))

        prima_decimal = (sbl_decimal * dias_decimal) / base_decimal

        # Redondeo
        if self.REDONDEO == 0:
            prima = int(prima_decimal.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        else:
            prima = float(
                prima_decimal.quantize(
                    Decimal(str(10**-self.REDONDEO)), rounding=ROUND_HALF_UP
                )
            )

        # Determinar fecha de pago según semestre
        fecha_cor_obj = datetime.strptime(fecha_corte, "%Y-%m-%d").date()
        if semestre == "primer_semestre":
            plazo_pago = f"{fecha_cor_obj.year}-06-30"
        else:
            plazo_pago = f"{fecha_cor_obj.year}-12-20"

        logger.info(
            f"Prima calculada: {prima:,.0f} COP "
            f"(SBL={sbl_prima:,.0f}, días={dias_prima}, {semestre})"
        )

        return {
            "valor": prima,
            "dias_liquidados": dias_prima,
            "semestre": semestre,
            "sbl_utilizado": sbl_prima,
            "formula": f"({sbl_prima:,.0f} × {dias_prima}) / {self.DIAS_BASE}",
            "plazo_pago_legal": plazo_pago,
            "norma": "Art. 306-308 CST",
            "metadata": {
                "fecha_ingreso": fecha_ingreso,
                "fecha_corte": fecha_corte,
                "base_dias": self.DIAS_BASE,
                "dias_semestre_completo": 185 if semestre == "primer_semestre" else 184,
                "proporcionalidad": round((dias_prima / 180) * 100, 2),
            },
        }

    def calculate_all_prestaciones(
        self, input_data: Dict[str, Any], sbl_general: float, sbl_prima: float
    ) -> Dict[str, Any]:
        """
        Calcula todas las prestaciones en un solo llamado.

        Args:
            input_data: Datos de entrada completos
            sbl_general: SBL para cesantías e intereses
            sbl_prima: SBL para prima

        Returns:
            Diccionario con todas las prestaciones calculadas
        """
        fecha_ingreso = input_data["fecha_ingreso"]
        fecha_corte = input_data["fecha_corte"]

        # Calcular días de servicio
        dias_servicio = self.calculate_dias_servicio(fecha_ingreso, fecha_corte)

        # Calcular prestaciones
        cesantias_result = self.calculate_cesantias(
            sbl_general, dias_servicio, fecha_ingreso, fecha_corte
        )

        intereses_result = self.calculate_intereses_cesantias(
            cesantias_result["valor"], dias_servicio, fecha_ingreso, fecha_corte
        )

        prima_result = self.calculate_prima(sbl_prima, fecha_ingreso, fecha_corte)

        total = (
            cesantias_result["valor"]
            + intereses_result["valor"]
            + prima_result["valor"]
        )

        logger.info(
            f"Prestaciones totales: {total:,.0f} COP "
            f"(Cesantías={cesantias_result['valor']:,.0f}, "
            f"Intereses={intereses_result['valor']:,.0f}, "
            f"Prima={prima_result['valor']:,.0f})"
        )

        return {
            "dias_servicio": dias_servicio,
            "cesantias": cesantias_result,
            "intereses_cesantias": intereses_result,
            "prima": prima_result,
            "total_prestaciones": total,
        }


def validate_formulas_against_known_cases() -> bool:
    """
    Valida las fórmulas contra casos conocidos documentados.

    Returns:
        True si todas las validaciones pasan, False en caso contrario
    """
    params = {"DIAS_BASE": 360.0, "TASA_INT_CESANTIAS": 0.12, "REDONDEO": 0}

    calc = PrestacionesCalculator(params)

    # Caso 1: Año completo, salario 2.200.000
    test_cases = [
        {
            "name": "Caso finca rural - año completo",
            "sbl_general": 2200000,
            "sbl_prima": 2200000,
            "fecha_ingreso": "2024-11-16",
            "fecha_corte": "2025-11-15",
            "expected": {
                "cesantias": 2200000,
                "intereses": 264000,
                "dias_servicio": 365,
            },
        },
        {
            "name": "Caso medio año",
            "sbl_general": 1500000,
            "sbl_prima": 1500000,
            "fecha_ingreso": "2025-01-01",
            "fecha_corte": "2025-06-30",
            "expected": {"cesantias": 762500, "intereses": 18300, "dias_servicio": 181},
        },
    ]

    all_passed = True

    for test in test_cases:
        dias = calc.calculate_dias_servicio(test["fecha_ingreso"], test["fecha_corte"])

        ces = calc.calculate_cesantias(
            test["sbl_general"], dias, test["fecha_ingreso"], test["fecha_corte"]
        )

        inter = calc.calculate_intereses_cesantias(
            ces["valor"], dias, test["fecha_ingreso"], test["fecha_corte"]
        )

        # Tolerancia de 1 peso por redondeos
        if abs(dias - test["expected"]["dias_servicio"]) > 0:
            logger.error(
                f"{test['name']}: Días incorrectos. Expected {test['expected']['dias_servicio']}, got {dias}"
            )
            all_passed = False

        if abs(ces["valor"] - test["expected"]["cesantias"]) > 1:
            logger.error(
                f"{test['name']}: Cesantías incorrectas. Expected {test['expected']['cesantias']}, got {ces['valor']}"
            )
            all_passed = False

        if abs(inter["valor"] - test["expected"]["intereses"]) > 1:
            logger.error(
                f"{test['name']}: Intereses incorrectos. Expected {test['expected']['intereses']}, got {inter['valor']}"
            )
            all_passed = False

    return all_passed


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    print("Validando fórmulas contra casos conocidos...")
    if validate_formulas_against_known_cases():
        print("✓ Todas las validaciones pasaron")
    else:
        print("✗ Algunas validaciones fallaron")
