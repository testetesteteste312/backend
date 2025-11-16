"""Módulo de rotas para gerenciamento de usuários."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UsuarioCreate, UsuarioResponse, UsuarioUpdate, ErrorResponse
from app.Usuario.controller import UsuarioController


router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.get(
    "/",
    response_model=List[UsuarioResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar todos os usuários",
    description="Retorna a lista completa de usuários cadastrados no sistema"
)
async def listar_usuarios(db: Session = Depends(get_db)):
    """Lista todos os usuários cadastrados no sistema."""
    usuarios = UsuarioController.listar_todos(db)
    return usuarios


@router.get(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}},
    summary="Buscar usuário por ID",
    description="Retorna os dados de um usuário específico"
)
async def buscar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Busca um usuário pelo ID."""
    usuario = UsuarioController.buscar_por_id(db, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário com ID {usuario_id} não encontrado"
        )
    return UsuarioResponse.from_orm(usuario)


@router.post("/", response_model=UsuarioResponse)
async def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """Cria um novo usuário no sistema."""
    return UsuarioController.criar(db, **usuario.dict())


@router.put(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
    summary="Atualizar usuário",
    description="Atualiza os dados de um usuário existente"
)
async def atualizar_usuario(
    usuario_id: int,
    usuario: UsuarioUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza os dados de um usuário existente."""
    usuario_atualizado = UsuarioController.atualizar(
        db, usuario_id, usuario.nome, usuario.email, usuario.senha,
        is_admin=usuario.is_admin or False
    )
    return usuario_atualizado


@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
    summary="Deletar usuário",
    description="Remove um usuário do sistema"
)
async def deletar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Remove um usuário do sistema."""
    UsuarioController.deletar(db, usuario_id)
    return None


@router.post(
    "/login",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
    responses={401: {"model": ErrorResponse}},
    summary="Autenticar usuário",
    description="Valida email e senha do usuário"
)
async def login(email: str, senha: str, db: Session = Depends(get_db)):
    """Autentica um usuário."""
    usuario = UsuarioController.autenticar(db, email, senha)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    return usuario
