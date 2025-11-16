"""Configuração de fixtures para os testes do módulo de Usuário.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Cria todas as tabelas do banco de dados antes da execução dos testes.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    """Fornece um cliente de teste para fazer requisições à API.
    """
    with TestClient(app) as test_client:
        yield test_client

# pylint: disable=duplicate-code
@pytest.fixture()
def db_session():
    """Fornece uma sessão do banco de dados para cada teste.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
