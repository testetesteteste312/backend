"""Testes de rotas para o módulo de usuários."""

from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.Usuario.model import Usuario

client = TestClient(app)


class TestUsuarioView:
    """Testes de rotas para o módulo de usuários."""
    @patch('app.Usuario.routes.UsuarioController.listar_todos')
    @patch('app.Usuario.routes.get_db')
    def test_listar_usuarios_vazio(self, mock_get_db, mock_listar):
        """Deve retornar lista vazia."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_listar.return_value = []

        response = client.get("/usuarios/")

        assert response.status_code == 200
        assert response.json() == []

    @patch('app.Usuario.routes.UsuarioController.listar_todos')
    @patch('app.Usuario.routes.get_db')
    def test_listar_usuarios_com_dados(self, mock_get_db, mock_listar):
        """Deve retornar lista de usuários."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        usuarios_mock = [
            Usuario(id=1, nome="Alice", email="alice@test.com", senha="hash1", is_admin=False),
            Usuario(id=2, nome="Bob", email="bob@test.com", senha="hash2", is_admin=False)
        ]
        mock_listar.return_value = usuarios_mock

        response = client.get("/usuarios/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["nome"] == "Alice"
        assert data[0].get("is_admin") is not None  # Garante que is_admin está presente

    @patch('app.Usuario.routes.UsuarioController.buscar_por_id')
    @patch('app.Usuario.routes.get_db')
    def test_buscar_usuario_encontrado(self, mock_get_db, mock_buscar):
        """Deve retornar usuário por ID."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_buscar.return_value = Usuario(
            id=1, nome="Alice", email="alice@test.com", senha="hash", is_admin=False
        )

        response = client.get("/usuarios/1")

        assert response.status_code == 200
        data = response.json()
        assert data["nome"] == "Alice"
        assert data.get("is_admin") is not None  # Garante que is_admin está presente

    @patch('app.Usuario.routes.UsuarioController.buscar_por_id')
    @patch('app.Usuario.routes.get_db')
    def test_buscar_usuario_nao_encontrado(self, mock_get_db, mock_buscar):
        """Deve retornar 404 quando usuário não existe."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_buscar.return_value = None

        response = client.get("/usuarios/999")

        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]

    @patch('app.Usuario.routes.UsuarioController.criar')
    @patch('app.Usuario.routes.get_db')
    def test_cadastrar_usuario_sucesso(self, mock_get_db, mock_criar):
        """Deve cadastrar usuário com sucesso."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_criar.return_value = Usuario(
            id=1, nome="Alice", email="alice@test.com", senha="hash", is_admin=False
        )

        payload = {
            "nome": "Alice",
            "email": "alice@test.com",
            "senha": "senha123",
            "is_admin": False
        }
        response = client.post("/usuarios/", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["nome"] == "Alice"
        assert data.get("is_admin") is not None  # Garante que is_admin está presente
        assert "senha" not in data

    @patch('app.Usuario.routes.UsuarioController.criar')
    @patch('app.Usuario.routes.get_db')
    def test_cadastrar_usuario_email_duplicado(self, mock_get_db, mock_criar):
        """Deve retornar erro ao cadastrar email duplicado."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_criar.side_effect = HTTPException(
            status_code=400,
            detail="Usuário com email 'alice@test.com' já existe"
        )

        payload = {
            "nome": "Alice",
            "email": "alice@test.com",
            "senha": "senha123"
        }
        response = client.post("/usuarios/", json=payload)

        assert response.status_code == 400

    def test_cadastrar_usuario_dados_invalidos(self):
        """Deve retornar erro com dados inválidos."""
        # Email inválido
        payload = {
            "nome": "Alice",
            "email": "email_invalido",
            "senha": "senha123"
        }
        response = client.post("/usuarios/", json=payload)
        assert response.status_code == 422

        # Senha curta
        payload = {
            "nome": "Alice",
            "email": "alice@test.com",
            "senha": "123"
        }
        response = client.post("/usuarios/", json=payload)
        assert response.status_code == 422

    @patch('app.Usuario.routes.UsuarioController.atualizar')
    @patch('app.Usuario.routes.get_db')
    def test_atualizar_usuario_sucesso(self, mock_get_db, mock_atualizar):
        """Deve atualizar usuário com sucesso."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_atualizar.return_value = Usuario(
            id=1, nome="Alice Silva", email="alice@test.com", senha="hash", is_admin=False
        )

        payload = {
            "nome": "Alice Silva",
            "email": "alice@test.com",
            "senha": "nova_senha",
            "is_admin": False
        }
        response = client.put("/usuarios/1", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["nome"] == "Alice Silva"

    @patch('app.Usuario.routes.UsuarioController.atualizar')
    @patch('app.Usuario.routes.get_db')
    def test_atualizar_usuario_nao_encontrado(self, mock_get_db, mock_atualizar):
        """Deve retornar 404 ao atualizar usuário inexistente."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_atualizar.side_effect = HTTPException(
            status_code=404,
            detail="Usuário com ID 999 não encontrado"
        )

        payload = {"nome": "Teste"}
        response = client.put("/usuarios/999", json=payload)

        assert response.status_code == 404

    @patch('app.Usuario.routes.UsuarioController.deletar')
    @patch('app.Usuario.routes.get_db')
    def test_deletar_usuario_sucesso(self, mock_get_db, mock_deletar):
        """Deve deletar usuário com sucesso."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_deletar.return_value = True

        response = client.delete("/usuarios/1")

        assert response.status_code == 204

# pylint: disable=duplicate-code
    @patch('app.Usuario.routes.UsuarioController.deletar')
    @patch('app.Usuario.routes.get_db')
    def test_deletar_usuario_nao_encontrado(self, mock_get_db, mock_deletar):
        """Deve retornar 404 ao deletar usuário inexistente."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_deletar.side_effect = HTTPException(
            status_code=404,
            detail="Usuário com ID 999 não encontrado"
        )

        response = client.delete("/usuarios/999")

        assert response.status_code == 404

    @patch('app.Usuario.routes.UsuarioController.autenticar')
    @patch('app.Usuario.routes.get_db')
    def test_login_sucesso(self, mock_get_db, mock_autenticar):
        """Deve autenticar usuário com sucesso."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_autenticar.return_value = Usuario(
            id=1, nome="Alice", email="alice@test.com", senha="hash", is_admin=False
        )

        response = client.post(
            "/usuarios/login?email=alice@test.com&senha=senha123"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "alice@test.com"

    @patch('app.Usuario.routes.UsuarioController.autenticar')
    @patch('app.Usuario.routes.get_db')
    def test_login_credenciais_invalidas(self, mock_get_db, mock_autenticar):
        """Deve retornar 401 com credenciais inválidas."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_autenticar.return_value = None

        response = client.post(
            "/usuarios/login?email=alice@test.com&senha=senha_errada"
        )

        assert response.status_code == 401
        assert "incorretos" in response.json()["detail"]

# pylint: disable=unused-argument
    @pytest.mark.parametrize("endpoint,method", [
        ("/usuarios/", "get"),
        ("/usuarios/1", "get"),
        ("/usuarios/", "post"),
        ("/usuarios/1", "put"),
        ("/usuarios/1", "delete"),
    ])
    def test_endpoints_existen(self, endpoint, method):
        """Verifica se todos os endpoints esperados estão registrados."""
        routes = [route.path for route in app.routes]
        assert endpoint in routes or "/usuarios/{usuario_id}" in routes
