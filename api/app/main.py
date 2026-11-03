from fastapi import FastAPI

app = FastAPI(
    title="Human Healthspan Scientific AI Network API",
    version="0.1.0",
    description="Backend API foundation. Product workflows are not implemented yet.",
)


@app.get("/healthz", tags=["operations"])
async def health_check() -> dict[str, str]:
    """Report that the API process is responding."""
    return {"status": "ok"}
