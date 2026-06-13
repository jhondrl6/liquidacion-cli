"""
Markdown Generator Module
Generates readable Markdown documents using templates
"""

from typing import Dict, Any
import datetime

from .template_manager import TemplateManager


class MarkdownGenerator:
    """Generates readable Markdown documents using templates"""

    def __init__(self, templates_dir: str = "templates"):
        """
        Initialize the Markdown generator

        Args:
            templates_dir: Directory containing template files
        """
        self.template_manager = TemplateManager(templates_dir)

    def generate_markdown(self, json_data: Dict[str, Any]) -> str:
        """
        Generate Markdown document from JSON data

        Args:
            json_data: Structured JSON data from JSONGenerator

        Returns:
            Rendered Markdown document
        """
        modo = json_data["meta"]["modo"]

        # Prepare context for template
        context = {
            "año": json_data["meta"]["fecha_corte"][:4],
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "modo": modo,
            "fecha_ingreso": json_data["meta"]["fecha_ingreso"],
            "fecha_corte": json_data["meta"]["fecha_corte"],
            "nombre": json_data["trabajador"]["nombre"],
            "documento": json_data["trabajador"]["documento"],
            "tipo_contrato": json_data["trabajador"]["tipo_contrato"],
            "reside_en_lugar": json_data["trabajador"]["reside_en_lugar_trabajo"],
            "cesantias": json_data["desglose"]["cesantias"]["valor"],
            "dias_ces": json_data["desglose"]["cesantias"]["dias_liquidados"],
            "plazo_ces": json_data["desglose"]["cesantias"]["plazo_pago_legal"],
            "norma_ces": json_data["desglose"]["cesantias"]["norma"],
            "intereses": json_data["desglose"]["intereses_cesantias"]["valor"],
            "dias_int": json_data["desglose"]["intereses_cesantias"]["dias_liquidados"],
            "plazo_int": json_data["desglose"]["intereses_cesantias"][
                "plazo_pago_legal"
            ],
            "norma_int": json_data["desglose"]["intereses_cesantias"]["norma"],
            "prima": json_data["desglose"]["prima"]["valor"],
            "dias_prima": json_data["desglose"]["prima"]["dias_liquidados"],
            "plazo_prima": json_data["desglose"]["prima"]["plazo_pago_legal"],
            "norma_prima": json_data["desglose"]["prima"]["norma"],
            "vacaciones": json_data["desglose"]["vacaciones"]["valor"],
            "dias_vac": json_data["desglose"]["vacaciones"]["dias_liquidados"],
            "norma_vac": json_data["desglose"]["vacaciones"]["norma"],
            "total": json_data.get("total_liquidacion", 0),
            "observaciones": self._format_observaciones(
                json_data["validaciones_y_alertas"]
            ),
            "plazos_detallados": self._format_plazos(json_data),
            "declaracion": self._get_declaracion(modo),
        }

        # Add indemnization and salary pending if in FINIQUITO mode
        if modo == "FINIQUITO":
            context.update(
                {
                    "indemnizacion": json_data["desglose"]["indemnizacion"]["valor"],
                    "dias_indem": json_data["desglose"]["indemnizacion"][
                        "dias_liquidados"
                    ],
                    "norma_indem": json_data["desglose"]["indemnizacion"]["norma"],
                    "salario_pendiente": json_data["desglose"]["salario_pendiente"][
                        "valor"
                    ],
                    "dias_salario_pend": json_data["desglose"]["salario_pendiente"][
                        "dias_liquidados"
                    ],
                    "norma_salario": json_data["desglose"]["salario_pendiente"][
                        "norma"
                    ],
                }
            )

        # Select appropriate template
        template_name = "finiquito" if modo == "FINIQUITO" else "periodica"

        # Render template
        return self.template_manager.render_template(template_name, context)

    def save_markdown(self, markdown_content: str, file_path: str):
        """
        Save Markdown content to file

        Args:
            markdown_content: Markdown content to save
            file_path: Path to save the file
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            return True
        except Exception as e:
            print(f"Error saving Markdown: {e}")
            return False

    def _format_observaciones(self, validaciones: Dict[str, str]) -> str:
        """
        Format validations and alerts as a Markdown list

        Args:
            validaciones: Dictionary of validations and alerts

        Returns:
            Formatted Markdown list
        """
        if not validaciones:
            return "Ninguna observación."

        items = []
        for key, value in validaciones.items():
            items.append(f"- {value}")

        return "\n".join(items)

    def _format_plazos(self, json_data: Dict[str, Any]) -> str:
        """
        Format payment deadlines as a Markdown table

        Args:
            json_data: Structured JSON data

        Returns:
            Formatted Markdown table
        """
        items = []

        # Cesantías
        items.append(
            f"- Cesantías: {json_data['desglose']['cesantias']['plazo_pago_legal']} "
            f"({json_data['desglose']['cesantias']['norma']})"
        )

        # Intereses
        items.append(
            f"- Intereses sobre cesantías: {json_data['desglose']['intereses_cesantias']['plazo_pago_legal']} "
            f"({json_data['desglose']['intereses_cesantias']['norma']})"
        )

        # Prima
        items.append(
            f"- Prima de servicios: {json_data['desglose']['prima']['plazo_pago_legal']} "
            f"({json_data['desglose']['prima']['norma']})"
        )

        # Add indemnization and salary pending if in FINIQUITO mode
        if json_data["meta"]["modo"] == "FINIQUITO":
            items.append(
                f"- Indemnización: Pago inmediato ({json_data['desglose']['indemnizacion']['norma']})"
            )
            items.append(
                f"- Salario pendiente: Pago inmediato ({json_data['desglose']['salario_pendiente']['norma']})"
            )

        return "\n".join(items)

    def _get_declaracion(self, modo: str) -> str:
        """
        Get legal declaration based on mode

        Args:
            modo: Calculation mode (PERIÓDICA or FINIQUITO)

        Returns:
            Legal declaration text
        """
        if modo == "PERIÓDICA":
            return (
                "El empleador declara que los valores aquí liquidados corresponden a las "
                "prestaciones sociales causadas en el período indicado, conforme a la "
                "normatividad laboral colombiana. Las cesantías serán consignadas en el "
                "fondo de pensiones seleccionado por el trabajador dentro de los plazos "
                "legales establecidos."
            )
        else:
            return (
                "El empleador declara que los valores aquí liquidados corresponden a la "
                "totalidad de las prestaciones sociales e indemnizaciones causadas por "
                "terminación del contrato, conforme a la normatividad laboral colombiana. "
                "El trabajador declara haber recibido el pago total de los conceptos "
                "liquidados en este documento."
            )
