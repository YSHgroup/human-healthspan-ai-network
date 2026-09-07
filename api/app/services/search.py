class SearchService:
    """Unified keyword/semantic search boundary."""

    async def search(self, query: str, filters: dict | None = None):
        # Next round: OpenSearch + pgvector hybrid retrieval.
        return []
