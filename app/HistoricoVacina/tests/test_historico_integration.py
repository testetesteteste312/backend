"""Testes de integração para o histórico de vacinas."""
from datetime import date
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, SessionLocal, Base, engine
from app.HistoricoVacina.model import HistoricoVacinal, StatusDose
from app.Usuario.model import Usuario
from app.Vacina.model import Vacina

# Fixtures
@pytest.fixture(scope="module")
def test_client():
    """Fornece um cliente de teste para a aplicação."""
    return TestClient(app)

# pylint: disable=duplicate-code
@pytest.fixture(scope="function")
def db_session():
    """Cria e gerencia uma sessão de banco de dados para os testes."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

# pylint: disable=redefined-outer-name
@pytest.fixture
def override_get_db(db_session):
    """Substitui a dependência get_db para uso nos testes."""
    def _get_db():
        try:
            yield db_session
        finally:
            pass
    return _get_db

# pylint: disable=redefined-outer-name
@pytest.fixture(autouse=True)
def setup_test_db(override_get_db):
    """Configura o banco de dados de teste antes de cada teste."""
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()

# pylint: disable=redefined-outer-name
@pytest.fixture()
def criar_usuario(db_session):
    """Cria um usuário para os testes."""
    usuario = Usuario(
        nome="Test User",
        email="test@example.com",
        senha="testpassword"
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario

# pylint: disable=redefined-outer-name
@pytest.fixture()
def criar_vacina(db_session):
    """Cria uma vacina para os testes."""
    vacina = Vacina(
        nome="Vacina Teste",
        doses=3
    )
    db_session.add(vacina)
    db_session.commit()
    db_session.refresh(vacina)
    return vacina

# pylint: disable=redefined-outer-name
def test_listar_historico(test_client, criar_usuario, criar_vacina, db_session):
    """Testa a listagem de histórico."""
    # Cria um registro de histórico para teste
    historico = HistoricoVacinal(
        usuario_id=criar_usuario.id,
        vacina_id=criar_vacina.id,
        numero_dose=1,
        status=StatusDose.PENDENTE
    )
    db_session.add(historico)
    db_session.commit()

    # Faz a requisição
    response = test_client.get(f"/usuarios/{criar_usuario.id}/historico/")
    # Verifica a resposta
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["usuario_id"] == criar_usuario.id

# pylint: disable=redefined-outer-name
def test_atualizar_historico(test_client, criar_usuario, criar_vacina, db_session):
    """Testa a atualização de um registro de histórico."""
    # Cria um registro de histórico para teste
    historico = HistoricoVacinal(
        usuario_id=criar_usuario.id,
        vacina_id=criar_vacina.id,
        numero_dose=1,
        status=StatusDose.PENDENTE
    )
    db_session.add(historico)
    db_session.commit()

    # Dados para atualização
    dados_atualizacao = {
        "status": "aplicada",
        "data_aplicacao": date.today().isoformat()
    }

    # Faz a requisição
    response = test_client.put(
        f"/usuarios/{criar_usuario.id}/historico/{historico.id}",
        json=dados_atualizacao
    )

    # Verifica a resposta
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "aplicada"
    assert data["data_aplicacao"] == date.today().isoformat()

def test_marcar_como_aplicada(test_client, criar_usuario, criar_vacina, db_session):
    """Testa marcar uma dose como aplicada."""
    # Cria um registro de histórico
    historico = HistoricoVacinal(
        usuario_id=criar_usuario.id,
        vacina_id=criar_vacina.id,
        numero_dose=1,
        status=StatusDose.PENDENTE
    )
    db_session.add(historico)
    db_session.commit()

    # Dados para marcar como aplicada
    dados_aplicacao = {
        "data_aplicacao": date.today().isoformat(),
        "lote": "LOTE123",
        "local_aplicacao": "Braço esquerdo",
        "profissional": "Dr. Silva"
    }

    # Faz a requisição
    response = test_client.patch(
        f"/usuarios/{criar_usuario.id}/historico/{historico.id}/aplicar",
        json=dados_aplicacao
    )

    # Verifica a resposta
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "aplicada"
    assert data["lote"] == "LOTE123"
    assert data["local_aplicacao"] == "Braço esquerdo"
    assert data["profissional"] == "Dr. Silva"

# pylint: disable=redefined-outer-name
def test_deletar_historico(test_client, criar_usuario, criar_vacina, db_session):
    """Testa a exclusão de um registro de histórico."""
    # Cria um registro de histórico para teste
    historico = HistoricoVacinal(
        usuario_id=criar_usuario.id,
        vacina_id=criar_vacina.id,
        numero_dose=1,
        status=StatusDose.PENDENTE
    )
    db_session.add(historico)
    db_session.commit()

    # Faz a requisição de exclusão
    response = test_client.delete(
        f"/usuarios/{criar_usuario.id}/historico/{historico.id}"
    )
    assert response.status_code == 204

    # Verifica se o registro foi realmente excluído
    response = test_client.get(
        f"/usuarios/{criar_usuario.id}/historico/{historico.id}"
    )
    assert response.status_code == 404
