# Architecture

```mermaid
flowchart TD
    U[User] --> S[Streamlit Frontend]
    S --> A[FastAPI Backend]
    A --> J[JWT Authentication]
    J --> C[SearchContext]
    C --> B[In-memory BM25 Index]
    B --> N[(Neon PostgreSQL)]

    D[20 Newsgroups Dataset] --> P[Preprocessing]
    P --> I[Inverted Index]
    I --> G[Persist to PostgreSQL]
    G --> R[Rebuild SearchContext at startup]
    R --> C
```

## Notes

- Search is served from an in-memory index rebuilt at application startup.
- PostgreSQL stores the durable source data, index metadata, and authentication records.
- Neon is used as managed PostgreSQL only; no Neon-specific SDKs are required.