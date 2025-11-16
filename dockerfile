# Estágio 1: Build (para instalar dependências)
# Escolha uma imagem base de Python. A versão 3.11 ou 3.12 é recomendada.
FROM python:3.11-slim AS build

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala o Poetry, se você o estiver usando para gerenciar dependências
# (Se você usa pip/requirements.txt, pule este passo e use pip install no lugar)
# RUN pip install poetry

# Copia e instala as dependências
# Se você usa requirements.txt:
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Se você usa Poetry (recomendado para projetos mais complexos):
# COPY pyproject.toml poetry.lock ./
# RUN poetry install --no-root --no-dev

# Estágio 2: Produção (a imagem final, mais leve)
# Usa uma imagem base menor, ideal para produção
FROM python:3.11-slim AS production

# Define variáveis de ambiente (pode ser sobrescrito no Render)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copia as dependências e arquivos da aplicação do estágio de build
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . /app

# Comando de Inicialização (CMD)
# Isso substitui a linha 'command:' do seu docker-compose para produção.
# Usamos Gunicorn com Uvicorn workers para produção, que é mais robusto que apenas uvicorn.
# Substitua 'app.main:app' pelo caminho correto para sua instância FastAPI
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]

# Exponha a porta (Render a detecta, mas é bom para documentação)
EXPOSE 8000