from fastapi import FastAPI
from app.api.routes import health, users, communities, posts, research, ai

app = FastAPI(title="Human Healthspan AI Network API", version="0.1.0")

app.include_router(health.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(communities.router, prefix="/api")
app.include_router(posts.router, prefix="/api")
app.include_router(research.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
