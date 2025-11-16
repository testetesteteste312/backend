"""Modelo de dados para representar as vacinas no sistema."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Vacina(Base):
    """Modelo que representa uma vacina no sistema."""
    __tablename__ = "vacinas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(100), unique=True, nullable=False, index=True)
    doses = Column(Integer, nullable=False)

    historico_vacinal = relationship("HistoricoVacinal", back_populates="vacina")

    def __repr__(self) -> str:
        """Retorna uma representação em string do objeto Vacina."""
        return f"<Vacina(id={self.id}, nome='{self.nome}', doses={self.doses})>"

    def to_dict(self) -> dict:
        """Converte o objeto Vacina para um dicionário."""
        return {
            "id": self.id,
            "nome": self.nome,
            "doses": self.doses
        }
