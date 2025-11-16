"""Módulo principal da aplicação ImuneTrack."""
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from app.database import Base, engine
from app.Usuario.routes import router as usuario_router
from app.Vacina.routes import router as vacina_router
from app.HistoricoVacina.routes import router as historico_router


def criar_tabelas_com_retry(retries=10, delay=3):
    """Cria tabelas no banco de dados com retry caso o banco ainda não esteja pronto."""
    for i in range(retries):
        try:
            Base.metadata.create_all(bind=engine)
            print("Tabelas criadas com sucesso!")
            break
        except OperationalError:
            print(f"[{i+1}/{retries}] Banco ainda não pronto, tentando novamente em {delay}s...")
            time.sleep(delay)
    else:
        raise RuntimeError("Não foi possível conectar ao banco de dados após várias tentativas.")

criar_tabelas_com_retry()

# Cria a aplicação FastAPI
app = FastAPI(title="ImuneTrack API")

# Adiciona CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui as rotas
app.include_router(usuario_router)
app.include_router(vacina_router)
app.include_router(historico_router, prefix="/usuarios")

@app.get("/")
async def root():
    """endpoint raiz"""
    return {"message": "Bem-vindo ao ImuneTrack!"}
