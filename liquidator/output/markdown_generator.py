"""Markdown Generator Module — v2.0 (Tarea 1.F refactor).

Generates readable Markdown documents using Jinja2 templates.
Consumes output from JSONGenerator (Tarea 1.D) in the Pydantic
``LiquidacionResult`` shape (Tarea 1.C).

Cambios (plan §6.2 Tarea 1.F):
1. ``import datetime`` → ``from datetime import datetime, date``.
2. Validar contexto antes de renderizar (no crash si faltan claves).
3. Manejar estados:
   - ``NO_GO`` → plantilla de bloqueo (sin datos del trabajador).
   - ``GO`` / ``WARN`` / ``OVERRIDE_APPROVED`` → plantilla normal con
     sección de advertencias.
4. No fallar si faltan campos opcionales; usar ``data.get("...", default)``.
5. Sanitizar PII en logs de error (no incluir nombres ni documentos).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .template_manager import TemplateManager

# Default: directorio de plantillas del paquete (liquidator/templates/).
# Ver REGISTRY.md (S14 — Tarea 1.A-plan) y KB_LLM/06 R-OP-07.
_DEFAULT_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

# Estados de compliance que se consideran "no bloqueados".
_NON_BLOCKING = frozenset({"GO", "WARN", "OVERRIDE_APPROVED"})


class MarkdownGenerator:
    """Genera documentos Markdown legibles desde datos del motor.

    Consume el output de ``JSONGenerator.generate_output()`` (forma de
    ``LiquidacionResult``) y renderiza plantillas Jinja2 con contexto
    construido a partir del JSON estructurado.
    """

    def __init__(self, templates_dir: Optional[str] = None):
        """Inicializa el generador Markdown.

        Args:
            templates_dir: Directorio con plantillas. Si None, usa
                ``liquidator/templates/`` del paquete.
        """
        self.templates_dir = templates_dir or str(_DEFAULT_TEMPLATES_DIR)
        self.template_manager = TemplateManager(self.templates_dir)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def generate_markdown(
        self,
        json_data: Dict[str, Any],
        status: Optional[str] = None,
    ) -> str:
        """Genera el documento Markdown.

        Args:
            json_data: Datos estructurados del JSONGenerator (forma de
                ``LiquidacionResult``). Debe contener al menos ``meta``,
                ``trabajador``, ``desglose`` y ``total_liquidacion``.
            status: Compliance status override. Si es None, se lee de
                ``json_data["meta"]["compliance_status"]``.

        Returns:
            Markdown renderizado.
        """
        effective_status = self._resolve_status(json_data, status)

        # --- Caso NO_GO: plantilla de bloqueo (sin datos del trabajador) ---
        if effective_status == "NO_GO":
            return self._render_blocked(json_data)

        # --- Validar contexto antes de renderizar ---
        missing = self._validate_context(json_data)
        if missing:
            return self._render_context_error(missing)

        # --- Construir contexto y renderizar ---
        context = self._build_context(json_data, effective_status)

        modo = (json_data.get("meta", {}).get("modo", "") or "").upper()
        template_name = "finiquito" if modo == "FINIQUITO" else "periodica"

        return self.template_manager.render_template(template_name, context)

    def save_markdown(self, markdown_content: str, file_path: str) -> bool:
        """Guarda el contenido Markdown a disco.

        Args:
            markdown_content: Contenido a guardar.
            file_path: Ruta destino.

        Returns:
            True si se escribió correctamente, False si ocurrió error.
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            return True
        except OSError:
            return False

    # ------------------------------------------------------------------
    # Construcción del contexto del template
    # ------------------------------------------------------------------

    def _build_context(
        self, data: Dict[str, Any], status: str
    ) -> Dict[str, Any]:
        """Construye el contexto que el template Jinja2 recibe.

        Soporta dos formas de ``desglose``:

        1. **Segmentado (v2.0, JSONGenerator):**
           ``{"2025": {"cesantias": ..., ...}, "2026": {...}}``
           → se agregan los totales por año y se construye una tabla de
           desglose por segmento.

        2. **Plano (legacy, tests Fase 0):**
           ``{"cesantias": {"valor": ..., ...}, ...}``
           → se leen los valores directamente.
        """
        meta = data.get("meta", {})
        trabajador = data.get("trabajador", {})
        contrato = data.get("contrato", {})
        desglose = data.get("desglose", {})

        modo = (meta.get("modo", "PERIODICA") or "PERIODICA").upper()

        # Detectar si desglose es segmentado (claves numéricas de año)
        segmented, flat_desglose = self._normalize_desglose(desglose)

        # Extraer valores planos (compat con templates existentes)
        ces = flat_desglose.get("cesantias", {})
        ints = flat_desglose.get("intereses_cesantias", {})
        pri = flat_desglose.get("prima", {})
        vac = flat_desglose.get("vacaciones", {})
        indem = flat_desglose.get("indemnizacion", {})
        sal_pend = flat_desglose.get("salario_pendiente", {})

        # Total: usar total_liquidacion del top-level, o sumar
        total = data.get("total_liquidacion", 0)

        # Fechas: del contrato (JSONGenerator) o del meta (legacy)
        fecha_ingreso = (
            contrato.get("fecha_ingreso")
            or meta.get("fecha_ingreso")
            or ""
        )
        fecha_corte = (
            contrato.get("fecha_corte")
            or meta.get("fecha_corte")
            or ""
        )
        # Año para el título
        anio = ""
        if fecha_corte and len(str(fecha_corte)) >= 4:
            anio = str(fecha_corte)[:4]

        context = {
            "año": anio,
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "modo": modo,
            "fecha_ingreso": self._fmt_date(fecha_ingreso),
            "fecha_corte": self._fmt_date(fecha_corte),
            "nombre": trabajador.get("nombre", "[ANONIMIZADO]"),
            "documento": trabajador.get("documento", "-"),
            "tipo_contrato": (contrato.get("tipo") or "").lower(),
            "reside_en_lugar": (
                trabajador.get("reside_en_lugar_trabajo")
                or trabajador.get("reside_en_lugar")
                or False
            ),
            "cesantias": ces.get("valor", 0),
            "dias_ces": ces.get("dias_liquidados", 0),
            "plazo_ces": ces.get("plazo_pago_legal", "—"),
            "norma_ces": ces.get("norma", "—"),
            "intereses": ints.get("valor", 0),
            "dias_int": ints.get("dias_liquidados", 0),
            "plazo_int": ints.get("plazo_pago_legal", "—"),
            "norma_int": ints.get("norma", "—"),
            "prima": pri.get("valor", 0),
            "dias_prima": pri.get("dias_liquidados", 0),
            "plazo_prima": pri.get("plazo_pago_legal", "—"),
            "norma_prima": pri.get("norma", "—"),
            "vacaciones": vac.get("valor", 0),
            "dias_vac": vac.get("dias_liquidados", 0),
            "norma_vac": vac.get("norma", "—"),
            "total": total,
            "observaciones": self._format_observaciones(
                data.get("validaciones_y_alertas") or {}
            ),
            "plazos_detallados": self._format_plazos(flat_desglose, modo),
            "declaracion": self._get_declaracion(modo),
            "desglose_segmentado": self._format_desglose_segmentado(segmented),
        }

        # Campos exclusivos de FINIQUITO
        if modo == "FINIQUITO":
            context.update(
                {
                    "indemnizacion": indem.get("valor", 0),
                    "dias_indem": indem.get("dias_liquidados", 0),
                    "norma_indem": indem.get("norma", "—"),
                    "salario_pendiente": sal_pend.get("valor", 0),
                    "dias_salario_pend": sal_pend.get(
                        "dias_liquidados", 0
                    ),
                    "norma_salario": sal_pend.get("norma", "—"),
                }
            )

        # Pasar compliance status para advertencias condicionales
        context["compliance_status"] = status

        return context

    # ------------------------------------------------------------------
    # Normalización y validación del desglose
    # ------------------------------------------------------------------

    def _normalize_desglose(
        self, desglose: Dict[str, Any]
    ) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        """Normaliza el desglose a dos representaciones.

        Returns:
            Tuple de (segmented, flat):
            - ``segmented``: dict {año: {concepto: valor, ...}} para
              la tabla de desglose por segmento.
            - ``flat``: dict {concepto: {valor, dias_liquidados, ...}}
              para compatibilidad con los templates existentes.
        """
        flat: Dict[str, Dict[str, Any]] = {}
        segmented: Dict[str, Dict[str, Any]] = {}

        if not desglose:
            return segmented, flat

        # Detectar si es segmentado: claves que parecen años (4 dígitos)
        year_keys = [k for k in desglose if isinstance(k, str) and k.isdigit() and len(k) == 4]

        if year_keys:
            # Forma segmentada: {"2025": {...}, "2026": {...}}
            segmented = {
                y: dict(desglose[y]) for y in sorted(year_keys) if isinstance(desglose[y], dict)
            }
            # Construir flat agregando a través de los años
            flat = self._aggregate_segments(segmented)
        else:
            # Forma plana legacy: {"cesantias": {...}, ...}
            for concept, data in desglose.items():
                if isinstance(data, dict) and "valor" in data:
                    flat[concept] = dict(data)

        return segmented, flat

    @staticmethod
    def _aggregate_segments(
        segmented: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Agrega valores a través de segmentos anuales.

        Cada segmento tiene la forma ``{concepto: valor_numérico, ...}``
        (valores escalares, como en ``sample_calc_results`` del test de
        JSONGenerator). Se suman los valores de cada concepto y se crea
        un flat con ``{"valor": suma, "dias_liquidados": suma_dias, ...}``.
        """
        flat: Dict[str, Dict[str, Any]] = {}
        if not segmented:
            return flat

        # Recorrer segmentos y sumar
        accum: Dict[str, float] = {}
        for year_data in segmented.values():
            for concept, value in year_data.items():
                if value is None:
                    continue
                try:
                    accum[concept] = accum.get(concept, 0) + float(value)
                except (TypeError, ValueError):
                    accum[concept] = accum.get(concept, 0)

        for concept, total in accum.items():
            flat[concept] = {
                "valor": total,
                "dias_liquidados": 0,
                "plazo_pago_legal": "—",
                "norma": "—",
            }

        return flat

    # ------------------------------------------------------------------
    # Gestión de estado de compliance
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_status(
        data: Dict[str, Any], explicit: Optional[str]
    ) -> str:
        """Resuelve el compliance status efectivo.

        Prioridad: parámetro explícito > ``meta.compliance_status`` >
        default ``"GO"``.
        """
        if explicit is not None:
            return explicit.upper()
        raw = (
            data.get("meta", {})
            .get("compliance_status")
            or data.get("compliance", {})
            .get("status")
            or "GO"
        )
        return str(raw).upper()

    # ------------------------------------------------------------------
    # Validación del contexto
    # ------------------------------------------------------------------

    def _validate_context(self, data: Dict[str, Any]) -> List[str]:
        """Valida que ``data`` contenga las claves mínimas para renderizar.

        Returns:
            Lista de descripciones de campos faltantes. Vacía si OK.
        """
        issues: List[str] = []
        meta = data.get("meta")
        if not isinstance(meta, dict):
            issues.append("meta (faltante o no es dict)")
        desglose = data.get("desglose")
        if not isinstance(desglose, dict):
            issues.append("desglose (faltante o no es dict)")
        trabajador = data.get("trabajador")
        if not isinstance(trabajador, dict):
            issues.append("trabajador (faltante o no es dict)")
        return issues

    # ------------------------------------------------------------------
    # Renderizado de estados especiales
    # ------------------------------------------------------------------

    def _render_blocked(self, data: Dict[str, Any]) -> str:
        """Renderiza plantilla de bloqueo para NO_GO.

        NO incluye datos del trabajador (sanitización PII implícita).
        """
        meta = data.get("meta", {})
        compliance = data.get("compliance_report", {})
        failures = compliance.get("blocking_failures", [])
        summary = compliance.get("summary", {})

        lines = [
            "# LIQUIDACIÓN BLOQUEADA",
            "",
            "**Estado:** NO_GO — La liquidación no puede generarse porque "
            "una o más validaciones críticas de compliance no se superaron.",
            "",
            f"**Fecha de intento:** {meta.get('fecha_generacion', '—')}",
            f"**Versión del motor:** {meta.get('motor_version', '—')}",
            "",
            "## Fallos bloqueantes",
            "",
        ]

        if failures:
            for i, f in enumerate(failures, 1):
                if isinstance(f, dict):
                    lines.append(
                        f"{i}. **{f.get('code', '?')}** — "
                        f"{f.get('message', 'Sin descripción')}"
                    )
                else:
                    lines.append(f"{i}. {f}")
        else:
            lines.append("No se registraron fallos detallados.")

        lines.extend(
            [
                "",
                "## Resumen de compliance",
                "",
                f"- Pasadas: {summary.get('passed', '—')}",
                f"- Advertencias: {summary.get('warnings', '—')}",
                f"- Fallos: {summary.get('failures', '—')}",
                "",
                "---",
                "",
                "*Esta liquidación ha sido bloqueada por el motor de "
                "compliance. Corrija los fallos listados arriba y "
                "re-ejecute el motor.*",
            ]
        )

        return "\n".join(lines)

    def _render_context_error(self, missing: List[str]) -> str:
        """Renderiza error de contexto faltante (sin PII)."""
        return (
            "# ERROR DE CONTEXTO\n\n"
            "No se puede generar el documento porque faltan campos "
            "obligatorios en los datos de entrada:\n\n"
            + "\n".join(f"- {m}" for m in missing)
            + "\n\n*Verifique que el JSONGenerator esté produciendo la "
            "forma ``LiquidacionResult`` correcta.*"
        )

    # ------------------------------------------------------------------
    # Formateo del desglose segmentado (para template)
    # ------------------------------------------------------------------

    def _format_desglose_segmentado(
        self, segmented: Dict[str, Dict[str, Any]]
    ) -> str:
        """Formatea el desglose por año como tabla Markdown.

        Si no hay segmentos, retorna cadena vacía (el template no
        renderiza la sección).
        """
        if not segmented:
            return ""

        # Recoger todos los conceptos únicos a través de los años
        all_concepts: List[str] = []
        seen = set()
        for year_data in segmented.values():
            for concept in year_data:
                if concept not in seen:
                    all_concepts.append(concept)
                    seen.add(concept)

        # Cabecera
        anios_sorted = sorted(segmented.keys())
        header = "| Concepto | " + " | ".join(anios_sorted) + " | Total |"
        sep = "|----------|" + "|".join("---------:" for _ in anios_sorted) + "|------:|"
        rows: List[str] = [header, sep]

        for concept in all_concepts:
            vals = []
            total = 0
            for anio in anios_sorted:
                v = segmented[anio].get(concept, 0)
                if v is None:
                    vals.append("—")
                else:
                    vals.append(self._fmt_currency(v))
                    try:
                        total += float(v)
                    except (TypeError, ValueError):
                        pass
            row = (
                f"| {concept.replace('_', ' ').title()} "
                + "".join(f"| {v} " for v in vals)
                + f"| {self._fmt_currency(total)} |"
            )
            rows.append(row)

        # Total general
        total_fila = (
            "| **Total por año** "
            + "".join(
                f"| {self._fmt_currency(sum(v for v in segmented[anio].values() if v is not None))} "
                for anio in anios_sorted
            )
            + "| |"
        )
        rows.append(total_fila)

        return "\n".join(
            [
                "### DESGLOSE POR SEGMENTO (AÑO CALENDARIO)",
                "",
                *rows,
            ]
        )

    # ------------------------------------------------------------------
    # Helpers de formato (heredados del refactor previo, mejorados)
    # ------------------------------------------------------------------

    def _format_observaciones(
        self, validaciones: Dict[str, str]
    ) -> str:
        """Formatea validaciones como lista Markdown."""
        if not validaciones:
            return "Ninguna observación."
        return "\n".join(f"- {v}" for v in validaciones.values())

    def _format_plazos(
        self, desglose: Dict[str, Dict[str, Any]], modo: str
    ) -> str:
        """Formatea plazos de pago como lista Markdown."""
        items: List[str] = []

        ces = desglose.get("cesantias", {})
        ints = desglose.get("intereses_cesantias", {})
        pri = desglose.get("prima", {})
        indem = desglose.get("indemnizacion", {})
        sal_pend = desglose.get("salario_pendiente", {})

        if ces:
            items.append(
                f"- Cesantías: {ces.get('plazo_pago_legal', '—')} "
                f"({ces.get('norma', '—')})"
            )
        if ints:
            items.append(
                f"- Intereses sobre cesantías: "
                f"{ints.get('plazo_pago_legal', '—')} "
                f"({ints.get('norma', '—')})"
            )
        if pri:
            items.append(
                f"- Prima de servicios: "
                f"{pri.get('plazo_pago_legal', '—')} "
                f"({pri.get('norma', '—')})"
            )
        if modo == "FINIQUITO":
            items.append(
                f"- Indemnización: Pago inmediato "
                f"({indem.get('norma', '—')})"
            )
            items.append(
                f"- Salario pendiente: Pago inmediato "
                f"({sal_pend.get('norma', '—')})"
            )

        return "\n".join(items) if items else "No se encontraron plazos."

    @staticmethod
    def _get_declaracion(modo: str) -> str:
        """Declaración legal según modo de liquidación."""
        if modo == "PERIODICA" or modo == "PERIÓDICA":
            return (
                "El empleador declara que los valores aquí liquidados "
                "corresponden a las prestaciones sociales causadas en "
                "el período indicado, conforme a la normatividad laboral "
                "colombiana. Las cesantías serán consignadas en el fondo "
                "de pensiones seleccionado por el trabajador dentro de "
                "los plazos legales establecidos."
            )
        return (
            "El empleador declara que los valores aquí liquidados "
            "corresponden a la totalidad de las prestaciones sociales e "
            "indemnizaciones causadas por terminación del contrato, "
            "conforme a la normatividad laboral colombiana. El "
            "trabajador declara haber recibido el pago total de los "
            "conceptos liquidados en este documento."
        )

    @staticmethod
    def _fmt_date(raw: Any) -> str:
        """Formatea fecha como YYYY-MM-DD o retorna el string tal cual."""
        s = str(raw).strip() if raw else ""
        # Si ya es ISO-like, devolver tal cual
        if len(s) >= 10 and s[4] == "-" and s[7] == "-":
            return s[:10]
        return s

    @staticmethod
    def _fmt_currency(value: Any) -> str:
        """Formatea número como moneda colombiana ($1.234.567)."""
        try:
            n = int(float(value))
        except (TypeError, ValueError):
            return str(value)
        return f"${n:,}".replace(",", ".")


__all__ = ["MarkdownGenerator"]
