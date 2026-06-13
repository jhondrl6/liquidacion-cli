from liquidator.validators import validate_salary_components


def test_validate_salary_components_ok_and_warnings():
    params = {"SMMLV": 1423500, "LIMITE_AUXILIO": 2 * 1423500}
    input_data = {
        "salario_mensual": 3000000,
        "reside_en_lugar_trabajo": True,
        "auxilio_conectividad": 50000,
    }
    warnings = validate_salary_components(input_data, params)
    assert any("límite" in w.lower() or "limite" in w.lower() for w in warnings)
    assert any("transporte excluido" in w.lower() for w in warnings)
