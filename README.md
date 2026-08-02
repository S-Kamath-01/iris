# IRIS

IRIS is a production-style information retrieval project built around the 20 Newsgroups corpus. It combines a FastAPI backend, PostgreSQL persistence, an in-memory inverted index rebuilt at startup, BM25 ranking, JWT auth, and a lightweight Streamlit frontend for ranked search and explanations.

## What It Does

- Ingests and stores the 20 Newsgroups dataset
- Builds and persists an inverted index with posting lists and index metadata
- Reconstructs the search context from PostgreSQL on startup
- Serves authenticated BM25 search with category, snippet, and optional term-level explanation
- Exposes a Streamlit UI for login, search, and result exploration

## Architecture

```mermaid
flowchart LR
		U[User] --> S[Streamlit UI]
		S --> A[FastAPI API]
		A --> D[(PostgreSQL)]
		A --> C[SearchContext\nBM25 + Inverted Index]
		C --> A
		A --> S
```

The important constraint is that search is not recomputed from raw documents on every request. The index is persisted once, then rebuilt into memory from the database at startup.

## Tech Stack

- FastAPI
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- PyJWT
- NLTK
- pytest
- Streamlit
- Docker and Docker Compose

## Screenshots

Add two images to the repo when you have a chance:

- Login view
- Search results view

Recommended paths:

- `docs/screenshots/login.png`
- `docs/screenshots/search.png`

## Local Setup

### Prerequisites

- Python 3.12+
- PostgreSQL 16+

### Backend

```bash
git clone <repo-url>
cd iris
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/iris_db
SECRET_KEY=replace-me-with-a-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Run migrations:

```bash
alembic upgrade head
```

Start the API:

```bash
uvicorn app.main:app --reload
```

### Streamlit Frontend

In a second terminal:

```bash
cd streamlit_app
pip install -r requirements.txt
API_BASE_URL=http://localhost:8000 streamlit run app.py
```

## Docker

Start the full stack locally:

```bash
docker compose up --build
```

The API will be available on port `8000` and PostgreSQL on port `5432`.

## Deployment

The simplest Render setup is two web services plus one managed Postgres database:

1. Backend service from the root `Dockerfile`
2. Streamlit service from `streamlit_app/app.py`
3. Render Postgres, wired into `DATABASE_URL`

Suggested environment variables:

- Backend: `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `APP_ENV=production`
- Frontend: `API_BASE_URL` pointing to the deployed backend URL

If you use the included `render.yaml`, Render can provision the services with the same split architecture.

## API Examples

Authenticate:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
	-H "Content-Type: application/x-www-form-urlencoded" \
	-d "username=user@example.com&password=secret"
```

Search:

```bash
curl "http://localhost:8000/api/v1/search/?q=space+shuttle&top_k=5&explain=true" \
	-H "Authorization: Bearer <token>"
```

## Testing

```bash
pytest
```

## Notes

- Users, documents, and index metadata are persisted in PostgreSQL.
- Startup is idempotent as long as migrations and the index persistence script are run once per dataset refresh.
- Search results now include category, preview snippet, document id, score, and optional explanation data.

## License

MIT. See [LICENSE](LICENSE).