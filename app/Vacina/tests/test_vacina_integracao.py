"""Testes de integração para o módulo de Vacinas."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine

# Cria um cliente de teste para a aplicação
client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Configura o banco de dados para cada teste."""
    # Limpa e recria todas as tabelas do banco de dados
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Limpa as tabelas após o teste
    Base.metadata.drop_all(bind=engine)


# pylint: disable=too-many-public-methods
class TestVacinaIntegration:
    """Testes de integração para o módulo de Vacinas."""

    def test_listar_vacinas_vazio(self):
        """Deve retornar uma lista vazia quando não há vacinas cadastradas."""
        # Executa a requisição
        response = client.get("/vacinas/")

        # Verifica a resposta
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 0

    def test_adicionar_vacina_sucesso(self):
        """Deve adicionar uma nova vacina com sucesso."""
        # Dados da nova vacina
        nova_vacina = {
            "nome": "Hepatite B",
            "doses": 3
        }

        # Executa a requisição
        response = client.post("/vacinas/", json=nova_vacina)

        # Verifica a resposta
        assert response.status_code == 201
        body = response.json()
        assert body["nome"] == "Hepatite B"
        assert body["doses"] == 3
        assert "id" in body
        assert body["id"] > 0

    def test_listar_vacinas_com_dados(self):
        """Deve listar corretamente múltiplas vacinas cadastradas."""
        client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        client.post("/vacinas/", json={"nome": "Hepatite B", "doses": 3})
        client.post("/vacinas/", json={"nome": "COVID-19", "doses": 2})

        response = client.get("/vacinas/")
        assert response.status_code == 200

        vacinas = response.json()
        assert len(vacinas) == 3
        assert any(v["nome"] == "BCG" for v in vacinas)
        assert any(v["nome"] == "Hepatite B" for v in vacinas)

    def test_buscar_vacina_por_id_sucesso(self):
        """Deve retornar os detalhes de uma vacina específica pelo ID."""
        response_create = client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        vacina_id = response_create.json()["id"]

        response = client.get(f"/vacinas/{vacina_id}")
        assert response.status_code == 200

        vacina = response.json()
        assert vacina["id"] == vacina_id
        assert vacina["nome"] == "BCG"
        assert vacina["doses"] == 1

    def test_buscar_vacina_nao_encontrada(self):
        """Deve retornar erro 404 ao buscar uma vacina com ID inexistente."""
        response = client.get("/vacinas/99999")
        assert response.status_code == 404
        assert "não encontrada" in response.json()["detail"].lower()

    def test_adicionar_vacina_nome_duplicado(self):
        """Deve impedir o cadastro de vacina com nome duplicado."""
        client.post("/vacinas/", json={"nome": "BCG", "doses": 1})

        response = client.post("/vacinas/", json={"nome": "BCG", "doses": 2})
        assert response.status_code == 400
        assert "já existe" in response.json()["detail"].lower()

    def test_adicionar_vacina_dados_invalidos(self):
        """Deve validar os dados fornecidos ao cadastrar uma vacina."""
        response = client.post("/vacinas/", json={"nome": "", "doses": 1})
        assert response.status_code == 422

        response = client.post("/vacinas/", json={"nome": "Teste", "doses": 0})
        assert response.status_code == 422

        response = client.post("/vacinas/", json={"nome": "Teste", "doses": -1})
        assert response.status_code == 422

        response = client.post("/vacinas/", json={"nome": "Teste", "doses": 11})
        assert response.status_code == 422

        response = client.post("/vacinas/", json={"nome": "Teste"})
        assert response.status_code == 422

    def test_atualizar_vacina_sucesso(self):
        """Deve atualizar corretamente os dados de uma vacina existente."""
        response_create = client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        vacina_id = response_create.json()["id"]

        response = client.put(
            f"/vacinas/{vacina_id}",
            json={"nome": "BCG Atualizada", "doses": 2}
        )
        assert response.status_code == 200

        vacina = response.json()
        assert vacina["nome"] == "BCG Atualizada"
        assert vacina["doses"] == 2

    def test_atualizar_vacina_nao_encontrada(self):
        """Deve retornar erro 404 ao tentar atualizar vacina inexistente."""
        response = client.put(
            "/vacinas/99999",
            json={"nome": "Teste", "doses": 1}
        )
        assert response.status_code == 404

    def test_deletar_vacina_sucesso(self):
        """Deve remover uma vacina existente com sucesso."""
        response_create = client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        vacina_id = response_create.json()["id"]

        response = client.delete(f"/vacinas/{vacina_id}")
        assert response.status_code == 204

        response_get = client.get(f"/vacinas/{vacina_id}")
        assert response_get.status_code == 404

    def test_deletar_vacina_nao_encontrada(self):
        """Deve retornar erro 404 ao tentar remover vacina inexistente."""
        response = client.delete("/vacinas/99999")
        assert response.status_code == 404

    def test_fluxo_completo_crud(self):
        """Deve executar com sucesso todas as operações CRUD em sequência."""
        response = client.get("/vacinas/")
        assert len(response.json()) == 0

        response = client.post("/vacinas/", json={"nome": "COVID-19", "doses": 2})
        assert response.status_code == 201
        vacina_id = response.json()["id"]

        response = client.get("/vacinas/")
        assert len(response.json()) == 1

        response = client.get(f"/vacinas/{vacina_id}")
        assert response.status_code == 200
        assert response.json()["nome"] == "COVID-19"

        response = client.put(
            f"/vacinas/{vacina_id}",
            json={"nome": "COVID-19 Pfizer", "doses": 3}
        )
        assert response.status_code == 200
        assert response.json()["doses"] == 3

        response = client.delete(f"/vacinas/{vacina_id}")
        assert response.status_code == 204

        response = client.get("/vacinas/")
        assert len(response.json()) == 0

    @pytest.mark.parametrize("nome,doses,esperado", [
        ("BCG", 1, 201),
        ("Hepatite B", 3, 201),
        ("Tríplice Viral", 2, 201),
        ("Febre Amarela", 1, 201),
    ])
    def test_adicionar_vacinas_validas(self, nome, doses, esperado):
        """Deve aceitar diferentes combinações válidas de nome e doses."""
        response = client.post("/vacinas/", json={"nome": nome, "doses": doses})
        assert response.status_code == esperado
        assert response.json()["nome"] == nome
        assert response.json()["doses"] == doses

    def test_atualizar_vacina_nome_duplicado(self):
        """Deve impedir a atualização para um nome de vacina já existente."""
        client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        response_create = client.post(
            "/vacinas/",
            json={"nome": "Hepatite B", "doses": 3}
        )
        vacina_id = response_create.json()["id"]

        response = client.put(
            f"/vacinas/{vacina_id}",
            json={"nome": "BCG"}
        )
        assert response.status_code == 400
        assert "já existe" in response.json()["detail"].lower()

    def test_response_structure(self):
        """Deve retornar a estrutura de dados correta na resposta."""
        response = client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        data = response.json()

        assert "id" in data
        assert "nome" in data
        assert "doses" in data
        assert isinstance(data["id"], int)
        assert isinstance(data["nome"], str)
        assert isinstance(data["doses"], int)

    def test_multiplas_vacinas_mesma_dose(self):
        """Deve permitir o cadastro de múltiplas vacinas com mesmo número de doses."""
        client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        client.post("/vacinas/", json={"nome": "Febre Amarela", "doses": 1})

        response = client.get("/vacinas/")
        vacinas = response.json()
        vacinas_dose_1 = [v for v in vacinas if v["doses"] == 1]
        assert len(vacinas_dose_1) == 2

    def test_atualizar_apenas_nome(self):
        """Deve atualizar apenas o nome mantendo os outros campos sem alterar."""
        response_create = client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        vacina_id = response_create.json()["id"]

        response = client.put(
            f"/vacinas/{vacina_id}",
            json={"nome": "BCG Atualizada"}
        )
        assert response.status_code == 200
        assert response.json()["nome"] == "BCG Atualizada"
        assert response.json()["doses"] == 1

    def test_atualizar_apenas_doses(self):
        """Deve atualizar apenas o número de doses mantendo o nome."""
        response_create = client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        vacina_id = response_create.json()["id"]

        response = client.put(
            f"/vacinas/{vacina_id}",
            json={"doses": 3}
        )
        assert response.status_code == 200
        assert response.json()["nome"] == "BCG"
        assert response.json()["doses"] == 3

    def test_criar_e_buscar_imediatamente(self):
        """Deve ser possível buscar uma vacina imediatamente após criá-la."""
        response_create = client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        vacina_id = response_create.json()["id"]

        response_get = client.get(f"/vacinas/{vacina_id}")
        assert response_get.status_code == 200
        assert response_get.json()["id"] == vacina_id
        assert response_get.json()["nome"] == "BCG"

    def test_deletar_e_verificar_lista(self):
        """Deve remover a vacina da lista após exclusão."""
        client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        response2 = client.post("/vacinas/", json={"nome": "Hepatite B", "doses": 3})
        vacina_id = response2.json()["id"]

        client.delete(f"/vacinas/{vacina_id}")

        response = client.get("/vacinas/")
        vacinas = response.json()
        assert len(vacinas) == 1
        assert vacinas[0]["nome"] == "BCG"

    @pytest.mark.parametrize("doses_invalidas", [0, -1, -5, 11, 20, 100])
    def test_doses_invalidas_parametrizado(self, doses_invalidas):
        """Deve rejeitar valores inválidos para o número de doses."""
        response = client.post(
            "/vacinas/",
            json={"nome": "Teste", "doses": doses_invalidas}
        )
        assert response.status_code == 422
