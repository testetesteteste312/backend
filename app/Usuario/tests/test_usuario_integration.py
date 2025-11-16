"""Testes de integração para o módulo de usuários."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, Base, engine
from app.Usuario.model import Usuario

client = TestClient(app)

# pylint: disable=duplicate-code
@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Configura o banco de dados para cada teste."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_module_db():
    """Limpa a tabela de usuários antes de cada módulo de teste."""
    db = SessionLocal()
    db.query(Usuario).delete()
    db.commit()
    db.close()


# pylint: disable=too-many-public-methods
class TestUsuarioIntegration:
    """Testes de integração para o módulo de usuários."""

    def test_listar_usuarios_vazio(self):
        """Deve retornar uma lista vazia quando não há usuários."""
        response = client.get("/usuarios/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 0

    def test_senha_maior_que_72_recusada(self):
        """Deve rejeitar senha com mais de 72 caracteres."""
        senha_73 = "a1" * 36 + "x"
        response = client.post(
            "/usuarios/",
            json={
                "nome": "Teste",
                "email": "teste@teste.com",
                "senha": senha_73
            }
        )
        assert response.status_code == 422

    def test_login_sucesso(self):
        """Deve autenticar usuário com credenciais corretas."""
        usuario_data = {
            "nome": "Teste",
            "email": "teste@teste.com",
            "senha": "senha123"
        }
        client.post("/usuarios/", json=usuario_data)

        response = client.post(
            "/usuarios/login",
            params={
                "email": "teste@teste.com",
                "senha": "senha123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["email"] == "teste@teste.com"

    def test_login_credenciais_invalidas(self):
        """Deve rejeitar login com credenciais incorretas."""
        client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        response = client.post(
            "/usuarios/login?email=alice@teste.com&senha=senha_errada"
        )
        assert response.status_code == 401
        assert "incorretos" in response.json()["detail"].lower()

    def test_login_usuario_inexistente(self):
        """Deve rejeitar login com usuário inexistente."""
        response = client.post(
            "/usuarios/login?email=naoexiste@teste.com&senha=senha123"
        )
        assert response.status_code == 401

    def test_fluxo_completo_crud(self):
        """Deve testar fluxo completo de CRUD."""
        response = client.get("/usuarios/")
        assert len(response.json()) == 0
        response = client.post("/usuarios/", json={
            "nome": "Alice",
            "is_admin": False,
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        assert response.status_code == 200
        usuario_id = response.json()["id"]
        response = client.get("/usuarios/")
        assert len(response.json()) == 1
        response = client.get(f"/usuarios/{usuario_id}")
        assert response.status_code == 200
        assert response.json()["nome"] == "Alice"

        response = client.put(
            f"/usuarios/{usuario_id}",
            json={
                "nome": "Alice Silva",
                "email": "alice.silva@teste.com"
            }
        )
        assert response.status_code == 200
        assert response.json()["nome"] == "Alice Silva"

        response = client.post(
            "/usuarios/login?email=alice.silva@teste.com&senha=senha123"
        )
        assert response.status_code == 200
        response = client.delete(f"/usuarios/{usuario_id}")
        assert response.status_code == 204
        response = client.get("/usuarios/")
        assert len(response.json()) == 0

    @pytest.mark.parametrize("nome,email,senha,esperado", [
        ("Alice", "alice@teste.com", "senha123", 200),
        ("Bob Silva", "bob.silva@empresa.com.br", "senha456", 200),
        ("Carlos", "carlos+tag@domain.co", "senha789", 200),
    ])
    def test_adicionar_usuarios_validos(self, nome, email, senha, esperado):
        """Deve adicionar usuários válidos."""
        response = client.post("/usuarios/", json={
            "nome": nome,
            "email": email,
            "senha": senha
        })
        assert response.status_code == esperado
        assert response.json()["nome"] == nome
        assert response.json()["email"] == email.lower()

    def test_atualizar_email_duplicado(self):
        """Deve rejeitar atualização de email duplicado."""
        client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })

        response_create = client.post("/usuarios/", json={
            "nome": "Bob",
            "email": "bob@teste.com",
            "senha": "senha456"
        })
        bob_id = response_create.json()["id"]

        response = client.put(
            f"/usuarios/{bob_id}",
            json={"email": "alice@teste.com"}
        )
        assert response.status_code == 400
        assert "já está em uso" in response.json()["detail"].lower()

    def test_atualizar_apenas_nome(self):
        """Deve atualizar apenas o nome."""
        response_create = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        usuario_id = response_create.json()["id"]

        response = client.put(
            f"/usuarios/{usuario_id}",
            json={"nome": "Alice Silva"}
        )
        assert response.status_code == 200
        assert response.json()["nome"] == "Alice Silva"
        assert response.json()["email"] == "alice@teste.com"

    def test_atualizar_apenas_email(self):
        """Deve atualizar apenas o email."""
        response_create = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        usuario_id = response_create.json()["id"]

        response = client.put(
            f"/usuarios/{usuario_id}",
            json={"email": "alice.nova@teste.com"}
        )
        assert response.status_code == 200
        assert response.json()["nome"] == "Alice"
        assert response.json()["email"] == "alice.nova@teste.com"

    def test_atualizar_apenas_senha(self):
        """Deve atualizar apenas a senha."""
        response_create = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        usuario_id = response_create.json()["id"]

        response = client.put(
            f"/usuarios/{usuario_id}",
            json={"senha": "novasenha456"}
        )
        assert response.status_code == 200

        response_login = client.post(
            "/usuarios/login?email=alice@teste.com&senha=novasenha456"
        )
        assert response_login.status_code == 200

    def test_criar_e_buscar_imediatamente(self):
        """Deve criar e buscar imediatamente."""
        response_create = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        usuario_id = response_create.json()["id"]

        response_get = client.get(f"/usuarios/{usuario_id}")
        assert response_get.status_code == 200
        assert response_get.json()["id"] == usuario_id
        assert response_get.json()["nome"] == "Alice"

    def test_deletar_e_verificar_lista(self):
        """Deve deletar e verificar lista."""
        response1 = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        client.post("/usuarios/", json={
            "nome": "Bob",
            "email": "bob@teste.com",
            "senha": "senha456"
        })

        usuario_id = response1.json()["id"]
        client.delete(f"/usuarios/{usuario_id}")

        response = client.get("/usuarios/")
        usuarios = response.json()
        assert len(usuarios) == 1
        assert usuarios[0]["nome"] == "Bob"

    @pytest.mark.parametrize("email_invalido", [
        "email_sem_arroba",
        "@semdominio.com",
        "usuario@",
        "usuario @dominio.com",
        "",
    ])
    def test_emails_invalidos_parametrizado(self, email_invalido):
        """Deve rejeitar emails inválidos parametrizados."""
        response = client.post("/usuarios/", json={
            "nome": "Teste",
            "email": email_invalido,
            "senha": "senha123"
        })
        assert response.status_code == 422

    @pytest.mark.parametrize("senha_invalida", ["", "12345", "abc", "a", "12"])
    def test_senhas_invalidas_parametrizado(self, senha_invalida):
        """Deve rejeitar senhas inválidas parametrizadas."""
        response = client.post("/usuarios/", json={
            "nome": "Teste",
            "email": "teste@teste.com",
            "senha": senha_invalida
        })
        assert response.status_code == 422

    def test_login_apos_atualizar_senha(self):
        """Deve rejeitar login com senha antiga."""
        response_create = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        usuario_id = response_create.json()["id"]

        response_login_antiga = client.post(
            "/usuarios/login?email=alice@teste.com&senha=senha123"
        )
        assert response_login_antiga.status_code == 200

        client.put(
            f"/usuarios/{usuario_id}",
            json={"senha": "novasenha456"}
        )

        response_login_antiga2 = client.post(
            "/usuarios/login?email=alice@teste.com&senha=senha123"
        )
        assert response_login_antiga2.status_code == 401

        response_login_nova = client.post(
            "/usuarios/login?email=alice@teste.com&senha=novasenha456"
        )
        assert response_login_nova.status_code == 200
