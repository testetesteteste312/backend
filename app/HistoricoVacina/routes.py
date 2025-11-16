"""Rotas do histórico vacinal."""
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, status, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    HistoricoVacinalCreate,
    HistoricoVacinalUpdate,
    HistoricoVacinalResponse,
    HistoricoVacinalCompleto,
    EstatisticasHistorico,
    ErrorResponse,
    StatusDoseEnum
)
from app.HistoricoVacina.controller import HistoricoVacinalController
from app.HistoricoVacina.model import StatusDose
from app.Usuario.model import Usuario

router = APIRouter(prefix="/{usuario_id}/historico", tags=["Histórico Vacinal"])

class FiltrosHistorico(BaseModel):
    """Modelo para os parâmetros de filtro do histórico."""
    ano: Optional[int] = Field(None, ge=1900, le=2100, description="Ano para filtrar o histórico")
    mes: Optional[int] = Field(None, ge=1, le=12, description="Mês para filtrar o histórico")
    vacina_id: Optional[int] = Field(None, description="ID da vacina para filtrar")
    status_filtro: Optional[StatusDoseEnum] = Field(None, description="Status da dose para filtrar")

class DadosAplicacao(BaseModel):
    """Modelo para os dados de aplicação da vacina."""
    data_aplicacao: date = Field(..., description="Data em que a dose foi aplicada")
    lote: Optional[str] = Field(None, description="Lote da vacina")
    local_aplicacao: Optional[str] = Field(None, description="Local onde foi aplicada")
    profissional: Optional[str] = Field(None, description="Nome do profissional")

# Listar histórico vacinal com filtros
@router.get(
    "/",
    response_model=List[HistoricoVacinalCompleto],
    status_code=status.HTTP_200_OK,
    summary="Listar histórico vacinal do usuário",
    description="Retorna o histórico vacinal completo do usuário com filtros opcionais"
)
async def listar_historico(
    usuario_id: int = Path(..., description="ID do usuário"),
    filtros: FiltrosHistorico = Depends(),
    db: Session = Depends(get_db)
):
    """Lista o histórico vacinal do usuário com filtros opcionais."""
    historico = HistoricoVacinalController.listar_por_usuario(
        db=db,
        usuario_id=usuario_id,
        ano=filtros.ano,
        mes=filtros.mes,
        vacina_id=filtros.vacina_id,
        status_filtro=filtros.status_filtro
    )

    resultado = []
    for h in historico:
        resultado.append({
            "id": h.id,
            "usuario_id": h.usuario_id,
            "vacina_id": h.vacina_id,
            "vacina_nome": h.vacina.nome,
            "vacina_doses_totais": h.vacina.doses,
            "numero_dose": h.numero_dose,
            "status": h.status,
            "data_aplicacao": h.data_aplicacao,
            "data_prevista": h.data_prevista,
            "lote": h.lote,
            "local_aplicacao": h.local_aplicacao,
            "profissional": h.profissional,
            "observacoes": h.observacoes,
            "created_at": h.created_at,
            "updated_at": h.updated_at
        })

    return resultado


@router.get(
    "/estatisticas",
    response_model=EstatisticasHistorico,
    status_code=status.HTTP_200_OK,
    summary="Obter estatísticas do histórico vacinal",
    description="Retorna estatísticas e resumo do histórico vacinal do usuário"
)
async def obter_estatisticas(
    usuario_id: int,
    db: Session = Depends(get_db)
):
    """obter estatisticas do historico"""
    estatisticas = HistoricoVacinalController.obter_estatisticas(db, usuario_id)
    return estatisticas


@router.get(
    "/{historico_id}",
    response_model=HistoricoVacinalCompleto,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}},
    summary="Buscar registro específico do histórico",
    description="Retorna detalhes de um registro específico do histórico vacinal"
)

