"""Rotas da API para gerenciamento de vacinas."""

from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import VacinaCreate, VacinaResponse, VacinaUpdate, ErrorResponse
from app.Vacina.controller import VacinaController

router = APIRouter(prefix="/vacinas", tags=["Vacinas"])

@router.get(
    "/",
    response_model=List[VacinaResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar todas as vacinas",
    description="Retorna a lista completa de vacinas cadastradas no sistema"
)
async def listar_vacinas(db: Session = Depends(get_db)) -> List[VacinaResponse]:
    """Lista todas as vacinas cadastradas no sistema."""
    vacinas = VacinaController.listar_todas(db)
    return vacinas

@router.get(
    "/{vacina_id}",
    response_model=VacinaResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}},
    summary="Buscar vacina por ID",
    description="Retorna os dados de uma vacina específica"
)
async def buscar_vacina(
    vacina_id: int,
    db: Session = Depends(get_db)
) -> VacinaResponse:
    """Busca uma vacina pelo seu ID."""
    vacina = VacinaController.buscar_por_id(db, vacina_id)
    if not vacina:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vacina com ID {vacina_id} não encontrada"
        )
    return VacinaResponse.from_orm(vacina)

@router.post(
    "/",
    response_model=VacinaResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
    summary="Cadastrar nova vacina",
    description="Cria uma nova vacina no sistema"
)
async def cadastrar_vacina(
    vacina: VacinaCreate,
    db: Session = Depends(get_db)
) -> VacinaResponse:
    """Cadastra uma nova vacina no sistema."""
    nova_vacina = VacinaController.criar(db, vacina.nome, vacina.doses)
    return nova_vacina

@router.put(
    "/{vacina_id}",
    response_model=VacinaResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Vacina não encontrada"},
        400: {"model": ErrorResponse, "description": "Dados inválidos"}
    },
    summary="Atualizar vacina",
    description="Atualiza os dados de uma vacina existente"
)
async def atualizar_vacina(
    vacina_id: int,
    vacina: VacinaUpdate,
    db: Session = Depends(get_db)
) -> VacinaResponse:
    """Atualiza os dados de uma vacina existente."""
    vacina_atualizada = VacinaController.atualizar(
        db, vacina_id, vacina.nome, vacina.doses
    )
    return vacina_atualizada

@router.delete(
    "/{vacina_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse, "description": "Vacina não encontrada"}},
    summary="Deletar vacina",
    description="Remove uma vacina do sistema"
)
async def deletar_vacina(
    vacina_id: int,
    db: Session = Depends(get_db)
) -> None:
    """Remove uma vacina do sistema."""
    VacinaController.deletar(db, vacina_id)
    return None
