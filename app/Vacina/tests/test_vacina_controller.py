"""Testes unitários para o controlador de Vacina."""

from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from app.Vacina.controller import VacinaController
from app.Vacina.model import Vacina


class TestVacinaController:
    """Testes unitários do VacinaController."""

    def test_listar_todas_vazio(self):
        """Deve retornar lista vazia quando não há vacinas."""
        db_mock = Mock()
        db_mock.query.return_value.all.return_value = []

        resultado = VacinaController.listar_todas(db_mock)

        assert resultado == []
        assert isinstance(resultado, list)

    def test_listar_todas_com_dados(self):
        """Deve retornar todas as vacinas cadastradas."""
        db_mock = Mock()
        vacinas_mock = [
            Vacina(id=1, nome="BCG", doses=1),
            Vacina(id=2, nome="Hepatite B", doses=3),
            Vacina(id=3, nome="COVID-19", doses=2)
        ]
        db_mock.query.return_value.all.return_value = vacinas_mock

        resultado = VacinaController.listar_todas(db_mock)

        assert len(resultado) == 3
        assert resultado[0].nome == "BCG"

    def test_buscar_por_id_encontrada(self):
        """Deve retornar vacina quando ID existe."""
        db_mock = Mock()
        vacina_mock = Vacina(id=1, nome="BCG", doses=1)
        db_mock.query.return_value.filter.return_value.first.return_value = vacina_mock

        resultado = VacinaController.buscar_por_id(db_mock, 1)

        assert resultado is not None
        assert resultado.nome == "BCG"

    def test_buscar_por_id_nao_encontrada(self):
        """Deve retornar None quando ID não existe."""
        db_mock = Mock()
        db_mock.query.return_value.filter.return_value.first.return_value = None

        resultado = VacinaController.buscar_por_id(db_mock, 999)

        assert resultado is None

    def test_buscar_por_nome_encontrada(self):
        """Deve retornar vacina quando nome existe."""
        db_mock = Mock()
        vacina_mock = Vacina(id=1, nome="BCG", doses=1)
        db_mock.query.return_value.filter.return_value.first.return_value = vacina_mock

        resultado = VacinaController.buscar_por_nome(db_mock, "BCG")

        assert resultado is not None
        assert resultado.nome == "BCG"

    def test_criar_vacina_sucesso(self):
        """Deve criar vacina com sucesso."""
        db_mock = Mock()
        db_mock.query.return_value.filter.return_value.first.return_value = None

        resultado = VacinaController.criar(db_mock, "COVID-19", 2)

        assert resultado.nome == "COVID-19"
        assert resultado.doses == 2
        db_mock.add.assert_called_once()
        db_mock.commit.assert_called_once()

    def test_criar_vacina_duplicada(self):
        """Deve lançar exceção ao criar vacina com nome duplicado."""
        db_mock = Mock()
        vacina_existente = Vacina(id=1, nome="BCG", doses=1)
        db_mock.query.return_value.filter.return_value.first.return_value = vacina_existente

        with pytest.raises(HTTPException) as exc_info:
            VacinaController.criar(db_mock, "BCG", 1)

        assert exc_info.value.status_code == 400
        assert "já existe" in exc_info.value.detail

    def test_criar_vacina_nome_vazio(self):
        """Deve lançar exceção ao criar vacina com nome vazio."""
        db_mock = Mock()

        with pytest.raises(HTTPException) as exc_info:
            VacinaController.criar(db_mock, "", 1)

        assert exc_info.value.status_code == 400

    def test_atualizar_vacina_sucesso(self):
        """Deve atualizar vacina com sucesso."""
        db_mock = Mock()
        vacina_mock = Vacina(id=1, nome="BCG", doses=1)
        db_mock.query.return_value.filter.return_value.first.return_value = vacina_mock

        resultado = VacinaController.atualizar(
            db_mock, 1, nome="BCG Atualizada", doses=2
        )

        assert resultado.nome == "BCG Atualizada"
        assert resultado.doses == 2

    def test_atualizar_vacina_nao_encontrada(self):
        """Deve lançar exceção ao atualizar vacina inexistente."""
        db_mock = Mock()
        db_mock.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            VacinaController.atualizar(db_mock, 999, nome="Teste")

        assert exc_info.value.status_code == 404

    def test_deletar_vacina_sucesso(self):
        """Deve deletar vacina com sucesso."""
        db_mock = Mock()
        vacina_mock = Vacina(id=1, nome="BCG", doses=1)
        db_mock.query.return_value.filter.return_value.first.return_value = vacina_mock

        resultado = VacinaController.deletar(db_mock, 1)

        assert resultado is True
        db_mock.delete.assert_called_once()

    def test_deletar_vacina_nao_encontrada(self):
        """Deve lançar exceção ao deletar vacina inexistente."""
        db_mock = Mock()
        db_mock.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            VacinaController.deletar(db_mock, 999)

        assert exc_info.value.status_code == 404

    def test_buscar_por_doses(self):
        """Deve buscar vacinas por número de doses."""
        db_mock = Mock()
        vacinas_mock = [
            Vacina(id=1, nome="BCG", doses=1),
            Vacina(id=4, nome="Febre Amarela", doses=1)
        ]
        db_mock.query.return_value.filter.return_value.all.return_value = vacinas_mock

        resultado = VacinaController.buscar_por_doses(db_mock, 1)

        assert len(resultado) == 2
        assert all(v.doses == 1 for v in resultado)

    @pytest.mark.parametrize("nome,doses,valido", [
        ("BCG", 1, True),
        ("Hepatite B", 3, True),
        ("COVID-19", 2, True),
        ("Tríplice Viral", 10, True),
        ("", 1, False),
        ("BCG", 0, False),
        ("BCG", 11, False),
    ])
    def test_criar_vacina_parametrizado(self, nome, doses, valido):
        """Testa criação com múltiplos casos."""
        db_mock = Mock()
        if valido:
            db_mock.query.return_value.filter.return_value.first.return_value = None
            resultado = VacinaController.criar(db_mock, nome, doses)
            assert resultado.nome == nome or resultado.nome == nome.strip()
        else:
            with pytest.raises(HTTPException):
                VacinaController.criar(db_mock, nome, doses)
