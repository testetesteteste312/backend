"""Módulo de controle para operações relacionadas a usuários.

Este módulo contém a lógica de negócio para operações CRUD de usuários,
incluindo validação de dados e manipulação de senhas seguras.
"""
import re
from typing import List, Optional

from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.Usuario.model import Usuario

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsuarioController:
    """Controlador para operações CRUD de Usuario."""

    @staticmethod
    def _hash_senha(senha: str) -> str:
        """Gera um hash seguro para a senha fornecida."""
        if isinstance(senha, bytes):
            senha = senha.decode("utf-8")
        # Se já for hash bcrypt, retorna direto
        if senha.startswith("$2b$"):
            return senha
        # Trunca se maior que 72 bytes
        if len(senha.encode("utf-8")) > 72:
            senha = senha[:72]
        return pwd_context.hash(senha)

    @staticmethod
    def _verificar_senha(senha: str, senha_hash: str) -> bool:
        """Verifica se a senha corresponde ao hash."""
        return pwd_context.verify(senha, senha_hash)

    @staticmethod
    def _validar_email(email: str) -> bool:
        """Valida formato do email."""
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(padrao, email) is not None

    @staticmethod
    def _validar_senha(senha: str) -> bool:
        """Valida força da senha."""
        return len(senha) >= 6

    @staticmethod
    def listar_todos(db: Session) -> List[Usuario]:
        """Retorna todos os usuários cadastrados."""
        return db.query(Usuario).all()

    @staticmethod
    def buscar_por_id(db: Session, usuario_id: int) -> Optional[Usuario]:
        """Busca um usuário por ID."""
        return db.query(Usuario).filter(Usuario.id == usuario_id).first()

    @staticmethod
    def buscar_por_email(db: Session, email: str) -> Optional[Usuario]:
        """Busca um usuário por email."""
        return db.query(Usuario).filter(Usuario.email == email).first()

    @staticmethod
    def criar(db: Session, nome: str, email: str, senha: str, is_admin: bool = False) -> Usuario:
        """Cria um novo usuário com validações e senha hasheada."""
        # Validações
        if not nome or len(nome.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome é obrigatório"
            )

        if not UsuarioController._validar_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email inválido"
            )

        if not UsuarioController._validar_senha(senha):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha deve ter no mínimo 6 caracteres"
            )

        # Verifica duplicidade de email
        if UsuarioController.buscar_por_email(db, email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Usuário com email '{email}' já existe"
            )

        # Cria usuário com senha hasheada
        senha_hash = UsuarioController._hash_senha(senha)
        usuario = Usuario(nome=nome.strip(), email=email.lower(), senha=senha_hash,
        is_admin=is_admin)

        try:
            db.add(usuario)
            db.commit()
            db.refresh(usuario)
            return usuario
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao criar usuário"
            ) from e

# pylint: disable=duplicate-code, too-many-arguments, too-many-positional-arguments
    @staticmethod
    def atualizar(
        db: Session,
        usuario_id: int,
        nome: Optional[str] = None,
        email: Optional[str] = None,
        senha: Optional[str] = None,
        is_admin: Optional[bool] = False,
    ) -> Usuario:
        """Atualiza um usuário existente."""
        usuario = UsuarioController.buscar_por_id(db, usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário com ID {usuario_id} não encontrado"
            )

        # Valida e atualiza nome
        if nome is not None:
            if len(nome.strip()) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Nome não pode ser vazio"
                )
            usuario.nome = nome.strip()

        # Valida e atualiza email
        if email is not None:
            if not UsuarioController._validar_email(email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email inválido"
                )
            # Verifica se email já está em uso por outro usuário
            usuario_existente = UsuarioController.buscar_por_email(db, email)
            if usuario_existente and usuario_existente.id != usuario_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email '{email}' já está em uso"
                )
            usuario.email = email.lower()

        # Valida e atualiza senha
        if senha is not None:
            if not UsuarioController._validar_senha(senha):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Senha deve ter no mínimo 6 caracteres"
                )
            usuario.senha = UsuarioController._hash_senha(senha)

        if is_admin is not None:
            usuario.is_admin = is_admin

        try:
            db.commit()
            db.refresh(usuario)
            return usuario
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao atualizar usuário"
            ) from e

# pylint: disable=duplicate-code
    @staticmethod
    def deletar(db: Session, usuario_id: int) -> bool:
        """Deleta um usuário."""
        usuario = UsuarioController.buscar_por_id(db, usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário com ID {usuario_id} não encontrado"
            )

        db.delete(usuario)
        db.commit()
        return True

    @staticmethod
    def autenticar(db: Session, email: str, senha: str) -> Optional[Usuario]:
        """Autentica um usuário verificando email e senha."""
        usuario = UsuarioController.buscar_por_email(db, email.lower())
        if not usuario:
            return None
        if not UsuarioController._verificar_senha(senha, usuario.senha):
            return None
        return usuario
