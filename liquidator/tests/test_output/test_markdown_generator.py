"""
Tests for Markdown Generator
"""

import os
import tempfile
import unittest
from liquidator.output.markdown_generator import MarkdownGenerator


class TestMarkdownGenerator(unittest.TestCase):
    """Test cases for MarkdownGenerator class"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = MarkdownGenerator()

        # Sample JSON data
        self.json_data = {
            "meta": {
                "modo": "PERIÓDICA",
                "fecha_corte": "2025-11-15",
                "fecha_ingreso": "2024-11-16",
            },
            "trabajador": {
                "nombre": "Juan Pérez",
                "documento": "123456789",
                "tipo_contrato": "indefinido",
                "reside_en_lugar_trabajo": True,
            },
            "desglose": {
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
                "vacaciones": {
                    "valor": 0,
                    "dias_liquidados": 0,
                    "norma": "Arts.186-192 CST",
                    "nota": "No aplica en modo PERIÓDICA, solo en FINIQUITO",
                },
            },
            "total_liquidacion_periodica": 3564000,
            "validaciones_y_alertas": {
                "auxilio_transporte_excluido": "Residencia en el lugar de trabajo (Finca).",
                "auxilio_conectividad_advertencia": "Verificar si está pactado como parte del salario habitual.",
            },
        }

    def test_generate_markdown_periodica(self):
        """Test Markdown generation for PERIÓDICA mode"""
        markdown = self.generator.generate_markdown(self.json_data)

        # Check that key sections are present
        self.assertIn("LIQUIDACIÓN PERIÓDICA DE PRESTACIONES SOCIALES", markdown)
        self.assertIn("DATOS DEL TRABAJADOR", markdown)
        self.assertIn("DETALLE DE PRESTACIONES", markdown)
        self.assertIn("TOTAL LIQUIDACIÓN PERIÓDICA", markdown)
        self.assertIn("OBSERVACIONES", markdown)
        self.assertIn("PLAZOS LEGALES DE PAGO", markdown)
        self.assertIn("DECLARACIÓN LEGAL", markdown)

        # Check that values are correctly formatted
        self.assertIn("$2.200.000", markdown)  # Cesantías
        self.assertIn("$264.000", markdown)  # Intereses
        self.assertIn("$1.100.000", markdown)  # Prima
        self.assertIn("$3.564.000", markdown)  # Total

        # Check that worker data is present
        self.assertIn("Juan Pérez", markdown)
        self.assertIn("123456789", markdown)
        self.assertIn("indefinido", markdown)
        self.assertIn("Sí", markdown)  # Reside en lugar de trabajo

        # Check that observations are present
        self.assertIn("Residencia en el lugar de trabajo", markdown)
        self.assertIn(
            "Verificar si está pactado como parte del salario habitual", markdown
        )

    def test_generate_markdown_finiquito(self):
        """Test Markdown generation for FINIQUITO mode"""
        # Update JSON data to FINIQUITO mode
        self.json_data["meta"]["modo"] = "FINIQUITO"
        self.json_data["total_liquidacion_finiquito"] = 3564000

        # Add finiquito-specific fields
        self.json_data["desglose"]["indemnizacion"] = {
            "valor": 4400000,
            "dias_liquidados": 360,
            "norma": "Art.64 CST",
        }
        self.json_data["desglose"]["salario_pendiente"] = {
            "valor": 0,
            "dias_liquidados": 0,
            "norma": "Art.65 CST",
        }

        markdown = self.generator.generate_markdown(self.json_data)

        # Check that key sections are present
        self.assertIn("LIQUIDACIÓN POR FINIQUITO DE PRESTACIONES SOCIALES", markdown)
        self.assertIn("TOTAL LIQUIDACIÓN POR FINIQUITO", markdown)

        # Check that indemnization and salary pending are present
        self.assertIn("Indemnización", markdown)
        self.assertIn("Salario pendiente", markdown)

    def test_save_markdown(self):
        """Test saving Markdown to file"""
        markdown = self.generator.generate_markdown(self.json_data)

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            temp_path = f.name

        try:
            # Save Markdown
            result = self.generator.save_markdown(markdown, temp_path)
            self.assertTrue(result)

            # Verify file exists and contains content
            self.assertTrue(os.path.exists(temp_path))
            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Verify content
            self.assertIn("LIQUIDACIÓN PERIÓDICA DE PRESTACIONES SOCIALES", content)
            self.assertIn("$3.564.000", content)
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_format_observaciones(self):
        """Test formatting of observations"""
        validaciones = {
            "auxilio_transporte_excluido": "Residencia en el lugar de trabajo (Finca).",
            "auxilio_conectividad_advertencia": "Verificar si está pactado como parte del salario habitual.",
        }

        result = self.generator._format_observaciones(validaciones)

        # Check that observations are formatted as a list
        self.assertIn("- Residencia en el lugar de trabajo (Finca).", result)
        self.assertIn(
            "- Verificar si está pactado como parte del salario habitual.", result
        )

    def test_format_observaciones_empty(self):
        """Test formatting of empty observations"""
        result = self.generator._format_observaciones({})
        self.assertEqual(result, "Ninguna observación.")

    def test_format_plazos(self):
        """Test formatting of payment deadlines"""
        result = self.generator._format_plazos(self.json_data)

        # Check that deadlines are formatted as a list
        self.assertIn("- Cesantías: 2026-02-14 (Art.249-250 CST)", result)
        self.assertIn(
            "- Intereses sobre cesantías: 2026-01-31 (Ley 50/1990 Art.99)", result
        )
        self.assertIn("- Prima de servicios: 2025-12-31 (Art.306-308 CST)", result)

    def test_get_declaracion(self):
        """Test getting legal declaration"""
        # Test PERIÓDICA mode
        result = self.generator._get_declaracion("PERIÓDICA")
        self.assertIn("prestaciones sociales causadas en el período indicado", result)
        self.assertIn("cesantías serán consignadas", result)

        # Test FINIQUITO mode
        result = self.generator._get_declaracion("FINIQUITO")
        self.assertIn(
            "totalidad de las prestaciones sociales e indemnizaciones", result
        )
        self.assertIn("trabajador declara haber recibido el pago total", result)


if __name__ == "__main__":
    unittest.main()
