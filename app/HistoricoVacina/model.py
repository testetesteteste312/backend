""" Modelo de Histórico Vacinal """
from datetime import datetime
import enum

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship

from app.database import Base


class StatusDose(str, enum.Enum):
    """ Enumeração de status de dose """
    PENDENTE = "pendente"
    APLICADA = "aplicada"
    ATRASADA = "atrasada"
    CANCELADA = "cancelada"

class HistoricoVacinal(Base):
    """Modelo de Histórico Vacinal."""
    __tablename__ = "historico_vacinal"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    vacina_id = Column(Integer, ForeignKey('vacinas.id'), nullable=False)
    numero_dose = Column(Integer, nullable=False)
    status = Column(Enum(StatusDose), default=StatusDose.PENDENTE, nullable=False)
    data_aplicacao = Column(Date, nullable=True)
    data_prevista = Column(Date, nullable=True)
    lote = Column(String(50), nullable=True)
    local_aplicacao = Column(String(100), nullable=True)
    profissional = Column(String(100), nullable=True)
    observacoes = Column(Text, nullable=True)
    created_at = Column(Date, default=datetime.utcnow, nullable=False)
    updated_at = Column(Date, default=datetime.utcnow,
    onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    vacina = relationship("Vacina", back_populates="historico_vacinal")
    usuario = relationship("Usuario", back_populates="historico_vacinal")

    def __repr__(self) -> str:
        return (f"<HistoricoVacinal(id={self.id}, usuario_id={self.usuario_id}, "
                f"vacina_id={self.vacina_id}, dose={self.numero_dose}, status='{self.status}')>")

    def to_dict(self) -> dict:
        """Converte o objeto para dicionário."""
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "vacina_id": self.vacina_id,
            "vacina_nome": self.vacina.nome if self.vacina else None,
            "numero_dose": self.numero_dose,
            "status": self.status.value,
            "data_aplicacao": self.data_aplicacao.isoformat() if self.data_aplicacao else None,
            "data_prevista": self.data_prevista.isoformat() if self.data_prevista else None,
            "lote": self.lote,
            "local_aplicacao": self.local_aplicacao,
            "profissional": self.profissional,
            "observacoes": self.observacoes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
