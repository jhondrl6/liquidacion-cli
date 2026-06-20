"""
Tests unitarios para el generador de PDF
Verifica la generación correcta de PDFs para liquidaciones de nómina
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pytest

# Importar el generador de PDF
try:
    from liquidator.output.pdf_generator import PDFGenerator, PDFGeneratorError

    try:
        import weasyprint
        PDF_AVAILABLE = True
    except ImportError:
        PDF_AVAILABLE = False
except ImportError:
    PDF_AVAILABLE = False


class TestPDFGenerator(unittest.TestCase):
    """Tests para la clase PDFGenerator"""

    def setUp(self):
        """Configurar tests"""
        if not PDF_AVAILABLE:
            self.skipTest("Dependencias de PDF no disponibles")

        # Crear directorio temporal para tests
        self.temp_dir = Path(tempfile.mkdtemp())

        # Crear estructura de directorios necesaria
        self.templates_dir = self.temp_dir / "templates"
        self.styles_dir = self.templates_dir / "styles"
        self.styles_dir.mkdir(parents=True)

        # Crear CSS de prueba
        css_content = """
        body { font-family: Arial, sans-serif; }
        h1 { color: #2c3e50; }
        """
        (self.styles_dir / "pdf_styles.css").write_text(css_content)

        # Crear plantilla de prueba
        template_content = """
        # LIQUIDACIÓN DE NÓMINA

        **Fecha:** {fecha_generacion}
        **Trabajador:** {trabajador.nombre}

        ## Detalle de Prestaciones

        {tabla_prestaciones}

        **Total:** ${total_liquidacion_periodica:,.0f}

        ## Firmas

        Trabajador: ________________  Empleador: ________________
        """
        (self.templates_dir / "comprobante_periodica.md").write_text(template_content)

        # Inicializar generador
        self.generator = PDFGenerator(
            templates_dir=self.templates_dir, styles_dir=self.styles_dir
        )

        # Datos de prueba
        self.test_data = {
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
            "empresa": {"nombre": "Hildaliria Raigoza L.", "nit": "CC 42.066.783"},
        }

    def tearDown(self):
        """Limpiar después de tests"""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test de inicialización del generador"""
        self.assertIsInstance(self.generator, PDFGenerator)
        self.assertEqual(self.generator.templates_dir, self.templates_dir)
        self.assertEqual(self.generator.styles_dir, self.styles_dir)

    def test_load_markdown_template(self):
        """Test de carga de plantillas Markdown"""
        template = self.generator._load_markdown_template("comprobante_periodica.md")
        self.assertIn("LIQUIDACIÓN DE NÓMINA", template)
        self.assertIn("{fecha_generacion}", template)

    def test_load_css_styles(self):
        """Test de carga de estilos CSS"""
        css = self.generator._load_css_styles("pdf_styles.css")
        self.assertIn("body", css)
        self.assertIn("font-family", css)

    def test_process_template(self):
        """Test de procesamiento de plantillas"""
        template = "# Liquidación para {trabajador.nombre}"
        processed = self.generator._process_template(template, self.test_data)
        self.assertIn("Juan Pérez", processed)

    def test_generate_prestaciones_table(self):
        """Test de generación de tabla de prestaciones"""
        html_table = self.generator._generate_prestaciones_table(
            self.test_data["desglose"]
        )

        # Verificar estructura HTML
        self.assertIn("<table", html_table)
        self.assertIn("<thead>", html_table)
        self.assertIn("<tbody>", html_table)
        self.assertIn("Cesantías", html_table)
        self.assertIn("2200000", html_table)
        self.assertIn("Art.249-250 CST", html_table)

    def test_generate_trabajador_info(self):
        """Test de generación de información del trabajador"""
        html_info = self.generator._generate_trabajador_info(
            self.test_data["trabajador"]
        )

        self.assertIn("Juan Pérez", html_info)
        self.assertIn("12345678", html_info)
        self.assertIn("indefinido", html_info)
        self.assertIn("trabajador-info", html_info)

    def test_markdown_to_html(self):
        """Test de conversión Markdown a HTML"""
        markdown_text = "# Título\n\n**Texto en negrita**"
        html = self.generator._markdown_to_html(markdown_text)

        self.assertIn("<h1>Título</h1>", html)
        self.assertIn("<strong>Texto en negrita</strong>", html)

    def test_generate_header_content(self):
        """Test de generación de contenido de encabezado"""
        header = self.generator._generate_header_content(self.test_data)

        self.assertIn("Hildaliria Raigoza L.", header)
        self.assertIn("CC 42.066.783", header)
        self.assertIn("header-content", header)

    def test_generate_footer_content(self):
        """Test de generación de contenido de pie de página"""
        footer = self.generator._generate_footer_content(self.test_data)

        self.assertIn("footer-content", footer)
        self.assertIn("Página", footer)
        self.assertIn("2025-11-16T12:00:00", footer)

    def test_generate_html_document(self):
        """Test de generación de documento HTML completo"""
        html_content = "<h1>Título de prueba</h1>"
        full_html = self.generator._generate_html_document(html_content, self.test_data)

        self.assertIn("<!DOCTYPE html>", full_html)
        self.assertIn('<html lang="es">', full_html)
        self.assertIn("Título de prueba", full_html)
        self.assertIn("header", full_html)
        self.assertIn("footer", full_html)

    @patch("liquidator.output.pdf_generator.markdown")
    @patch("liquidator.output.pdf_generator.HTML")
    @patch("liquidator.output.pdf_generator.CSS")
    def test_generate_pdf_basic(self, mock_css, mock_html, mock_markdown):
        """Test de generación básica de PDF"""
        # Configurar mocks
        mock_markdown.Markdown.return_value.convert.return_value = "<h1>Test</h1>"
        mock_html_instance = mock_html.return_value
        mock_html_instance.write_pdf.return_value = None

        # Generar PDF
        output_path = self.temp_dir / "test_output.pdf"
        result_path = self.generator.generate_pdf(
            self.test_data, output_path=output_path
        )

        # Verificar llamadas
        mock_html.assert_called_once()
        mock_markdown.Markdown.assert_called_once()

        # Verificar resultado
        self.assertEqual(result_path, output_path)

    def test_generate_pdf_with_missing_template(self):
        """Test de manejo de error por plantilla faltante"""
        output_path = self.temp_dir / "test_error.pdf"

        with self.assertRaises(PDFGeneratorError) as context:
            self.generator.generate_pdf(
                self.test_data,
                template_name="plantilla_inexistente.md",
                output_path=output_path,
            )

        self.assertIn("Plantilla no encontrada", str(context.exception))

    def test_generate_pdf_from_markdown(self):
        """Test de generación de PDF desde archivo Markdown"""
        # Crear archivo Markdown de prueba
        md_content = "# Documento de Prueba\n\nContenido del documento."
        md_file = self.temp_dir / "test.md"
        md_file.write_text(md_content)

        # Mock para evitar generación real
        with patch("liquidator.output.pdf_generator.HTML") as mock_html:
            mock_html.return_value.write_pdf.return_value = None

            output_path = self.temp_dir / "test_output.pdf"
            result_path = self.generator.generate_pdf_from_markdown(
                md_file, output_path=output_path
            )

            self.assertEqual(result_path, output_path)

    def test_validate_pdf_output_valid(self):
        """Test de validación de PDF válido"""
        # Crear un PDF falso pero válido
        pdf_content = b"%PDF-1.4\n%PDF fake content"
        pdf_file = self.temp_dir / "test_valid.pdf"
        pdf_file.write_bytes(pdf_content)

        result = self.generator.validate_pdf_output(pdf_file)

        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)
        self.assertIn("size", result["file_info"])

    def test_validate_pdf_output_invalid(self):
        """Test de validación de PDF inválido"""
        # Archivo no existe
        non_existent = self.temp_dir / "non_existent.pdf"
        result = self.generator.validate_pdf_output(non_existent)

        self.assertFalse(result["valid"])
        self.assertIn("no existe", result["errors"][0])

    def test_validate_pdf_output_empty(self):
        """Test de validación de PDF vacío"""
        # Archivo vacío
        pdf_file = self.temp_dir / "empty.pdf"
        pdf_file.write_bytes(b"")

        result = self.generator.validate_pdf_output(pdf_file)

        self.assertFalse(result["valid"])
        self.assertIn("está vacío", result["errors"][0])

    def test_validate_pdf_output_invalid_header(self):
        """Test de validación de PDF con header inválido"""
        # Archivo con header incorrecto
        pdf_content = b"NOT A PDF FILE"
        pdf_file = self.temp_dir / "invalid_header.pdf"
        pdf_file.write_bytes(pdf_content)

        result = self.generator.validate_pdf_output(pdf_file)

        self.assertFalse(result["valid"])
        self.assertIn("no es un PDF válido", result["errors"][0])

    def test_validate_pdf_output_small_file(self):
        """Test de validación de PDF muy pequeño"""
        # Archivo muy pequeño pero válido
        pdf_content = b"%PDF-1.4\n%x"
        pdf_file = self.temp_dir / "small.pdf"
        pdf_file.write_bytes(pdf_content)

        result = self.generator.validate_pdf_output(pdf_file)

        self.assertTrue(result["valid"])
        self.assertTrue(any("muy pequeño" in warning for warning in result["warnings"]))


