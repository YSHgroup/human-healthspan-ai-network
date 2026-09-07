# Human Healthspan AI Network — MVP Starter

A basic, extensible starter project based on the MVP architecture:
- Next.js/React/TypeScript web app
- FastAPI/Python API
- PostgreSQL + pgvector-ready data layer
- Redis-ready infrastructure
- OpenSearch-ready search layer
- S3-compatible object storage
- AI gateway boundary for RAG/model providers
- Modular-monolith structure for the first release

## Run
### API
```bash
cd api
python -m venv .venv
# activate the venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Web
```bash
cd web
npm install
npm run dev
```

The implementation is intentionally minimal. It provides the foundation to extend in the next development round.
