"""Módulo de configuração do banco de dados."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

ENV = os.getenv("ENV", "dev")

if ENV == "test":
    DATABASE_URL = "sqlite:///./test_imunetrack.db"
else:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://imunetrack_user:imunetrack_pass@db:5432/"
        "imunetrack"
    )

# Configuração do engine com suporte para SQLite em testes
connect_args = {"check_same_thread": False} if ENV == "test" else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# pylint: disable=invalid-name
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Gerenciador de contexto para sessões do banco de dados."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
