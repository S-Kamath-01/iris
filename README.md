# IRIS — Information Retrieval & Indexing System

> 🚧 **Status:** In Progress (Phase 1 Complete)

IRIS is a production-oriented backend search engine built from scratch over the **20 Newsgroups** dataset (~18,000 documents). It demonstrates core backend engineering, Information Retrieval (IR), and database concepts by implementing an **in-memory inverted index**, **BM25 relevance ranking**, and a scalable REST API using **FastAPI** and **PostgreSQL**.

---

## Features

### Implemented
- ✅ FastAPI project setup
- ✅ PostgreSQL integration
- ✅ SQLAlchemy ORM
- ✅ Alembic database migrations
- ✅ Environment-based configuration
- ✅ Database session management
- ✅ Document ORM model

### Planned
- Document ingestion & CRUD APIs
- Custom in-memory inverted index (HashMap → Posting Lists)
- Text preprocessing (tokenization, stopword removal, stemming)
- BM25 relevance ranking
- Keyword search with Top-K retrieval
- JWT authentication
- Search history
- Logging & exception handling
- Dockerized deployment
- Redis caching (stretch goal)

---

## Tech Stack

| Category | Technologies |
|----------|--------------|
| Backend | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Authentication | JWT |
| NLP | NLTK |
| Testing | pytest |
| Containerization | Docker, Docker Compose |
| Caching *(Stretch)* | Redis |

---

## Project Structure

```text
iris/
├── app/
│   ├── main.py                 # FastAPI application entrypoint
│   ├── api/
│   │   └── v1/                 # Versioned REST endpoints
│   ├── core/                   # Configuration & constants
│   ├── db/                     # Database engine & session
│   ├── documents/              # Document model, schemas, repository, service
│   ├── indexing/               # Tokenizer, posting lists, inverted index
│   ├── search/                 # BM25 ranking & search engine
│   ├── auth/                   # JWT authentication
│   └── utils/
├── tests/
├── alembic/
├── docker-compose.yml
└── requirements.txt
```

---

## Roadmap

| Phase | Status | Description |
|------|------|-------------|
| Phase 1 | ✅ Complete | Project setup, FastAPI, PostgreSQL, SQLAlchemy, Alembic, initial models |
| Phase 2 | 🚧 In Progress | Document ingestion, CRUD APIs, Pydantic validation |
| Phase 3 | ⏳ Planned | Tokenization, inverted index, posting lists, DB persistence |
| Phase 4 | ⏳ Planned | Keyword search, BM25 ranking, Top-K retrieval |
| Phase 5 | ⏳ Planned | JWT authentication, search history, logging, error handling |
| Phase 6 | ⏳ Planned | Testing, Docker, Docker Compose, deployment |
| Stretch | ⭐ Planned | Redis caching, Boolean/Phrase search, snippet generation, autocomplete |

---

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL
- Git

### Clone the repository

```bash
git clone <repository-url>
cd iris
```

### Create a virtual environment

```bash
python -m venv venv
```

**Windows**

```powershell
.\venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file in the project root.

```env
DATABASE_URL=postgresql://<username>:<password>@localhost:5432/iris_db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Create the database

```sql
CREATE DATABASE iris_db;
```

### Apply migrations

```bash
alembic upgrade head
```

### Start the server

```bash
uvicorn app.main:app --reload
```

The API documentation will be available at:

```
http://localhost:8000/docs
```

---

## Running Tests

```bash
pytest
```

---

## Learning Objectives

This project is built to explore and demonstrate:

- Backend API development
- Database design and ORM usage
- Information Retrieval systems
- Inverted Index construction
- BM25 relevance ranking
- Authentication & Authorization
- Software architecture and clean code
- Docker-based deployment
- Testing and maintainability

---

## License

This project is licensed under the **MIT License**.