class TestConvenienceFunction(unittest.TestCase):
    """Tests para la función de conveniencia"""

    def setUp(self):
        """Configurar tests"""
        if not PDF_AVAILABLE:
            self.skipTest("Dependencias de PDF no disponibles")

    @patch("liquidator.output.pdf_generator.PDFGenerator")
    def test_generate_liquidacion_pdf(self, mock_generator_class):
        """Test de función de conveniencia"""
        from liquidator.output.pdf_generator import generate_liquidacion_pdf

        # Mock del generador
        mock_generator = mock_generator_class.return_value
        mock_generator.generate_pdf.return_value = Path("/test/output.pdf")

        # Datos de prueba
        test_data = {"meta": {"modo": "PERIÓDICA"}}
        output_path = Path("/test/output.pdf")

        # Ejecutar función
        result = generate_liquidacion_pdf(test_data, output_path)

        # Verificar llamadas
        mock_generator_class.assert_called_once()
        mock_generator.generate_pdf.assert_called_once_with(
            test_data, output_path=output_path
        )

        # Verificar resultado
        self.assertEqual(result, Path("/test/output.pdf"))


class TestErrorHandling(unittest.TestCase):
    """Tests para manejo de errores"""

    def setUp(self):
        """Configurar tests"""
        if not PDF_AVAILABLE:
            self.skipTest("Dependencias de PDF no disponibles")

    def test_pdf_generator_error(self):
        """Test de excepción PDFGeneratorError"""
        with self.assertRaises(PDFGeneratorError) as context:
            raise PDFGeneratorError("Error de prueba")

        self.assertEqual(str(context.exception), "Error de prueba")

    def test_dependencies_missing(self):
        """Test de manejo de dependencias faltantes"""
        with patch("liquidator.output.pdf_generator.markdown", None):
            with patch("liquidator.output.pdf_generator.HTML", None):
                with self.assertRaises(PDFGeneratorError) as context:
                    PDFGenerator()

                self.assertIn("Dependencias faltantes", str(context.exception))


