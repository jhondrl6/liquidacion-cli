import pytest

from liquidator.legal import NormaNotFoundError, NormasRepository


def test_normas_repository_loads_defaults():
    repo = NormasRepository()
    normas = repo.list_normas()
    assert normas, "El repositorio debe cargar normas desde params/normas.json"


def test_normas_repository_get_existing_norm():
    repo = NormasRepository()
    norma = repo.get_norma("CST_249_252")
    assert "Cesantías" in norma.descripcion
    assert norma.url


def test_normas_repository_missing_norm_raises():
    repo = NormasRepository()
    with pytest.raises(NormaNotFoundError):
        repo.get_norma("NO_EXISTE")


def test_normas_repository_search_by_keyword():
    repo = NormasRepository()
    results = repo.search("prima")
    assert any(norma.id == "CST_306_308" for norma in results)


def test_normas_repository_get_plazo_definition():
    repo = NormasRepository()
    plazo = repo.get_plazo_definicion("cesantias")
    assert plazo["norma_ref"] == "CST_249_252"
