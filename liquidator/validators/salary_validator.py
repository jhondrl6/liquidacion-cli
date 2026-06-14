from __future__ import annotations

from liquidator.utils import SalaryError

REQUIRED_NUMERIC = [
    "salario_mensual",
]

OPTIONAL_NUMERIC_DEFAULTS = {
    "comisiones_promedio_mensual": 0.0,
    "horas_extras_promedio_mensual": 0.0,
    "bonificaciones_promedio_mensual": 0.0,
    "auxilio_conectividad": 0.0,
}


def _ensure_numeric_nonnegative(name: str, value) -> None:
    if isinstance(value, (int, float)):
        if value < 0:
            raise SalaryError(f"{name} no puede ser negativo.")
        return
    raise SalaryError(f"{name} debe ser numérico.")


def validate_salary_components(input_data: dict, params: dict) -> list[str]:
    """Valida montos salariales y reglas de auxilios. Retorna advertencias."""
    warnings: list[str] = []

    for field in REQUIRED_NUMERIC:
        if field not in input_data:
            raise SalaryError(f"Campo requerido ausente: {field}.")
        _ensure_numeric_nonnegative(field, input_data[field])

    for field, default in OPTIONAL_NUMERIC_DEFAULTS.items():
        if field in input_data:
            _ensure_numeric_nonnegative(field, input_data[field])
        else:
            input_data[field] = default

    # Validación de límite 2 SMMLV para auxilios de transporte (si aplica)
    smmlv = params.get("SMMLV")
    limite_aux = params.get("LIMITE_AUXILIO")

    if isinstance(smmlv, (int, float)) and isinstance(limite_aux, (int, float)):
        # Regla: si salario supera el límite,
        # advertir sobre no elegibilidad de auxilio de transporte.
        salario_mensual = input_data.get("salario_mensual", 0)
        if salario_mensual > limite_aux:
            warnings.append(
                "Salario supera límite de 2 SMMLV para auxilio de transporte "
                "(no elegible)."
            )

    # Regla de residencia en lugar de trabajo
    if bool(input_data.get("reside_en_lugar_trabajo", False)):
        warnings.append(
            "Auxilio de transporte excluido por residencia en lugar "
            "de trabajo (finca)."
        )

    # Nota sobre auxilio de transporte
    if input_data.get("auxilio_conectividad", 0) > 0:
        warnings.append(
            "Verificar si el auxilio de transporte está pactado "
            "como salario habitual."
        )

    return warnings
