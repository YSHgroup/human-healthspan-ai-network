# Database

SQLAlchemy models are registered in `app.models.domain`. Alembic migrations live in `app/db/migrations/versions/`.

Run schema changes from `apps/api`:

```text
alembic upgrade head
alembic revision --autogenerate -m "describe change"
```

The API container applies existing migrations before starting Uvicorn. Development/test mode can also create tables automatically for local SQLite use.
