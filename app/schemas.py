"""Schemas Pydantic para validação de dados da API."""
from datetime import datetime, date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from app.HistoricoVacina.model import StatusDose

class StatusDoseEnum(str, Enum):
    """Enum para status de doses de vacinas."""

    PENDENTE = "pendente"
    APLICADA = "aplicada"
    ATRASADA = "atrasada"
    CANCELADA = "cancelada"

class VacinaBase(BaseModel):
    """Schema base para Vacina."""

    nome: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nome da vacina"
    )
    doses: int = Field(
        ...,
        gt=0,
        le=10,
        description="Número de doses necessárias"
    )

# pylint: disable=too-few-public-methods
class VacinaCreate(VacinaBase):
    """Schema para criação de Vacina."""


class VacinaUpdate(BaseModel):
    """Schema para atualização de Vacina."""

    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    doses: Optional[int] = Field(None, gt=0, le=10)


class VacinaResponse(VacinaBase):
    """Schema para resposta de Vacina."""

    id: int

    class Config:
        """Configuração do Pydantic."""

        from_attributes = True


class UsuarioBase(BaseModel):
    """Schema base para Usuario."""

    nome: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nome completo",
        example="Alice Silva"
    )
    email: EmailStr = Field(
        ...,
        description="Email válido",
        example="alice@teste.com"
    )

    @validator('nome')
    @classmethod
    def nome_nao_vazio(cls, v):
        """Valida que nome não é apenas espaços."""
        if not v.strip():
            raise ValueError('Nome não pode ser vazio')
        return v.strip()

    @validator('email')
    @classmethod
    def email_lowercase(cls, v):
        """Converte email para minúsculas."""
        return v.lower()


class UsuarioCreate(UsuarioBase):
    """Schema para criação de Usuario."""

    senha: str = Field(
        ...,
        min_length=6,
        max_length=72,
        description="Senha com no mínimo 6 caracteres"
    )

    @validator('senha')
    @classmethod
    def senha_forte(cls, v):
        """Valida força da senha."""
        if len(v) < 6:
            raise ValueError('Senha deve ter pelo menos 6 caracteres')
        if len(v) > 72:
            raise ValueError('Senha deve ter no máximo 72 caracteres')
        if not any(c.isdigit() for c in v):
            raise ValueError('Senha deve conter ao menos um número')
        if not any(c.isalpha() for c in v):
            raise ValueError('Senha deve conter ao menos uma letra')
        return v


class UsuarioUpdate(BaseModel):
    """Schema para atualização de Usuario."""

    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    senha: Optional[str] = Field(None, min_length=6, max_length=72)
    is_admin: Optional[bool] = False

    @validator('nome')
    @classmethod
    def nome_nao_vazio(cls, v):
        """Valida que nome não é apenas espaços."""
        if v is not None and (not v or not v.strip()):
            raise ValueError('Nome não pode ser vazio')
        return v.strip() if v else v

    @validator('email')
    @classmethod
    def email_lowercase(cls, v):
        """Converte email para minúsculas."""
        return v.lower() if v else v


# pylint: disable=too-few-public-methods
class UsuarioResponse(UsuarioBase):
    """Schema para resposta de Usuario."""

    id: int
    is_admin: bool

    class Config:
        """Configuração do Pydantic."""

        from_attributes = True


# ==================== SCHEMAS DE ERRO ====================

class ErrorResponse(BaseModel):
    """Schema para respostas de erro."""

    detail: str = Field(..., description="Descrição do erro")


class MessageResponse(BaseModel):
    """Schema para mensagens de sucesso."""

    message: str = Field(..., description="Mensagem de sucesso")


# ==================== SCHEMAS DE HISTÓRICO VACINAL ====================
class HistoricoVacinalBase(BaseModel):
    """Schema base para Histórico Vacinal."""

    vacina_id: int = Field(..., description="ID da vacina")
    numero_dose: int = Field(..., ge=1, description="Número da dose (1, 2, 3...)")
    status: StatusDoseEnum = Field(default=StatusDoseEnum.PENDENTE)
    data_aplicacao: Optional[date] = Field(
        None,
        description="Data em que a dose foi aplicada"
    )
    data_prevista: Optional[date] = Field(
        None,
        description="Data prevista para aplicação"
    )
    lote: Optional[str] = Field(None, max_length=50)
    local_aplicacao: Optional[str] = Field(None, max_length=200)
    profissional: Optional[str] = Field(None, max_length=200)
    observacoes: Optional[str] = Field(None, max_length=500)


# pylint: disable=too-few-public-methods, unnecessary-pass
class HistoricoVacinalCreate(HistoricoVacinalBase):
    """Schema para criação de Histórico Vacinal."""
    vacina_id: int
    numero_dose: int
    status: StatusDose = StatusDose.PENDENTE
    data_aplicacao: Optional[date] = None
    data_prevista: Optional[date] = None
    lote: Optional[str] = None
    local_aplicacao: Optional[str] = None
    profissional: Optional[str] = None
    observacoes: Optional[str] = None


class HistoricoVacinalUpdate(BaseModel):
    """Schema para atualizar um registro no histórico."""

    numero_dose: Optional[int] = Field(None, ge=1)
    status: Optional[StatusDoseEnum] = None
    data_aplicacao: Optional[date] = None
    data_prevista: Optional[date] = None
    lote: Optional[str] = Field(None, max_length=50)
    local_aplicacao: Optional[str] = Field(None, max_length=200)
    profissional: Optional[str] = Field(None, max_length=200)
    observacoes: Optional[str] = Field(None, max_length=500)


class HistoricoVacinalResponse(HistoricoVacinalBase):
    """Schema para resposta com dados do histórico."""

    id: int
    usuario_id: int
    vacina_nome: str
    created_at: datetime
    updated_at: datetime

    class Config:
        """Configuração do Pydantic."""

        from_attributes = True


class HistoricoVacinalCompleto(BaseModel):
    """Schema com informações completas incluindo dados da vacina."""

    id: int
    usuario_id: int
    vacina_id: int
    vacina_nome: str
    vacina_doses_totais: int
    numero_dose: int
    status: StatusDoseEnum
    data_aplicacao: Optional[date]
    data_prevista: Optional[date]
    lote: Optional[str]
    local_aplicacao: Optional[str]
    profissional: Optional[str]
    observacoes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Configuração do Pydantic."""

        from_attributes = True


# pylint: disable=too-few-public-methods
class HistoricoFiltros(BaseModel):
    """Filtros para busca no histórico vacinal."""

    ano: Optional[int] = Field(None, ge=1900, le=2100)
    vacina_id: Optional[int] = None
    status: Optional[StatusDoseEnum] = None
    mes: Optional[int] = Field(None, ge=1, le=12)


# pylint: disable=too-few-public-methods
class EstatisticasHistorico(BaseModel):
    """Estatísticas do histórico vacinal."""

    total_doses: int
    doses_aplicadas: int
    doses_pendentes: int
    doses_atrasadas: int
    doses_canceladas: int
    vacinas_completas: int
    vacinas_incompletas: int
    proximas_doses: list
