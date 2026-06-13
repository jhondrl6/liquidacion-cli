from liquidator.legal import TopesManager


def build_manager() -> TopesManager:
    params = {
        "SMMLV": 1423500,
        "LIMITE_AUXILIO": 2847000,
        "TOPE_INDEMNIZACION_SMMLV": 20,
    }
    return TopesManager(params)


def test_aplica_auxilio_transporte_dentro_del_limite():
    manager = build_manager()
    assert manager.aplica_auxilio_transporte(2000000)


def test_aplica_auxilio_transporte_fuera_del_limite():
    manager = build_manager()
    assert not manager.aplica_auxilio_transporte(3000000)


def test_aplicar_tope_indemnizacion():
    manager = build_manager()
    valor = manager.aplicar_tope_indemnizacion(50 * manager.smmlv)
    assert valor == 20 * manager.smmlv
