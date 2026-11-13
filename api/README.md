# Backend API

Python + FastAPI modular-monolith foundation. The only implemented endpoint is `GET /healthz`; it is a liveness check and does not verify database or external-service readiness.

Feature routes, persistence, authentication, authorization, audit services, and compatibility adapters are planned work. Add them within domain modules and enforce all permissions at the API boundary.

## Local development

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e "api[dev]"
uvicorn app.main:asgi_app --app-dir api --reload --port 8000
```
