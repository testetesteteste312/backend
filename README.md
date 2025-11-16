# 💉 ImuneTrack Backend

Microserviço principal do sistema **ImuneTrack**, responsável por gerenciar:
- Vacinas disponíveis;
- Histórico de vacinação de usuários;
- Integração com o serviço de autenticação (`imunetrack-auth`);
- Lógica de negócios e APIs REST.

---

## 🚀 Tecnologias

- **Python 3.11+**
- **FastAPI**
- **SQLAlchemy**
- **PostgreSQL**
- **Docker & Docker Compose**
- **Pytest**

---

## ⚙️ Estrutura do Projeto

```
imunetrack-backend/
│
├── app/
│   ├── main.py                # Ponto de entrada FastAPI
│   ├── Vacina/                # Módulo de Vacinas
│   ├── Usuario/               # Integração com Auth e dados locais
│   ├── HistoricoVacina/       # Histórico de vacinação
│   ├── database.py            # Configuração do banco
│   ├── schemas/               # Schemas Pydantic
│   └── tests/                 # Testes unitários e de integração
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## ⚙️ Configuração e Execução

### 1️⃣ Clonar o repositório

```bash
git clone https://gitlab.com/imunetrack/imunetrack-backend.git
cd imunetrack-backend
```

### 2️⃣ Criar arquivo `.env`

```
DATABASE_URL=postgresql+psycopg2://user:password@db:5432/imunetrack_backend
AUTH_SERVICE_URL=http://imunetrack-auth:8000
SECRET_KEY=your-secret-key
ALGORITHM=HS256
```

### 3️⃣ Subir com Docker Compose

```bash
docker-compose up --build
```

O serviço estará disponível em:  
👉 [http://localhost:8001/docs](http://localhost:8001/docs)

---

## 🔗 Integração com Auth

O backend consome o serviço `imunetrack-auth` para:
- Validar tokens de autenticação via middleware;
- Associar usuários aos registros de vacinas e históricos.

---

## 🧪 Testes

Para executar os testes:

```bash
docker-compose run --rm tests
```

Durante os testes, é utilizado um banco **SQLite em memória** para maior desempenho e isolamento.

---

## 🔑 Endpoints Principais

| Método | Rota | Descrição |
|--------|------|------------|
| `GET` | `/vacinas/` | Lista todas as vacinas |
| `POST` | `/vacinas/` | Cadastra nova vacina |
| `GET` | `/historico/` | Lista histórico de vacinas de um usuário |
| `POST` | `/historico/` | Adiciona registro de vacinação |
| `GET` | `/usuarios/{id}` | Busca dados de um usuário (via Auth) |

---
