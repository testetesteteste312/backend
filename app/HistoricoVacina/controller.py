""" Controlador para operações do histórico vacinal """
from typing import List, Optional, Dict, Any
from datetime import date
from dataclasses import dataclass

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, extract
from fastapi import HTTPException, status

from app.HistoricoVacina.model import HistoricoVacinal, StatusDose
from app.Vacina.model import Vacina
from app.Usuario.model import Usuario
from app.schemas import HistoricoVacinalCreate
from app.HistoricoVacina.email_services import email_service

# pylint: disable=too-many-instance-attributes, duplicate-code
@dataclass
class HistoricoVacinalData:
    """Dados para criação/atualização de histórico vacinal."""
    usuario_id: int
    vacina_id: int
    numero_dose: int
    status: StatusDose = StatusDose.PENDENTE
    data_aplicacao: Optional[date] = None
    data_prevista: Optional[date] = None
    lote: Optional[str] = None
    local_aplicacao: Optional[str] = None
    profissional: Optional[str] = None
    observacoes: Optional[str] = None

class HistoricoVacinalController:
    """Controlador para operações do histórico vacinal."""

    @staticmethod
    def criar_registro(
        db: Session,
        usuario_id: int,
        historico_data: HistoricoVacinalCreate
    ) -> HistoricoVacinal:
        """Cria um novo registro de histórico vacinal."""
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário com ID {usuario_id} não encontrado"
            )
        vacina = db.query(Vacina).filter(Vacina.id == historico_data.vacina_id).first()
        if not vacina:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vacina com ID {historico_data.vacina_id} não encontrada"
            )
        if historico_data.numero_dose < 1 or historico_data.numero_dose > vacina.doses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Número da dose deve estar entre 1 e {vacina.doses}"
            )
        historico = HistoricoVacinal(
            usuario_id=usuario_id,
            vacina_id=historico_data.vacina_id,
            numero_dose=historico_data.numero_dose,
            status=StatusDose(historico_data.status.value),
            data_aplicacao=historico_data.data_aplicacao,
            data_prevista=historico_data.data_prevista,
            lote=historico_data.lote,
            local_aplicacao=historico_data.local_aplicacao,
            profissional=historico_data.profissional,
            observacoes=historico_data.observacoes
        )
        db.add(historico)
        db.commit()
        db.refresh(historico)

    # Envia e-mail de confirmação
        try:
            sucesso = email_service.enviar_confirmacao_vacina(
                destinatario=usuario.email,
                nome_usuario=usuario.nome,
                vacina=vacina.nome,
                data=(historico_data.data_aplicacao or
                historico_data.data_prevista).strftime("%d/%m/%Y")
            )
            if sucesso:
                print(f"✅ E-mail de confirmação enviado para {usuario.email}")
        except Exception as e:
            print(f"⚠️ Falha ao enviar e-mail para {usuario.email}: {e}")

        return historico

