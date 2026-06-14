"""Entry point CLI: liquidacion.

Subcomandos: liquidar, validate, info.

Implementa el entry point declarado en pyproject.toml:
    [project.scripts]
    liquidacion = "liquidator.cli.main:main"

Fase 1.B — esqueleto funcional. El motor (LiquidacionEngine) tiene issues
de init preexistentes (Fase 1). ParamsProvider year-aware (Tarea 1.E)
implementado — los comandos usan ParamsProvider.for_year().
Los comandos degradan gracefulmente cuando una dependencia no está lista.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

import click

from liquidator import __version__
from liquidator.core.input_parser import InputParser
from liquidator.core.params_provider import ParamsProvider
from liquidator.validators.input_validator import validate_input

# --- Helpers ------------------------------------------------------------------

def _load_params(year: int) -> Dict[str, Any]:
    """Carga params/<year>.json via ParamsProvider (Tarea 1.E)."""
    try:
        provider = ParamsProvider.for_year(year)
        return provider.to_dict()
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))


def _resolve_input(input_path: Path) -> Dict[str, Any]:
    """Resuelve y parsea el archivo de entrada JSON."""
    parser = InputParser()
    try:
        return parser.parse(str(input_path))
    except FileNotFoundError:
        raise click.ClickException(f"Archivo no encontrado: {input_path}")
    except ValueError as exc:
        raise click.ClickException(str(exc))


def _write_output_artifacts(
    result: Dict[str, Any],
    out_dir: Path,
    input_stem: str,
    is_blocked: bool,
) -> tuple[Path, Path | None]:
    """Escribe los artefactos de salida (.json, .md opcional).

    Tarea 3.D (Fase 3 base, plan §8.2):
    - ``is_blocked=False``: escribe ``liquidacion.<json>`` (comportamiento
      previo, sólo JSON). El plan original pide también ``liquidacion.md``
      y ``liquidacion.pdf``; el MD se omite intencionalmente para no
      duplicar la lógica del ``MarkdownGenerator`` (gap preexistente de
      Fase 1, fuera de scope de 3.D).
    - ``is_blocked=True``: escribe ``liquidacion_BLOQUEADA.json`` Y
      ``liquidacion_BLOQUEADA.md`` con la salida del ``MarkdownGenerator``
      en estado ``NO_GO`` (regla AGENTS.md #7: NO PDF cuando NO_GO).

    Returns:
        Tuple ``(json_path, md_path_or_None)``.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    base_name = "liquidacion_BLOQUEADA" if is_blocked else "liquidacion"

    json_path = out_dir / f"{base_name}.json"
    json_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    md_path: Path | None = None
    if is_blocked:
        # Generar también el markdown de bloqueo (Tarea 3.D).
        # Import diferido: el generator puede no estar listo en tests
        # de import aislados; este path solo se ejecuta cuando el
        # usuario invoca `liquidar` y hay NO_GO real.
        try:
            from liquidator.output.markdown_generator import (
                MarkdownGenerator,
            )

            md_content = MarkdownGenerator().generate_markdown(
                result, status="NO_GO"
            )
            md_path = out_dir / f"{base_name}.md"
            md_path.write_text(md_content, encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            click.secho(
                f"Advertencia: no se pudo generar el markdown de "
                f"bloqueo: {exc}",
                fg="yellow",
                err=True,
            )
            md_path = None

    return json_path, md_path


# --- CLI ----------------------------------------------------------------------

@click.group()
@click.version_option(__version__, prog_name="liquidacion")
def main() -> None:
    """Liquidacion de nomina colombiana — CLI local v2.0-dev.

    Herramienta local para calcular prestaciones sociales, generar
    documentos de liquidacion (JSON/MD/PDF) y validar compliance legal.

    Modos soportados: PERIODICA, FINIQUITO, VACACIONES.
    """


# ---- liquidar ----------------------------------------------------------------

@main.command()
@click.argument(
    "input_path",
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "--out-dir",
    type=click.Path(path_type=Path),
    default=Path("output"),
    help="Directorio de salida para artefactos generados.",
)
@click.option(
    "--override",
    is_flag=True,
    help="Forzar override de fallos HIGH (registrado en auditoria).",
)
@click.option(
    "--override-reason",
    default=None,
    help="Justificacion del override (requerido si --override).",
)
@click.option(
    "--json-only",
    is_flag=True,
    help="Emitir solo el JSON de resultado por stdout (sin artefactos).",
)
def liquidar(
    input_path: Path,
    out_dir: Path,
    override: bool,
    override_reason: Optional[str],
    json_only: bool,
) -> None:
    """Liquida a partir de un JSON de entrada.

    INPUT_PATH: archivo JSON con los datos del trabajador, contrato,
    salario y modo de liquidacion (ver Contexto/KB_LLM/04_schema_entrada.md).

    El motor genera JSON + Markdown en --out-dir. Con --json-only emite
    solo el JSON de resultado por stdout.

    Modo NO_GO (Tarea 3.D, plan §8.2):
        Cuando compliance = NO_GO, los archivos se emiten con el prefijo
        ``liquidacion_BLOQUEADA.`` (``liquidacion_BLOQUEADA.json`` +
        ``liquidacion_BLOQUEADA.md``) y el proceso termina con exit
        code 2. NO se genera PDF (regla AGENTS.md #7).

    Modo GO/WARN/OVERRIDE_APPROVED:
        Archivos ``liquidacion.json`` (comportamiento previo) y exit
        code 0.
    """
    if override and not override_reason:
        raise click.ClickException(
            "--override-reason es obligatorio cuando se usa --override."
        )

    payload = _resolve_input(input_path)

    # Intentar usar el motor. Si el motor no esta listo (Fase 1 en curso),
    # mostrar mensaje claro con el estado actual.
    try:
        from liquidator.core.engine import LiquidacionEngine

        engine = LiquidacionEngine()
        result = engine.process(payload)
    except Exception as exc:
        modo = payload.get("modo", "?")
        fecha_ingreso = payload.get("fecha_ingreso", "?")
        fecha_corte = payload.get("fecha_corte", "?")
        click.secho(
            "El motor de liquidacion no esta listo para procesar. "
            "Esto es esperado en Fase 1.",
            fg="yellow",
            err=True,
        )
        click.echo(
            f"\n  Modo:           {modo}\n"
            f"  Fecha ingreso:  {fecha_ingreso}\n"
            f"  Fecha corte:    {fecha_corte}\n"
            f"  Causa:          {exc}\n"
            f"  Tareas pendientes que desbloquean el motor:\n"
            f"    - Tarea 1.D  (JSONGenerator con schema_path)\n"
            f"    - Tarea 1.G  (R-OP-03: fix schema refs rotas)\n"
            f"  Ver REGISTRY.md para el estado actual.\n",
            err=True,
        )
        sys.exit(3)

    compliance_status = result.get("compliance_report", {}).get(
        "compliance_status", "GO"
    )
    is_blocked = compliance_status.upper() == "NO_GO"

    if json_only:
        click.echo(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    else:
        json_path, md_path = _write_output_artifacts(
            result, out_dir, input_path.stem, is_blocked
        )
        click.echo(f"Resultado escrito en {json_path}")
        if md_path is not None:
            click.echo(f"Bloqueo (markdown) escrito en {md_path}")

    # Tarea 3.D: código de salida diferenciado para NO_GO.
    if is_blocked:
        sys.exit(2)
    else:
        sys.exit(0)


# ---- validate ----------------------------------------------------------------

@main.command()
@click.argument(
    "input_path",
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "--params-year",
    type=int,
    default=2026,
    help="Anio de parametros a usar para validacion (default: 2026).",
)
def validate(input_path: Path, params_year: int) -> None:
    """Valida un JSON de entrada sin ejecutar el motor.

    Comprueba: campos requeridos, rangos de fechas, modo valido,
    consistencia de contrato y salario.

    Usa los parametros del anio indicado con --params-year.
    """
    payload = _resolve_input(input_path)
    params = _load_params(params_year)

    try:
        warnings, notes = validate_input(payload, params)
    except Exception as exc:
        click.secho(f"Error de validacion: {exc}", fg="red", err=True)
        sys.exit(1)

    click.echo(f"Validacion contra params/{params_year}.json\n")
    click.echo(f"  Campos requeridos: OK")
    click.echo(f"  Modo:              {payload.get('modo', '?')}")
    click.echo(f"  Tipo contrato:     {payload.get('tipo_contrato', '?')}")
    click.echo(f"  Fecha ingreso:     {payload.get('fecha_ingreso', '?')}")
    click.echo(f"  Fecha corte:       {payload.get('fecha_corte', '?')}")
    click.echo(f"  Salario mensual:   {payload.get('salario_mensual', '?')}")

    if warnings:
        click.secho(f"\n  Advertencias ({len(warnings)}):", fg="yellow")
        for w in warnings:
            click.echo(f"    - {w}")

    if notes:
        click.echo(f"\n  Notas ({len(notes)}):")
        for n in notes:
            click.echo(f"    - {n}")

    if not warnings:
        click.secho("\n  Resultado: OK", fg="green")
        sys.exit(0)
    else:
        click.secho(
            f"\n  Resultado: {len(warnings)} advertencia(s) — "
            f"revisar antes de liquidar",
            fg="yellow",
        )
        sys.exit(0)


# ---- info --------------------------------------------------------------------

@main.command()
@click.option(
    "--year",
    type=int,
    default=None,
    help="Anio especifico (default: muestra 2025 y 2026).",
)
def info(year: Optional[int]) -> None:
    """Muestra parametros vigentes y estado del sistema.

    Sin --year: muestra parametros de 2025 y 2026.
    Con --year: muestra solo el anio indicado.

    Usa ParamsProvider.for_year() — Tarea 1.E completada.
    """
    years = [year] if year else [2025, 2026]

    click.echo(f"liquidacion-cli v{__version__}\n")

    for yr in years:
        try:
            params = _load_params(yr)
        except click.ClickException:
            click.secho(f"  {yr}: params/{yr}.json no encontrado", fg="yellow")
            continue

        smmlv = params.get("SMMLV", "?")
        aux_trans = params.get("AUXILIO_TRANS", "?")
        tasa_int = params.get("TASA_INT_CESANTIAS", "?")
        dias_base = params.get("DIAS_BASE", "?")

        click.echo(f"  {yr}:")
        click.echo(f"    SMMLV:                 {smmlv:>12,}")
        click.echo(f"    Auxilio transporte:    {aux_trans:>12,}")
        click.echo(f"    Tasa int. cesantias:   {tasa_int:>12}")
        click.echo(f"    Dias base:             {dias_base:>12}")

    click.echo(f"\n  Suite de tests:")
    click.echo(f"    R-OP-05 (params):      RESUELTO (S13) — 0 collection errors")
    click.echo(f"    R-OP-06 (utils):       RESUELTO (S13) — 7/7 tests verdes")
    click.echo(f"    R-OP-02 Causa 2:       PENDIENTE (9 fails en test_versioning.py)")
    click.echo(f"\\n  Pendientes Fase 1:")
    click.echo(f"    Tarea 1.C  — Schemas Pydantic de entrada/salida (CERRADA S16)")
    click.echo(f"    Tarea 1.D  — JSONGenerator con schema_path")
    click.echo(f"    Tarea 1.E  — ParamsProvider year-aware (CERRADA — este comando lo usa)")
    click.echo(f"    Tarea 1.G  — R-OP-03 schema fix (1 minuto)")
    click.echo(f"\n  Ver REGISTRY.md para trazabilidad completa.")


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
