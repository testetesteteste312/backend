"""Testes unitários para o modelo de Vacina."""

import pytest
from app.Vacina.model import Vacina


class TestVacinaModel:
    """Testes para o modelo Vacina."""

    def test_criacao_vacina(self):
        """Deve criar uma instância válida de Vacina."""
        vacina = Vacina(id=1, nome="BCG", doses=1)
        assert vacina.id == 1
        assert vacina.nome == "BCG"
        assert vacina.doses == 1

    def test_to_dict(self):
        """Deve converter corretamente o objeto Vacina para dicionário."""
        vacina = Vacina(id=1, nome="Hepatite B", doses=3)
        vacina_dict = vacina.to_dict()
        assert vacina_dict == {
            "id": 1,
            "nome": "Hepatite B",
            "doses": 3
        }

    def test_repr(self):
        """Deve retornar a representação legível da Vacina."""
        vacina = Vacina(id=10, nome="COVID-19", doses=2)
        repr_str = repr(vacina)
        assert "Vacina" in repr_str
        assert "COVID-19" in repr_str
        assert "2" in repr_str

    @pytest.mark.parametrize("nome,doses", [
        ("Tétano", 3),
        ("Raiva", 5),
        ("Gripe", 1),
    ])
    def test_criacao_parametrizada(self, nome, doses):
        """Testa várias instâncias válidas de Vacina."""
        vacina = Vacina(nome=nome, doses=doses)
        assert vacina.nome == nome
        assert vacina.doses == doses