# pylint: disable=duplicate-code
async def buscar_registro(
    usuario_id: int,
    historico_id: int,
    db: Session = Depends(get_db)
):
    """buscar registro do historico"""
    historico = HistoricoVacinalController.buscar_por_id(db, historico_id, usuario_id)
    if not historico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registro com ID {historico_id} não encontrado"
        )

    return {
        "id": historico.id,
        "usuario_id": historico.usuario_id,
        "vacina_id": historico.vacina_id,
        "vacina_nome": historico.vacina.nome,
        "vacina_doses_totais": historico.vacina.doses,
        "numero_dose": historico.numero_dose,
        "status": historico.status,
        "data_aplicacao": historico.data_aplicacao,
        "data_prevista": historico.data_prevista,
        "lote": historico.lote,
        "local_aplicacao": historico.local_aplicacao,
        "profissional": historico.profissional,
        "observacoes": historico.observacoes,
        "created_at": historico.created_at,
        "updated_at": historico.updated_at
    }


@router.post(
    "/",
    response_model=HistoricoVacinalResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Adicionar registro ao histórico vacinal",
    description="Cria um novo registro de dose no histórico vacinal do usuário"
)
async def criar_registro(
    usuario_id: int,
    historico_data: HistoricoVacinalCreate,
    db: Session = Depends(get_db)
):
    """Cria um novo registro de histórico vacinal e envia e-mail de confirmação."""

    # Verifica se o usuário existe
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Cria o registro no banco
    novo_registro = HistoricoVacinalController.criar_registro(
        db=db,
        usuario_id=usuario_id,
        historico_data=historico_data,
    )

    return {
        "id": novo_registro.id,
        "usuario_id": novo_registro.usuario_id,
        "vacina_id": novo_registro.vacina_id,
        "vacina_nome": novo_registro.vacina.nome,
        "numero_dose": novo_registro.numero_dose,
        "status": novo_registro.status,
        "data_aplicacao": novo_registro.data_aplicacao,
        "data_prevista": novo_registro.data_prevista,
        "lote": novo_registro.lote,
        "local_aplicacao": novo_registro.local_aplicacao,
        "profissional": novo_registro.profissional,
        "observacoes": novo_registro.observacoes,
        "created_at": novo_registro.created_at,
        "updated_at": novo_registro.updated_at,
    }


@router.put(
    "/{historico_id}",
    response_model=HistoricoVacinalResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
    summary="Atualizar registro do histórico",
    description="Atualiza um registro existente no histórico vacinal"
)
@router.put(
    "/{historico_id}",
    response_model=HistoricoVacinalResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
    summary="Atualizar registro do histórico",
    description="Atualiza um registro existente no histórico vacinal"
)
async def atualizar_registro(
    usuario_id: int,
    historico_id: int,
    historico: HistoricoVacinalUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza um registro do histórico."""
    update_data = historico.model_dump(exclude_unset=True)

    if 'status' in update_data and update_data['status'] is not None:
        update_data['status'] = StatusDose(update_data['status'].value)

    registro_atualizado = HistoricoVacinalController.atualizar_registro(
        db=db,
        historico_id=historico_id,
        usuario_id=usuario_id,
        update_data=update_data
    )

    if not registro_atualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registro com ID {historico_id} não encontrado"
        )

    return registro_atualizado

@router.patch(
    "/{historico_id}/aplicar",
    response_model=HistoricoVacinalResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
    summary="Marcar dose como aplicada",
    description="Marca uma dose pendente como aplicada com informações da aplicação"
)
async def marcar_como_aplicada(
    usuario_id: int,
    historico_id: int,
    dados: DadosAplicacao,
    db: Session = Depends(get_db)
):
    """Marcar dose como aplicada com as informações fornecidas"""
    registro_atualizado = HistoricoVacinalController.marcar_dose_como_aplicada(
        db=db,
        historico_id=historico_id,
        usuario_id=usuario_id,
        data_aplicacao=dados.data_aplicacao,
        lote=dados.lote,
        local_aplicacao=dados.local_aplicacao,
        profissional=dados.profissional
    )

    if not registro_atualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registro com ID {historico_id} não encontrado"
        )

    return registro_atualizado

@router.delete(
    "/{historico_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
    summary="Deletar registro do histórico",
    description="Remove um registro do histórico vacinal"
)
async def deletar_registro(
    usuario_id: int,
    historico_id: int,
    db: Session = Depends(get_db)
):
    """deletar registro do historico"""
    HistoricoVacinalController.deletar_registro(db, historico_id, usuario_id)
    return None
