"""Run the local API using values from the repository's .env file."""

from pathlib import Path

from dotenv import load_dotenv

API_DIRECTORY = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = API_DIRECTORY.parent
AI_DIRECTORY = REPOSITORY_ROOT / "ai"


def main() -> None:
    load_dotenv(REPOSITORY_ROOT / ".env", override=True)

    import uvicorn

    uvicorn.run(
        "app.main:asgi_app",
        app_dir=str(API_DIRECTORY),
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[str(API_DIRECTORY), str(AI_DIRECTORY)],
    )


if __name__ == "__main__":
    main()