# pylint: disable=too-many-arguments, too-many-positional-arguments
    #Lista o histórico vacinal de um usuário.
    @staticmethod
    def listar_por_usuario(
        db: Session,
        usuario_id: int,
        ano: Optional[int] = None,
        mes: Optional[int] = None,
        vacina_id: Optional[int] = None,
        status_filtro: Optional[StatusDose] = None
    ) -> List[HistoricoVacinal]:
        """Lista o histórico vacinal de um usuário com filtros opcionais."""
        query = db.query(HistoricoVacinal).options(
            joinedload(HistoricoVacinal.vacina)
        ).filter(HistoricoVacinal.usuario_id == usuario_id)

        if ano:
            query = query.filter(
                extract('year', HistoricoVacinal.data_aplicacao) == ano
            )

        if mes:
            query = query.filter(
                extract('month', HistoricoVacinal.data_aplicacao) == mes
            )

        if vacina_id:
            query = query.filter(HistoricoVacinal.vacina_id == vacina_id)

        if status_filtro:
            query = query.filter(HistoricoVacinal.status == status_filtro)

        return query.order_by(
            HistoricoVacinal.data_aplicacao.desc().nullslast(),
            HistoricoVacinal.created_at.desc()
        ).all()

    @staticmethod
    def buscar_por_id(db: Session, historico_id: int, usuario_id: int):
        """Busca um histórico pelo ID."""
        historico = db.query(HistoricoVacinal).filter(
            HistoricoVacinal.id == historico_id,
            HistoricoVacinal.usuario_id == usuario_id
        ).first()
        if not historico:
            return None

        return historico.to_dict()

    @staticmethod
    def atualizar_registro(
        db: Session,
        historico_id: int,
        usuario_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Atualiza um registro de histórico vacinal."""
        historico = db.query(HistoricoVacinal).options(
            joinedload(HistoricoVacinal.vacina)
        ).filter(
            and_(
                HistoricoVacinal.id == historico_id,
                HistoricoVacinal.usuario_id == usuario_id
            )
        ).first()

        if not historico:
            return None

        # Atualiza os campos
        for key, value in update_data.items():
            setattr(historico, key, value)

        db.commit()
        db.refresh(historico)

        # Retorna o formato esperado pelo response model
        return {
            "id": historico.id,
            "usuario_id": historico.usuario_id,
            "vacina_id": historico.vacina_id,
            "vacina_nome": historico.vacina.nome,
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

    @staticmethod
    def deletar_registro(db: Session, historico_id: int, usuario_id: int) -> bool:
        """Deleta um registro do histórico vacinal."""
        historico = db.query(HistoricoVacinal).filter(
            HistoricoVacinal.id == historico_id,
            HistoricoVacinal.usuario_id == usuario_id
        ).first()

        if not historico:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registro com ID {historico_id} não encontrado"
            )

        db.delete(historico)
        db.commit()
        return True

    @staticmethod
    def obter_estatisticas(db: Session, usuario_id: int) -> dict:
        """ Obtem estatísticas do histórico vacinal."""
        historico = db.query(HistoricoVacinal).filter(
            HistoricoVacinal.usuario_id == usuario_id
        ).all()

        total_doses = len(historico)
        doses_aplicadas = len([h for h in historico if h.status == StatusDose.APLICADA])
        doses_pendentes = len([h for h in historico if h.status == StatusDose.PENDENTE])
        doses_atrasadas = len([h for h in historico if h.status == StatusDose.ATRASADA])
        doses_canceladas = len([h for h in historico if h.status == StatusDose.CANCELADA])

        vacinas_dict = {}
        for h in historico:
            if h.vacina_id not in vacinas_dict:
                vacinas_dict[h.vacina_id] = {
                    'total_doses': h.vacina.doses,
                    'aplicadas': 0
                }
            if h.status == StatusDose.APLICADA:
                vacinas_dict[h.vacina_id]['aplicadas'] += 1

        vacinas_completas = sum(1 for v in vacinas_dict.values()
        if v['aplicadas'] >= v['total_doses'])
        vacinas_incompletas = len(vacinas_dict) - vacinas_completas

        proximas = db.query(HistoricoVacinal).options(
            joinedload(HistoricoVacinal.vacina)
        ).filter(
            and_(
                HistoricoVacinal.usuario_id == usuario_id,
                HistoricoVacinal.status == StatusDose.PENDENTE,
                HistoricoVacinal.data_prevista.isnot(None)
            )
        ).order_by(HistoricoVacinal.data_prevista).limit(5).all()

        proximas_doses = [
            {
                "vacina": h.vacina.nome,
                "dose": h.numero_dose,
                "data_prevista": h.data_prevista.isoformat()
            }
            for h in proximas
        ]

        return {
            "total_doses": total_doses,
            "doses_aplicadas": doses_aplicadas,
            "doses_pendentes": doses_pendentes,
            "doses_atrasadas": doses_atrasadas,
            "doses_canceladas": doses_canceladas,
            "vacinas_completas": vacinas_completas,
            "vacinas_incompletas": vacinas_incompletas,
            "proximas_doses": proximas_doses
        }

# pylint: disable=too-many-arguments, too-many-positional-arguments
    @staticmethod
    def marcar_dose_como_aplicada(
        db: Session,
        historico_id: int,
        usuario_id: int,
        data_aplicacao: date,
        lote: Optional[str] = None,
        local_aplicacao: Optional[str] = None,
        profissional: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Marca uma dose como aplicada."""
        historico = db.query(HistoricoVacinal).options(
            joinedload(HistoricoVacinal.vacina)
        ).filter(
            and_(
                HistoricoVacinal.id == historico_id,
                HistoricoVacinal.usuario_id == usuario_id
            )
        ).first()

        if not historico:
            return None

        historico.status = StatusDose.APLICADA
        historico.data_aplicacao = data_aplicacao
        historico.lote = lote
        historico.local_aplicacao = local_aplicacao
        historico.profissional = profissional

        db.commit()
        db.refresh(historico)

        # Include vacina_nome at the root level
        return {
            "id": historico.id,
            "usuario_id": historico.usuario_id,
            "vacina_id": historico.vacina_id,
            "vacina_nome": historico.vacina.nome,  
            "numero_dose": historico.numero_dose,
            "status": historico.status,
            "data_aplicacao": historico.data_aplicacao,
            "data_prevista": historico.data_prevista,
            "lote": historico.lote,
            "local_aplicacao": historico.local_aplicacao,
            "profissional": historico.profissional,
            "observacoes": historico.observacoes,
            "created_at": historico.created_at,
            "updated_at": historico.updated_at,
            "vacina": {
                "id": historico.vacina.id,
                "nome": historico.vacina.nome,
                "doses": historico.vacina.doses
            }
        }
