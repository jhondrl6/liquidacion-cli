# liquidator/calculators/vacaciones_calculator.py
"""
Módulo para el cálculo de vacaciones según la normativa colombiana.
Este módulo implementa las reglas para calcular días de vacaciones causados,
su valor monetario y determinar si aplica compensación en dinero.
"""

from datetime import datetime
from typing import Dict, Any
from ..utils.date_utils import calculate_days_between, calculate_years_of_service
from ..utils.currency_utils import round_currency
from ..utils.constants import DEFAULT_DIAS_BASE_VACACIONES
from ..legal.topes_manager import TopesManager


class VacacionesCalculator:
    """
    Calculador de vacaciones según normativa colombiana.
    Responsabilidades:
    - Calcular días de vacaciones causadas
    - Calcular valor monetario de vacaciones (base 720)
    - Determinar si aplica compensación en dinero (solo finiquito)
    - Validar reglas específicas para cada modo de liquidación
    """

    VACACIONES_DENOM = DEFAULT_DIAS_BASE_VACACIONES

    def __init__(self, params: Dict[str, Any]):
        """
        Inicializa el calculador con los parámetros legales vigentes.

        Args:
            params: Diccionario con parámetros legales (SMMLV, topes, etc.)
        """
        self.params = params
        self.topes_manager = TopesManager(params)

    def calculate_dias_vacaciones_causadas(
        self, fecha_ingreso: str, fecha_corte: str
    ) -> int:
        """
        Calcula los días de vacaciones causados según tiempo de servicio.

        Según el Artículo 186 del CST, el trabajador tiene derecho a 15 días
        hábiles de vacaciones remuneradas por cada año de servicio.

        Args:
            fecha_ingreso: Fecha de ingreso del trabajador (YYYY-MM-DD)
            fecha_corte: Fecha de corte para el cálculo (YYYY-MM-DD)

        Returns:
            int: Días de vacaciones causados (máximo 15 por año)
        """
        try:
            dias_servicio = calculate_days_between(fecha_ingreso, fecha_corte)
            years_service = calculate_years_of_service(fecha_ingreso, fecha_corte)

            # Cálculo proporcional: 15 días por año completo
            dias_vacaciones = int(years_service * 15)

            # Límite máximo: año completo = 15 días máximo
            # Para períodos parciales, el cálculo proporcional ya es correcto
            if years_service >= 1:
                max_dias = int(years_service) * 15
                dias_vacaciones = min(dias_vacaciones, max_dias)
            # Para años < 1, mantener el cálculo proporcional

            return dias_vacaciones

        except Exception as e:
            raise ValueError(f"Error calculando días de vacaciones: {str(e)}")

    def calculate_valor_vacaciones(
        self, sbl_vacaciones: float, dias_vacaciones: int
    ) -> float:
        """
        Calcula el valor monetario de las vacaciones con base 720 días.
        
        NOTA: Este método calcula vacaciones PROPORCIONALES desde días de servicio.
        Para compensación directa de días ya determinados, usar calculate_compensacion_dias_directos().

        Fórmula: (SBL_VACACIONES × días) / 720

        Args:
            sbl_vacaciones: Salario Base de Liquidación para vacaciones
            dias_vacaciones: Días de vacaciones causados (proporcionales al servicio)

        Returns:
            float: Valor monetario de las vacaciones, redondeado a pesos
        """
        if sbl_vacaciones <= 0:
            raise ValueError("SBL_VACACIONES debe ser mayor a cero")

        if dias_vacaciones < 0:
            raise ValueError("Días de vacaciones no pueden ser negativos")

        if dias_vacaciones == 0:
            return 0.0

        # Fórmula legal Art. 186-192 CST: (SBL_Vacaciones × Días) / 720
        # Justificación: 360 días de trabajo = 15 días de vacaciones (15/360 = 1/24)
        # Equivalente a aplicar el factor 1/24 multiplicando por días y dividiendo por 720
        # Esta fórmula es válida para calcular el valor de días proporcionales, NO para
        # compensación directa de días ya determinados.
        valor_vacaciones = (sbl_vacaciones * dias_vacaciones) / self.VACACIONES_DENOM
        return round_currency(valor_vacaciones, self.params.get("REDONDEO", 0))

    def calculate_compensacion_dias_directos(
        self, sbl_vacaciones: float, dias_a_compensar: float
    ) -> float:
        """
        Calcula el valor monetario de compensación de días de vacaciones ya determinados.
        
        Se utiliza cuando se compensan en dinero días específicos de vacaciones acumuladas
        (ej: 7.5 días solicitados) mediante acuerdo mutuo (Art. 189 CST).

        Fórmula: (SBL_VACACIONES / 30) × días_a_compensar

        Args:
            sbl_vacaciones: Salario Base de Liquidación para vacaciones
            dias_a_compensar: Días específicos a compensar en dinero

        Returns:
            float: Valor monetario de la compensación, redondeado a pesos
            
        Ejemplo: 
            SBL = 1,500,000, días = 7.5
            (1,500,000 / 30) × 7.5 = 50,000 × 7.5 = 375,000
        """
        if sbl_vacaciones <= 0:
            raise ValueError("SBL_VACACIONES debe ser mayor a cero")

        if dias_a_compensar <= 0:
            raise ValueError("Días a compensar deben ser mayor a cero")

        # Fórmula: Valor diario de salario × días a compensar
        # Valor diario = SBL / 30 (mes = 30 días por ley colombiana)
        valor_diario = sbl_vacaciones / 30
        valor_compensacion = valor_diario * dias_a_compensar
        return round_currency(valor_compensacion, self.params.get("REDONDEO", 0))

    def determinar_compensacion_dinero(
        self, modo: str, dias_vacaciones_pendientes: int = 0, dias_compensar_acuerdo: float = 0
    ) -> Dict[str, Any]:
        """
        Determina si aplica compensación en dinero por vacaciones.

        Reglas:
        - Modo FINIQUITO: Se compensan las vacaciones pendientes acumuladas.
        - Modo PERIÓDICA: Solo aplica si hay acuerdo mutuo (Art. 189 CST) y
          no excede el 50% de las vacaciones pendientes.

        Args:
            modo: "PERIODICA" o "FINIQUITO"
            dias_vacaciones_pendientes: Días de vacaciones pendientes totales
            dias_compensar_acuerdo: Días solicitados para compensar en dinero (Periodica)

        Returns:
            Dict[str, Any]: Resultado con información sobre compensación
        """
        resultado = {
            "aplica_compensacion": False,
            "dias_compensados": 0,
            "motivo": "",
            "norma_aplicada": "",
        }

        if modo.upper() == "PERIODICA":
            if dias_compensar_acuerdo > 0:
                # Validación: Máximo 50% de lo pendiente/causado
                if dias_vacaciones_pendientes <= 0:
                     # Si no hay pendientes, no se puede compensar
                     resultado["motivo"] = "No hay vacaciones pendientes para compensar"
                     return resultado
                
                # El límite legal es hasta la mitad de las vacaciones causadas.
                # Asumimos que dias_vacaciones_pendientes refleja el saldo disponible.
                limite = dias_vacaciones_pendientes / 2
                if dias_compensar_acuerdo > limite:
                    # Ajustamos al límite o lanzamos error? 
                    # Por seguridad, no compensamos más de lo legal pero permitimos el proceso
                    # advirtiendo (o ajustando). Aquí ajustamos al límite legal.
                    # Pero para ser estrictos con la solicitud, mejor lanzamos error si se excede
                    # o retornamos solo lo permitido. Vamos a retornar lo permitido.
                    dias_compensar_acuerdo = limite
                
                resultado["aplica_compensacion"] = True
                resultado["dias_compensados"] = dias_compensar_acuerdo
                resultado["motivo"] = f"Compensación parcial por acuerdo mutuo (Art. 189 CST). Solicitado: {dias_compensar_acuerdo}"
                resultado["norma_aplicada"] = "Art. 189 CST (Acuerdo Mutuo)"
                return resultado

            resultado["aplica_compensacion"] = False
            resultado["motivo"] = "No aplica en modo PERIÓDICA sin acuerdo de compensación"
            resultado["norma_aplicada"] = "Arts.186-192 CST"
            return resultado

        if modo.upper() == "FINIQUITO":
            if dias_vacaciones_pendientes <= 0:
                resultado["aplica_compensacion"] = False
                resultado["motivo"] = (
                    "No hay días de vacaciones pendientes para compensar"
                )
                resultado["norma_aplicada"] = "Arts.186-192 CST"
                return resultado

            resultado["aplica_compensacion"] = True
            resultado["dias_compensados"] = dias_vacaciones_pendientes
            resultado["motivo"] = (
                f"Compensación por {dias_vacaciones_pendientes} días de vacaciones pendientes en finiquito"
            )
            resultado["norma_aplicada"] = "Arts.186-192 CST"
            return resultado

        raise ValueError(f"Modo no válido: {modo}. Debe ser 'PERIODICA' o 'FINIQUITO'")

    def calculate_vacaciones_completas(
        self, input_data: Dict[str, Any], sbl_vacaciones: float
    ) -> Dict[str, Any]:
        """
        Calcula el resultado completo de vacaciones para la liquidación.

        Args:
            input_data: Datos de entrada del trabajador
            sbl_vacaciones: Salario Base de Liquidación para vacaciones

        Returns:
            Dict[str, Any]: Resultado completo con días, valor y metadatos
        """
        modo = input_data.get("modo", "PERIODICA")
        fecha_ingreso = input_data.get("fecha_ingreso")
        fecha_corte = input_data.get("fecha_corte")
        dias_vacaciones_pendientes = input_data.get("dias_vacaciones_pendientes", 0)
        dias_compensar_acuerdo = input_data.get("dias_vacaciones_para_compensar_dinero", 0)

        resultado = {
            "valor": 0.0,
            "dias_liquidados": 0,
            "dias_causados": 0,
            "dias_pendientes": dias_vacaciones_pendientes,
            "aplica_compensacion": False,
            "norma": "Arts.186-192 CST",
            "nota": "",
        }

        # Calcular días causados
        dias_causados = self.calculate_dias_vacaciones_causadas(
            fecha_ingreso, fecha_corte
        )
        resultado["dias_causados"] = dias_causados

        # Determinar si aplica compensación
        comp_result = self.determinar_compensacion_dinero(
            modo, dias_vacaciones_pendientes, dias_compensar_acuerdo
        )
        resultado["aplica_compensacion"] = comp_result["aplica_compensacion"]

        if comp_result["aplica_compensacion"]:
            dias_a_pagar = comp_result["dias_compensados"]
            # Usar la fórmula de compensación directa: (SBL / 30) × días
            # NO la fórmula de proporcional: (SBL × días) / 720
            valor = self.calculate_compensacion_dias_directos(
                sbl_vacaciones, dias_a_pagar
            )
            resultado["valor"] = valor
            resultado["dias_liquidados"] = dias_a_pagar
            resultado["nota"] = comp_result["motivo"]
            resultado["norma"] = comp_result["norma_aplicada"]
            
            # Si es periódica, actualizar el saldo de pendientes en el objeto resultado (informativo)
            if modo.upper() == "PERIODICA":
                 resultado["dias_pendientes"] = dias_vacaciones_pendientes - dias_a_pagar
        else:
            if modo.upper() == "PERIODICA":
                resultado["nota"] = "No aplica compensación en dinero en esta liquidación periódica"

        return resultado
