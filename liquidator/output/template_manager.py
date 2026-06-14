"""
Template Manager Module
Loads and manages Markdown templates for document generation
"""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template

# Default: directorio de plantillas del paquete (liquidator/templates/).
# Antes del packaging v2.0, el default era "templates" relativo a cwd,
# lo cual fallaba al instalar el paquete via `pip install -e .`.
# Ver REGISTRY.md (S14 — Tarea 1.A-plan) y KB_LLM/06 R-OP-07.
_DEFAULT_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


class TemplateManager:
    """Manages loading and rendering of Markdown templates"""

    def __init__(self, templates_dir: str | None = None):
        """
        Initialize the template manager

        Args:
            templates_dir: Directory containing template files.
                Si None, usa las plantillas que viajan con el paquete
                (liquidator/templates/).
        """
        self.templates_dir = templates_dir or str(_DEFAULT_TEMPLATES_DIR)
        self.env = Environment(loader=FileSystemLoader(self.templates_dir))
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

    def get_template(self, template_name: str) -> Template | None:
        """
        Get a specific template by name

        Args:
            template_name: Name of the template

        Returns:
            Jinja2 Template object or None if not found
        """
        return self.templates.get(template_name)

    def render_template(self, template_name: str, context: dict[str, Any]) -> str:
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
