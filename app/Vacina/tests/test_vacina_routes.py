"""Testes para as rotas de Vacina."""

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app
from app.Vacina.model import Vacina

# Cria um cliente de teste para a aplicação
client = TestClient(app)

class TestVacinaRoutes:
    """Testes para as rotas de Vacina."""
    @patch('app.Vacina.routes.VacinaController.listar_todas')
    @patch('app.Vacina.routes.get_db')
    def test_listar_vacinas_vazio(self, mock_get_db, mock_listar):
        """Deve retornar lista vazia quando não há vacinas."""
        # Configura os mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_listar.return_value = []

        # Executa a requisição
        response = client.get("/vacinas/")

        # Verifica a resposta
        assert response.status_code == 200
        assert response.json() == []

    @patch('app.Vacina.routes.VacinaController.listar_todas')
    @patch('app.Vacina.routes.get_db')
    def test_listar_vacinas_com_dados(self, mock_get_db, mock_listar):
        """Deve retornar lista de vacinas quando existirem registros."""
        # Configura os mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        vacinas_mock = [
            Vacina(id=1, nome="Hepatite B", doses=3),
            Vacina(id=2, nome="Febre Amarela", doses=1)
        ]
        mock_listar.return_value = vacinas_mock

        # Executa a requisição
        response = client.get("/vacinas/")

        # Verifica a resposta
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 2
        assert response_data[0]["nome"] == "Hepatite B"
        assert response_data[1]["nome"] == "Febre Amarela"

    @patch('app.Vacina.routes.VacinaController.buscar_por_id')
    @patch('app.Vacina.routes.get_db')
    def test_buscar_vacina_encontrada(self, mock_get_db, mock_buscar):
        """Deve retornar uma vacina quando encontrada."""
        # Configura os mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_buscar.return_value = Vacina(
            id=1, nome="BCG", doses=1
        )

        # Executa a requisição
        response = client.get("/vacinas/1")

        # Verifica a resposta
        assert response.status_code == 200
        data = response.json()
        assert data["nome"] == "BCG"

    @patch('app.Vacina.routes.VacinaController.buscar_por_id')
    @patch('app.Vacina.routes.get_db')
    def test_buscar_vacina_nao_encontrada(self, mock_get_db, mock_buscar):
        """Deve retornar 404 quando a vacina não é encontrada."""
        # Configura os mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_buscar.return_value = None

        # Executa a requisição
        response = client.get("/vacinas/999")

        # Verifica a resposta
        assert response.status_code == 404
        assert "não encontrada" in response.json()["detail"]

    @patch('app.Vacina.routes.VacinaController.criar')
    @patch('app.Vacina.routes.get_db')
    def test_criar_vacina_sucesso(self, mock_get_db, mock_criar):
        """Deve criar uma nova vacina com sucesso."""
        # Configura os mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        vacina_mock = Vacina(id=1, nome="Hepatite B", doses=2)
        mock_criar.return_value = vacina_mock

        # Dados para criação
        nova_vacina = {
            "nome": "Hepatite B",
            "doses": 2
        }

        # Executa a requisição
        response = client.post("/vacinas/", json=nova_vacina)

        # Verifica a resposta
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["id"] == 1
        assert response_data["nome"] == "Hepatite B"
        assert response_data["doses"] == 2

    @patch('app.Vacina.routes.VacinaController.criar')
    @patch('app.Vacina.routes.get_db')
    def test_cadastrar_vacina_nome_duplicado(self, mock_get_db, mock_criar):
        """Deve retornar 400 quando o nome da vacina é duplicado."""
        # Configura os mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_criar.side_effect = HTTPException(
            status_code=400,
            detail="Vacina com nome 'BCG' já existe"
        )

        # Dados para criação
        nova_vacina = {
            "nome": "BCG",
            "doses": 1
        }

        # Executa a requisição
        response = client.post("/vacinas/", json=nova_vacina)

        # Verifica a resposta
        assert response.status_code == 400

    @patch('app.Vacina.routes.VacinaController.atualizar')
    @patch('app.Vacina.routes.get_db')
    def test_atualizar_vacina_sucesso(self, mock_get_db, mock_atualizar):
        """Deve atualizar uma vacina existente com sucesso."""
        # Configura os mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        vacina_atualizada = Vacina(id=1, nome="Hepatite B Atualizada", doses=2)
        mock_atualizar.return_value = vacina_atualizada

        # Dados para atualização
        dados_atualizacao = {
            "nome": "Hepatite B Atualizada",
            "doses": 2
        }

        # Executa a requisição
        response = client.put("/vacinas/1", json=dados_atualizacao)

        # Verifica a resposta
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["nome"] == "Hepatite B Atualizada"
        assert response_data["doses"] == 2

    @patch('app.Vacina.routes.VacinaController.atualizar')
    @patch('app.Vacina.routes.get_db')
    def test_atualizar_vacina_nao_encontrada(self, mock_get_db, mock_atualizar):
        """Deve retornar 404 quando a vacina não é encontrada."""
        # Configura os mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_atualizar.side_effect = HTTPException(
            status_code=404,
            detail="Vacina com ID 999 não encontrada"
        )

        # Dados para atualização
        dados_atualizacao = {
            "nome": "Teste",
            "doses": 1
        }

        # Executa a requisição
        response = client.put("/vacinas/999", json=dados_atualizacao)

        # Verifica a resposta
        assert response.status_code == 404

    @patch('app.Vacina.routes.VacinaController.deletar')
    @patch('app.Vacina.routes.get_db')
    def test_deletar_vacina_sucesso(self, mock_get_db, mock_deletar):
        """Deve deletar uma vacina existente com sucesso."""
        # Configura os mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_deletar.return_value = True

        # Executa a requisição
        response = client.delete("/vacinas/1")

        # Verifica a resposta
        assert response.status_code == 204

    @patch('app.Vacina.routes.VacinaController.deletar')
    @patch('app.Vacina.routes.get_db')
    def test_deletar_vacina_nao_encontrada(self, mock_get_db, mock_deletar):
        """Deve retornar 404 quando a vacina não é encontrada."""
        # Configura os mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_deletar.side_effect = HTTPException(
            status_code=404,
            detail="Vacina com ID 999 não encontrada"
        )

        # Executa a requisição
        response = client.delete("/vacinas/999")

        # Verifica a resposta
        assert response.status_code == 404

 # pylint: disable=unused-argument
    @pytest.mark.parametrize("endpoint,method", [
        ("/vacinas/", "get"),
        ("/vacinas/1", "get"),
        ("/vacinas/", "post"),
        ("/vacinas/1", "put"),
        ("/vacinas/1", "delete"),
    ])
    def test_endpoints_existem(self, endpoint, method):
        """Verifica se todos os endpoints esperados estão registrados nas rotas da aplicação."""
        routes = [route.path for route in app.routes]
        assert endpoint in routes or "/vacinas/{vacina_id}" in routes
