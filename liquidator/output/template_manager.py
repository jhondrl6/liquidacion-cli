"""
Template Manager Module
Loads and manages Markdown templates for document generation
"""

import os
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template


class TemplateManager:
    """Manages loading and rendering of Markdown templates"""

    def __init__(self, templates_dir: str = "templates"):
        """
        Initialize the template manager

        Args:
            templates_dir: Directory containing template files
        """
        self.templates_dir = templates_dir
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        self.templates = {}
        self._load_templates()

    def _load_templates(self):
        """Load all available templates"""

        main_templates = {
            "periodica": "comprobante_periodica.md",
            "finiquito": "comprobante_finiquito.md",
        }
        partial_templates = {
            "header": "partials/header.md",
            "footer": "partials/footer.md",
            "firmas": "partials/firmas.md",
        }

        for key, filename in main_templates.items():
            try:
                self.templates[key] = self.env.get_template(filename)
            except Exception:
                pass

        for key, filename in partial_templates.items():
            try:
                self.templates[key] = self.env.get_template(filename)
            except Exception:
                pass

    def get_template(self, template_name: str) -> Optional[Template]:
        """
        Get a specific template by name

        Args:
            template_name: Name of the template

        Returns:
            Jinja2 Template object or None if not found
        """
        return self.templates.get(template_name)

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with the given context

        Args:
            template_name: Name of the template to render
            context: Variables to substitute in the template

        Returns:
            Rendered template as string
        """
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")

        # Add currency formatting filter
        template.globals["format_currency"] = self._format_currency

        return template.render(**context)

    def _format_currency(self, value: int) -> str:
        """
        Format a number as Colombian currency

        Args:
            value: Numeric value to format

        Returns:
            Formatted currency string
        """
        return f"${value:,}".replace(",", ".")
