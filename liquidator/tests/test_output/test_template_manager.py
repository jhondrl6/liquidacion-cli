"""
Tests for Template Manager
"""

import os
import tempfile
import unittest

from liquidator.output.template_manager import TemplateManager


class TestTemplateManager(unittest.TestCase):
    """Test cases for TemplateManager class"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for templates
        self.temp_dir = tempfile.mkdtemp()

        # Create main templates
        with open(os.path.join(self.temp_dir, "comprobante_periodica.md"), "w") as f:
            f.write(
                "# LIQUIDACIÓN PERIÓDICA\n\nFecha: {{ fecha }}\n\nTotal: {{ format_currency(total) }}"
            )

        with open(os.path.join(self.temp_dir, "comprobante_finiquito.md"), "w") as f:
            f.write(
                "# LIQUIDACIÓN POR FINIQUITO\n\nFecha: {{ fecha }}\n\nTotal: {{ format_currency(total) }}"
            )

        # Create partials directory and templates
        os.makedirs(os.path.join(self.temp_dir, "partials"))

        with open(os.path.join(self.temp_dir, "partials", "header.md"), "w") as f:
            f.write("# COMPROBANTE DE LIQUIDACIÓN")

        with open(os.path.join(self.temp_dir, "partials", "footer.md"), "w") as f:
            f.write("---\nEste documento es un comprobante.")

        with open(os.path.join(self.temp_dir, "partials", "firmas.md"), "w") as f:
            f.write("---\nFirmas: __________")

        # Initialize template manager
        self.manager = TemplateManager(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temporary directory
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_get_template(self):
        """Test getting a template by name"""
        # Test existing template
        template = self.manager.get_template("periodica")
        self.assertIsNotNone(template)

        # Test non-existing template
        template = self.manager.get_template("nonexistent")
        self.assertIsNone(template)

    def test_render_template(self):
        """Test rendering a template with context"""
        context = {"fecha": "2025-11-16", "total": 3564000}

        result = self.manager.render_template("periodica", context)

        # Check that variables are substituted
        self.assertIn("Fecha: 2025-11-16", result)
        self.assertIn("Total: $3.564.000", result)

    def test_render_template_nonexistent(self):
        """Test rendering a non-existent template"""
        context = {"fecha": "2025-11-16"}

        with self.assertRaises(ValueError):
            self.manager.render_template("nonexistent", context)

    def test_format_currency(self):
        """Test currency formatting"""
        # render_template adds format_currency global
        self.manager.render_template("periodica", {"fecha": "2025-01-01", "total": 1000})
        template = self.manager.get_template("periodica")

        # Test formatting different values
        self.assertEqual(template.globals["format_currency"](1000), "$1.000")
        self.assertEqual(template.globals["format_currency"](3564000), "$3.564.000")
        self.assertEqual(template.globals["format_currency"](0), "$0")


if __name__ == "__main__":
    unittest.main()
