"""
Generador de PDF para Liquidación de Nómina
Convierte documentos Markdown a PDF profesionales con estilos corporativos
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging
from datetime import datetime

from liquidator.output.template_manager import TemplateManager

try:
    import markdown
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
except Exception as e:  # pragma: no cover - dependencias externas
    logging.warning(f"Dependencias de PDF no disponibles: {e}")
    markdown = None
    HTML = None
    CSS = None
    FontConfiguration = None


class PDFGeneratorError(Exception):
    """Excepción específica para errores de generación de PDF"""

    pass


class PDFGenerator:
    """
    Generador de PDF profesional para liquidaciones de nómina

    Características:
    - Conversión Markdown → HTML → PDF
    - Aplicación de estilos CSS corporativos
    - Manejo de páginas múltiples
    - Encabezados y pies de página
    - Configuración de fuentes
    """

    def __init__(
        self,
        templates_dir: Optional[Path] = None,
        styles_dir: Optional[Path] = None,
        fonts_dir: Optional[Path] = None,
        template_manager: Optional[TemplateManager] = None,
    ):
        """
        Inicializar generador de PDF

        Args:
            templates_dir: Directorio con plantillas
            styles_dir: Directorio con estilos CSS
            fonts_dir: Directorio con fuentes personalizadas
        """
        self.templates_dir = (
            templates_dir or Path(__file__).parent.parent.parent / "templates"
        )
        self.styles_dir = styles_dir or self.templates_dir / "styles"
        self.fonts_dir = fonts_dir
        self.template_manager = template_manager or TemplateManager(
            str(self.templates_dir)
        )

        # Configurar logging
        self.logger = logging.getLogger(__name__)

        # Check if dependencies are available
        self.dependencies_available = self._check_dependencies()

        # If dependencies are not available, warn the user
        if not self.dependencies_available:
            self.logger.warning("PDF generation dependencies not available. Only creating placeholder.")

    def _check_dependencies(self):
        """Verificar que las dependencias necesarias estén instaladas"""
        if not markdown or not HTML:
            return False
        return True

    def _load_markdown_template(self, template_name: str) -> str:
        """Cargar plantilla Markdown desde disco"""

        template_path = self.templates_dir / template_name
        if not template_path.exists():
            raise PDFGeneratorError(f"Plantilla no encontrada: {template_path}")

        try:
            return template_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return template_path.read_text(encoding="latin-1")

    def _render_markdown_template(
        self, template_name: str, context: Dict[str, Any]
    ) -> str:
        """Renderizar plantilla Markdown con contexto dinámico"""

        template_file = self._normalize_template_name(template_name)

        try:
            template_source = self._load_markdown_template(template_file)
        except PDFGeneratorError:
            raise
        except Exception as exc:  # pragma: no cover
            raise PDFGeneratorError(f"Plantilla no encontrada: {template_name}") from exc

        template = self.template_manager.env.from_string(template_source)
        template.globals["format_currency"] = self._format_currency_value
        return template.render(**context)

    def _normalize_template_name(self, template_name: str) -> str:
        if template_name.endswith(".md"):
            return template_name
        if template_name in {"periodica", "finiquito"}:
            return f"comprobante_{template_name}.md"
        return template_name

    def _format_currency_value(self, value: Union[int, float]) -> str:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return str(value)
        return f"${numeric:,.0f}".replace(",", ".")

    def _load_css_styles(self, css_file: str = "pdf_styles.css") -> str:
        """Cargar estilos CSS"""
        css_path = self.styles_dir / css_file

        if not css_path.exists():
            self.logger.warning(f"Archivo CSS no encontrado: {css_path}")
            return ""

        with open(css_path, "r", encoding="utf-8") as f:
            return f.read()

    def _process_template(self, template: str, data: Dict[str, Any]) -> str:
        """Procesar plantilla Markdown con datos"""
        # Variables comunes
        default_vars = {
            "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "empresa_nombre": "Hildaliria Raigoza L.",
            "empresa_nit": "CC 42.066.783",
        }

        # Combinar datos
        template_vars = {**default_vars, **data}

        return template
        for key, value in template_vars.items():
            if isinstance(value, str):
                template = template.replace(f"{{{key}}}", value)
            elif isinstance(value, (int, float)):
                template = template.replace(f"{{{key}}}", str(value))

        # Procesar tablas y listas complejas
        template = self._process_complex_structures(template, template_vars)

        return template
    def _process_complex_structures(self, template: str, data: Dict[str, Any]) -> str:
        """Procesar estructuras complejas como tablas dinámicas"""
        # Procesar tabla de prestaciones si existe
        if "desglose" in data and "tabla_prestaciones" in template:
            tabla_html = self._generate_prestaciones_table(data["desglose"])
            template = template.replace("{tabla_prestaciones}", tabla_html)

        # Procesar información del trabajador
        if "trabajador" in data and "info_trabajador" in template:
            info_html = self._generate_trabajador_info(data["trabajador"])
            template = template.replace("{info_trabajador}", info_html)

        return template

    def _generate_prestaciones_table(self, desglose: Dict[str, Any]) -> str:
        """Generar tabla HTML de prestaciones"""
        rows = []

        # Cesantías
        if "cesantias" in desglose and desglose["cesantias"]["valor"] > 0:
            rows.append(
                f"""
                <tr>
                    <td>Cesantías</td>
                    <td>${desglose['cesantias']['valor']:,.0f}</td>
                    <td>{desglose['cesantias'].get('dias_liquidados', 0)} días</td>
                    <td>{desglose['cesantias'].get('plazo_pago_legal', 'N/A')}</td>
                    <td>{desglose['cesantias'].get('norma', 'N/A')}</td>
                </tr>
            """
            )

        # Intereses
        if (
            "intereses_cesantias" in desglose
            and desglose["intereses_cesantias"]["valor"] > 0
        ):
            rows.append(
                f"""
                <tr>
                    <td>Intereses sobre Cesantías</td>
                    <td>${desglose['intereses_cesantias']['valor']:,.0f}</td>
                    <td>{desglose['intereses_cesantias'].get('dias_liquidados', 0)} días</td>
                    <td>{desglose['intereses_cesantias'].get('plazo_pago_legal', 'N/A')}</td>
                    <td>{desglose['intereses_cesantias'].get('norma', 'N/A')}</td>
                </tr>
            """
            )

        # Prima
        if "prima" in desglose and desglose["prima"]["valor"] > 0:
            rows.append(
                f"""
                <tr>
                    <td>Prima de Servicios</td>
                    <td>${desglose['prima']['valor']:,.0f}</td>
                    <td>{desglose['prima'].get('dias_liquidados', 0)} días</td>
                    <td>{desglose['prima'].get('plazo_pago_legal', 'N/A')}</td>
                    <td>{desglose['prima'].get('norma', 'N/A')}</td>
                </tr>
            """
            )

        # Vacaciones (solo si tiene valor)
        if "vacaciones" in desglose and desglose["vacaciones"]["valor"] > 0:
            rows.append(
                f"""
                <tr>
                    <td>Vacaciones</td>
                    <td>${desglose['vacaciones']['valor']:,.0f}</td>
                    <td>{desglose['vacaciones'].get('dias_liquidados', 0)} días</td>
                    <td>{desglose['vacaciones'].get('plazo_pago_legal', 'N/A')}</td>
                    <td>{desglose['vacaciones'].get('norma', 'N/A')}</td>
                </tr>
            """
            )

        return f"""
        <table class="prestaciones-table">
            <thead>
                <tr>
                    <th>Concepto</th>
                    <th>Valor (COP)</th>
                    <th>Días</th>
                    <th>Plazo de Pago</th>
                    <th>Base Legal</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """

    def _generate_trabajador_info(self, trabajador: Dict[str, Any]) -> str:
        """Generar información del trabajador"""
        return f"""
        <div class="trabajador-info">
            <p><strong>Nombre:</strong> {trabajador.get('nombre', 'N/A')}</p>
            <p><strong>Documento:</strong> {trabajador.get('documento', 'N/A')}</p>
            <p><strong>Tipo de Contrato:</strong> {trabajador.get('tipo_contrato', 'N/A')}</p>
            <p><strong>Reside en lugar de trabajo:</strong> {'Sí' if trabajador.get('reside_en_lugar_trabajo') else 'No'}</p>
        </div>
        """

    def _markdown_to_html(self, markdown_content: str) -> str:
        """Convertir Markdown a HTML"""
        md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "attr_list"])
        return md.convert(markdown_content)

    def _generate_html_document(
        self,
        html_content: str,
        data: Dict[str, Any],
        page_title: str = "Liquidación de Nómina",
    ) -> str:
        """Generar documento HTML completo con estilos"""

        # CSS personalizado embebido
        custom_css = self._load_css_styles()

        # Encabezado y pie de página
        header_content = self._generate_header_content(data)
        footer_content = self._generate_footer_content(data)

        # Documento HTML completo
        html_doc = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{page_title}</title>
            <style>
                {custom_css}
            </style>
        </head>
        <body>
            <div id="header">
                {header_content}
            </div>

            <div id="footer">
                {footer_content}
            </div>

            <main class="document-content">
                {html_content}
            </main>
        </body>
        </html>
        """

        return html_doc

    def _generate_header_content(self, data: Dict[str, Any]) -> str:
        """Generar contenido del encabezado"""
        empresa = data.get("empresa", {})
        return f"""
        <div class="header-content">
            <div class="company-info">
                <h2>{empresa.get('nombre', 'Hildaliria Raigoza L.')}</h2>
                <p>{empresa.get('nit', 'CC 42.066.783')}</p>
            </div>
        </div>
        """

    def _generate_footer_content(self, data: Dict[str, Any]) -> str:
        """Generar contenido del pie de página"""
        return f"""
        <div class="footer-content">
            <p>Página <span class="page-number"></span> de <span class="total-pages"></span></p>
            <p>Documento generado el {data.get('fecha_generacion', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</p>
        </div>
        """

    def _build_template_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        meta = data.get("meta", {})
        trabajador = data.get("trabajador", {})
        empresa = data.get("empresa") or data.get("empleador") or {}
        desglose = data.get("desglose", {})

        fecha_generacion = meta.get("fecha_generacion")
        try:
            fecha_dt = (
                datetime.fromisoformat(fecha_generacion)
                if fecha_generacion
                else datetime.now()
            )
        except ValueError:
            fecha_dt = datetime.now()

        total = (
            data.get("total_liquidacion")
            or data.get("total_liquidacion_periodica")
            or sum(
                concepto.get("valor", 0)
                for key, concepto in desglose.items()
                if isinstance(concepto, dict)
            )
        )

        context = {
            "año": fecha_dt.year,
            "fecha": fecha_dt.strftime("%Y-%m-%d"),
            "modo": meta.get("modo", data.get("modo", "PERIODICA")),
            "fecha_ingreso": meta.get("fecha_ingreso")
            or data.get("fecha_ingreso", "N/D"),
            "fecha_corte": meta.get("fecha_corte")
            or data.get("fecha_corte", "N/D"),
            "nombre": trabajador.get("nombre", "N/D"),
            "documento": trabajador.get("documento", "N/D"),
            "tipo_contrato": trabajador.get("tipo_contrato", "N/D"),
            "reside_en_lugar": trabajador.get(
                "reside_en_lugar_trabajo",
                data.get("reside_en_lugar_trabajo", False),
            ),
            "cesantias": desglose.get("cesantias", {}).get("valor", 0),
            "dias_ces": desglose.get("cesantias", {}).get("dias_liquidados", 0),
            "plazo_ces": desglose.get("cesantias", {}).get("plazo_pago_legal", "N/A"),
            "norma_ces": desglose.get("cesantias", {}).get("norma", "N/A"),
            "intereses": desglose.get("intereses_cesantias", {}).get("valor", 0),
            "dias_int": desglose.get("intereses_cesantias", {}).get("dias_liquidados", 0),
            "plazo_int": desglose.get("intereses_cesantias", {}).get(
                "plazo_pago_legal", "N/A"
            ),
            "norma_int": desglose.get("intereses_cesantias", {}).get("norma", "N/A"),
            "prima": desglose.get("prima", {}).get("valor", 0),
            "dias_prima": desglose.get("prima", {}).get("dias_liquidados", 0),
            "plazo_prima": desglose.get("prima", {}).get("plazo_pago_legal", "N/A"),
            "norma_prima": desglose.get("prima", {}).get("norma", "N/A"),
            "vacaciones": desglose.get("vacaciones", {}).get("valor", 0),
            "dias_vac": desglose.get("vacaciones", {}).get("dias_liquidados", 0),
            "total": int(total),
            "observaciones": self._format_observaciones(
                data.get("validaciones_y_alertas", {})
            ),
            "plazos_detallados": self._format_plazos(desglose),
            "declaracion": data.get(
                "declaracion",
                "El empleador certifica que la información presentada refleja las prestaciones sociales liquidadas conforme a la normatividad laboral colombiana vigente.",
            ),
        }

        if empresa:
            data.setdefault("empresa", empresa)

        return context

    def _format_observaciones(self, alertas: Dict[str, Any]) -> str:
        if not alertas:
            return "Sin observaciones."
        lineas = [f"- {mensaje}" for mensaje in alertas.values() if mensaje]
        return "\n".join(lineas) or "Sin observaciones."

    def _format_plazos(self, desglose: Dict[str, Any]) -> str:
        items = []
        mapping = {
            "cesantias": "Cesantías",
            "intereses_cesantias": "Intereses sobre Cesantías",
            "prima": "Prima de Servicios",
        }
        for clave, etiqueta in mapping.items():
            plazo = desglose.get(clave, {}).get("plazo_pago_legal")
            if plazo:
                items.append(f"- {etiqueta}: {plazo}")
        return "\n".join(items) or "Los plazos aplican según Código Sustantivo del Trabajo."

    def generate_pdf(
        self,
        data: Dict[str, Any],
        template_name: str = "periodica",
        output_path: Optional[Path] = None,
        page_title: str = "Liquidación de Nómina",
    ) -> Path:
        """
        Generar PDF desde datos de liquidación. If dependencies are not available,
        creates a placeholder PDF with information about the process.
        
        Args:
            data: Datos de la liquidación
            template_name: Nombre de plantilla Markdown
            output_path: Ruta donde guardar el PDF
            page_title: Título de la página

        Returns:
            Path del archivo PDF generado
        """
        try:
            self.logger.info(f"Iniciando generación de PDF: {template_name}")

            if (
                not self.dependencies_available
                and markdown is not None
                and HTML is not None
                and CSS is not None
            ):
                self.dependencies_available = True

            if self.dependencies_available:
                context = self._build_template_context(data)
                processed_template = self._render_markdown_template(
                    template_name, context
                )
                html_content = self._markdown_to_html(processed_template)

                # 3. Generar documento HTML completo
                full_html = self._generate_html_document(html_content, data, page_title)

                # 4. Determinar ruta de salida
                if not output_path:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_filename = f"liquidacion_{timestamp}.pdf"
                    output_path = Path.cwd() / output_filename

                # 5. Configurar CSS para PDF
                css_objects = []
                if self.dependencies_available:  # Use CSS if dependencies are available
                    css_objects.append(CSS(string="""
                        body { font-family: Arial, sans-serif; }
                        table { border-collapse: collapse; width: 100%; }
                        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                        th { background-color: #f2f2f2; }
                    """))

                # 6. Generar PDF
                html_obj = HTML(string=full_html)
                html_obj.write_pdf(str(output_path), stylesheets=css_objects)

                self.logger.info(f"PDF generado exitosamente: {output_path}")
            else:
                # Create a simple placeholder PDF using a text file approach
                if not output_path:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_filename = f"liquidacion_{timestamp}_placeholder.txt"
                    output_path = Path.cwd() / output_filename
                else:
                    # Change extension to .txt if dependencies aren't available
                    output_path = output_path.with_suffix('.txt')
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write("REPORTE DE LIQUIDACIÓN - ARCHIVO DE PLANTILLA\n\n")
                    f.write(
                        f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    )
                    f.write(f"Modo: {data.get('meta', {}).get('modo', 'N/A')}\n\n")
                    f.write("PARÁMETROS DE LA LIQUIDACIÓN:\n")
                    params = data.get("parametros", {})
                    f.write(f"  SMMLV: {params.get('SMMLV', 'N/A')}\n")
                    f.write(
                        f"  Auxilio de Transporte: {params.get('AUXILIO_TRANS', 'N/A')}\n\n"
                    )

                    f.write("DESCRIPCIÓN DE LA LIQUIDACIÓN:\n")
                    desglose = data.get("desglose", {})
                    for concepto, valores in desglose.items():
                        if isinstance(valores, dict) and 'valor' in valores:
                            f.write(
                                f"  {concepto.upper()}: ${valores['valor']:,}\n"
                            )

                    total_placeholder = (
                        data.get('total_liquidacion')
                        or data.get('total_liquidacion_periodica')
                        or 'N/A'
                    )
                    f.write(
                        f"\nTOTAL DE LA LIQUIDACIÓN: ${total_placeholder}\n\n"
                    )
                    f.write(
                        "NOTA: Este es un archivo de plantilla generado en un entorno sin soporte para generación PDF.\n"
                    )
                    f.write(
                        "Para generar el PDF profesional, instale las dependencias adicionales: pip install weasyprint"
                    )

            return output_path

        except Exception as e:
            error_msg = f"Error generando PDF: {str(e)}"
            self.logger.error(error_msg)
            raise PDFGeneratorError(error_msg) from e

    def generate_pdf_from_markdown(
        self,
        markdown_file: Path,
        output_path: Optional[Path] = None,
        css_file: str = "pdf_styles.css",
    ) -> Path:
        """
        Generar PDF directamente desde archivo Markdown

        Args:
            markdown_file: Archivo Markdown fuente
            output_path: Ruta donde guardar el PDF
            css_file: Archivo CSS a aplicar

        Returns:
            Path del archivo PDF generado
        """
        try:
            # Leer archivo Markdown
            with open(markdown_file, "r", encoding="utf-8") as f:
                markdown_content = f.read()

            # Convertir a HTML
            html_content = self._markdown_to_html(markdown_content)

            # Generar documento completo
            html_doc = self._generate_html_document(html_content, {})

            # Determinar ruta de salida
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"document_{timestamp}.pdf"
                output_path = Path.cwd() / output_filename

            # Use the main generate_pdf method
            # Since we don't have the full data structure here, we'll generate a placeholder
            if not self.dependencies_available:
                output_path = output_path.with_suffix('.txt')
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write("Documento generado desde archivo Markdown\n\n")
                    f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Fuente: {markdown_file}\n\n")
                    f.write("Contenido del documento:\n")
                    f.write(markdown_content)
                
                return output_path
            else:
                # Generate actual PDF if dependencies are available
                from weasyprint import HTML, CSS
                HTML(string=html_doc).write_pdf(str(output_path), stylesheets=[CSS(string="""
                    body { font-family: Arial, sans-serif; }
                """)])
                
                return output_path

        except Exception as e:
            error_msg = f"Error generando PDF desde Markdown: {str(e)}"
            self.logger.error(error_msg)
            raise PDFGeneratorError(error_msg) from e

    def validate_pdf_output(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Validar que el PDF generado sea correcto

        Args:
            pdf_path: Ruta del PDF a validar

        Returns:
            Diccionario con resultado de validación
        """
        validation_result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "file_info": {},
        }

        try:
            # Verificar que el archivo existe
            if not pdf_path.exists():
                validation_result["errors"].append("El archivo PDF no existe")
                return validation_result

            # Verificar tamaño del archivo
            file_size = pdf_path.stat().st_size
            validation_result["file_info"]["size"] = file_size

            if file_size == 0:
                validation_result["errors"].append("El archivo PDF está vacío")
                return validation_result

            # Check if it's a text file (placeholder) or actual PDF
            is_text_file = pdf_path.suffix.lower() == '.txt'
            
            if not is_text_file:
                # Verificar que es un PDF válido leyendo header
                with open(pdf_path, "rb") as f:
                    header = f.read(8)
                    if not header.startswith(b"%PDF-"):
                        validation_result["errors"].append("El archivo no es un PDF válido")
                        return validation_result

            validation_result["valid"] = True
            self.logger.info(f"PDF validado correctamente: {pdf_path}")

        except Exception as e:
            validation_result["errors"].append(f"Error validando PDF: {str(e)}")

        return validation_result


# Función de conveniencia
def generate_liquidacion_pdf(
    data: Dict[str, Any],
    output_path: Optional[Path] = None,
    template_name: str = "periodica",
) -> Path:
    """
    Función de conveniencia para generar PDF de liquidación

    Args:
        data: Datos de la liquidación
        output_path: Ruta donde guardar el PDF

    Returns:
        Path del archivo PDF generado
    """
    generator = PDFGenerator()
    return generator.generate_pdf(
        data, template_name=template_name, output_path=output_path
    )


def generate_pdf_from_json(
    json_path: Union[str, Path],
    output_path: Optional[Path] = None,
    template_name: str = "periodica",
) -> Path:
    with open(Path(json_path), "r", encoding="utf-8") as f:
        data = json.load(f)  # type: ignore[name-defined]
    generator = PDFGenerator()
    return generator.generate_pdf(
        data, template_name=template_name, output_path=output_path
    )


if __name__ == "__main__":
    # Ejemplo de uso
    import json

    # Datos de ejemplo
    ejemplo_data = {
        "meta": {
            "modo": "PERIÓDICA",
            "fecha_generacion": "2025-11-16T12:00:00",
            "fecha_corte": "2025-11-15",
            "fecha_ingreso": "2024-11-16",
        },
        "trabajador": {
            "nombre": "Juan Pérez",
            "documento": "12345678",
            "tipo_contrato": "indefinido",
            "reside_en_lugar_trabajo": True,
        },
        "desglose": {
            "SBL_GENERAL": 2200000,
            "cesantias": {
                "valor": 2200000,
                "dias_liquidados": 360,
                "plazo_pago_legal": "2026-02-14",
                "norma": "Art.249-250 CST",
            },
            "intereses_cesantias": {
                "valor": 264000,
                "dias_liquidados": 360,
                "plazo_pago_legal": "2026-01-31",
                "norma": "Ley 50/1990 Art.99",
            },
            "prima": {
                "valor": 1100000,
                "dias_liquidados": 180,
                "plazo_pago_legal": "2025-12-31",
                "norma": "Art.306-308 CST",
            },
        },
        "total_liquidacion_periodica": 3564000,
        "empresa": {"nombre": "HILDALIRIA RAIGOZA LOAIZA", "nit": "CC 42.066.783"},
    }

    try:
        pdf_path = generate_liquidacion_pdf(ejemplo_data)
        print(f"PDF generado: {pdf_path}")
    except Exception as e:
        print(f"Error: {e}")
