class RetrievalService:
    """Permission-aware retrieval boundary.

    Retrieval must receive an authorization scope before querying documents, vectors or graph data.
    """

    async def retrieve(self, query: str, authorization_scope: dict) -> list[dict]:
        raise NotImplementedError