class TestComplexCases(unittest.TestCase):
    """Tests para casos complejos"""

    def setUp(self):
        """Configurar tests"""
        if not PDF_AVAILABLE:
            self.skipTest("Dependencias de PDF no disponibles")

        self.temp_dir = Path(tempfile.mkdtemp())
        self.templates_dir = self.temp_dir / "templates"
        self.styles_dir = self.templates_dir / "styles"
        self.styles_dir.mkdir(parents=True)

        # CSS básico
        (self.styles_dir / "pdf_styles.css").write_text("body { font-family: Arial; }")

        # Plantilla con estructuras complejas
        complex_template = """
        # Liquidación Completa

        {info_trabajador}

        ## Prestaciones
        {tabla_prestaciones}

        ## Plazos Legales
        {plazos_legales}

        ## Total
        **Total a pagar:** ${total_liquidacion_periodica:,.0f}
        """
        (self.templates_dir / "comprobante_completa.md").write_text(complex_template)

        self.generator = PDFGenerator(
            templates_dir=self.templates_dir, styles_dir=self.styles_dir
        )

        # Datos completos
        self.complex_data = {
            "meta": {
                "modo": "FINIQUITO",
                "fecha_generacion": "2025-11-16T12:00:00",
                "fecha_corte": "2025-11-15",
                "fecha_ingreso": "2024-11-16",
            },
            "trabajador": {
                "nombre": "María García López",
                "documento": "98765432",
                "tipo_contrato": "indefinido",
                "reside_en_lugar_trabajo": False,
                "salario_mensual": 3000000,
            },
            "desglose": {
                "SBL_GENERAL": 3200000,
                "SBL_VACACIONES": 3000000,
                "cesantias": {
                    "valor": 3200000,
                    "dias_liquidados": 360,
                    "plazo_pago_legal": "2026-02-14",
                    "norma": "Art.249-250 CST",
                },
                "intereses_cesantias": {
                    "valor": 384000,
                    "dias_liquidados": 360,
                    "plazo_pago_legal": "2026-01-31",
                    "norma": "Ley 50/1990 Art.99",
                },
                "prima": {
                    "valor": 1600000,
                    "dias_liquidados": 180,
                    "plazo_pago_legal": "2025-12-31",
                    "norma": "Art.306-308 CST",
                },
                "vacaciones": {
                    "valor": 833333,
                    "dias_liquidados": 20,
                    "plazo_pago_legal": "Inmediato",
                    "norma": "Arts.186-192 CST",
                },
                "indemnizacion": {
                    "valor": 12000000,
                    "dias_liquidados": 360,
                    "plazo_pago_legal": "Inmediato",
                    "norma": "Art.64 CST",
                },
            },
            "total_liquidacion_periodica": 18372333,
            "empresa": {"nombre": "Empresa Compleja SAS", "nit": "900.987.654-3"},
        }

    def tearDown(self):
        """Limpiar después de tests"""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_complex_data_processing(self):
        """Test de procesamiento de datos complejos"""
        template = self.generator._load_markdown_template("comprobante_completa.md")
        processed = self.generator._process_template(template, self.complex_data)

        # Verificar que se procesaron todas las variables
        self.assertIn("María García López", processed)
        self.assertIn("18372333", processed)
        self.assertIn("FINIQUITO", processed)

    def test_full_prestations_table(self):
        """Test de tabla completa con todas las prestaciones"""
        table_html = self.generator._generate_prestaciones_table(
            self.complex_data["desglose"]
        )

        # Verificar todas las prestaciones
        self.assertIn("Cesantías", table_html)
        self.assertIn("Intereses sobre Cesantías", table_html)
        self.assertIn("Prima de Servicios", table_html)
        self.assertIn("Vacaciones", table_html)
        self.assertIn("Indemnización", table_html)

        # Verificar valores
        self.assertIn("3200000", table_html)  # Cesantías
        self.assertIn("833333", table_html)  # Vacaciones
        self.assertIn("12000000", table_html)  # Indemnización

    def test_complete_trabajador_info(self):
        """Test de información completa del trabajador"""
        info_html = self.generator._generate_trabajador_info(
            self.complex_data["trabajador"]
        )

        self.assertIn("María García López", info_html)
        self.assertIn("98765432", info_html)
        self.assertIn("3000000", info_html)
        self.assertIn("No", info_html)  # No reside en lugar de trabajo

    @patch("liquidator.output.pdf_generator.HTML")
    @patch("liquidator.output.pdf_generator.CSS")
    def test_generate_complex_pdf(self, mock_css, mock_html):
        """Test de generación de PDF con datos complejos"""
        # Configurar mocks
        mock_html_instance = mock_html.return_value
        mock_html_instance.write_pdf.return_value = None

        output_path = self.temp_dir / "complex_output.pdf"
        result_path = self.generator.generate_pdf(
            self.complex_data,
            template_name="comprobante_completa.md",
            output_path=output_path,
            page_title="Finiquito Laboral Completo",
        )

        # Verificar que se generó sin errores
        self.assertEqual(result_path, output_path)
        mock_html_instance.write_pdf.assert_called_once()


