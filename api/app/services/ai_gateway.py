class AIGateway:
    """Provider-independent boundary for LLM, embeddings, RAG and tools."""

    async def answer(self, user_id: int, question: str, workspace_id: int | None = None):
        # Next round: auth-aware retrieval -> citations -> model router -> audit.
        raise NotImplementedError
