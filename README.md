# IRIS — Information Retrieval & Indexing System

> 🚧 **Project Status: In Progress** — actively being built. This README reflects the current
> state and is updated as development progresses. See [Roadmap](#roadmap) for what's done vs
> planned.

A backend information retrieval system that indexes a document corpus and exposes REST APIs
for keyword search and relevance-ranked retrieval, built over the 20 Newsgroups dataset
(~18,000 documents).

## Features

- Document ingestion and CRUD APIs
- Custom in-memory inverted index (HashMap → posting lists), persisted to PostgreSQL
- Text preprocessing: tokenization, stopword removal, stemming
- BM25-based relevance ranking with top-k retrieval
- JWT authentication, protected endpoints, and per-user search history
- Dockerized deployment with Postgres and (optionally) Redis caching

## Tech Stack

- **API:** FastAPI
- **Database:** PostgreSQL, SQLAlchemy ORM, Alembic migrations
- **Auth:** JWT
- **Caching (optional):** Redis
- **NLP:** NLTK
- **Testing:** pytest
- **Containerization:** Docker, Docker Compose

## Project Structure

```
iris/
├── app/
│   ├── main.py                 # FastAPI app entrypoint
│   ├── api/v1/                 # versioned route handlers
│   ├── core/                   # config, constants
│   ├── db/                     # DB engine/session setup
│   ├── documents/              # document model, schema, repository, service
│   ├── indexing/               # tokenizer, inverted index, posting lists
│   ├── search/                 # BM25 ranking, search engine
│   ├── auth/                   # JWT auth
│   └── utils/
├── tests/
├── alembic/                    # DB migrations
├── docker-compose.yml
└── requirements.txt
```

## Roadmap

- [x] Phase 1 — Project setup, FastAPI, PostgreSQL, SQLAlchemy, Alembic, initial models
- [x] Phase 2 — Document ingestion, CRUD APIs, Pydantic validation
- [x] Phase 3 — Tokenization, inverted index, posting lists, DB persistence
- [ ] Phase 4 — Keyword search, BM25 ranking, top-k retrieval
- [ ] Phase 5 — JWT auth, search history, logging, error handling
- [ ] Phase 6 — Tests, Docker, Docker Compose, deployment`
- [ ] Stretch — Redis caching, boolean/phrase search, snippet generation, autocomplete

## Getting Started

### Prerequisites
- Python 3.12+
- PostgreSQL running locally (or via Docker)

### Setup

```bash
git clone <repo-url>
cd iris
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/iris_db
SECRET_KEY=<your-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Create the database:

```sql
CREATE DATABASE iris_db;
```

Run migrations:

```bash
alembic upgrade head
```

Start the server:

```bash
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

## Running Tests

```bash
pytest
```

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.