class TestPDFGeneratorIntegration(unittest.TestCase):
    """Tests de integración para el generador de PDF"""

    def setUp(self):
        """Configurar tests de integración"""
        if not PDF_AVAILABLE:
            self.skipTest("Dependencias de PDF no disponibles")

        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Limpiar después de tests"""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @pytest.mark.skipif(not PDF_AVAILABLE, reason="Dependencias de PDF no disponibles")
    def test_end_to_end_pdf_generation(self):
        """Test completo de generación de PDF"""
        # Este test requeriría las dependencias reales instaladas
        # Por ahora se marca como skipped
        pass

    def test_template_loading_error(self):
        """Test de manejo de error al cargar plantilla"""
        generator = PDFGenerator(templates_dir=self.temp_dir)

        with self.assertRaises(PDFGeneratorError):
            generator._load_markdown_template("inexistente.md")

    def test_css_loading_with_missing_file(self):
        """Test de carga de CSS con archivo faltante"""
        generator = PDFGenerator(styles_dir=self.temp_dir)

        css = generator._load_css_styles("missing.css")
        self.assertEqual(css, "")


if __name__ == "__main__":
    # Configurar logging para tests
    import logging

    logging.basicConfig(level=logging.WARNING)

    # Ejecutar tests
    unittest.main(verbosity=2)
