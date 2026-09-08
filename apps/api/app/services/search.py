class SearchService:
    async def search(self, query: str, filters: dict | None = None) -> list[dict]:
        raise NotImplementedError
