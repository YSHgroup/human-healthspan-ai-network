class AIGateway:
    """Provider-neutral AI boundary.

    Round 2 deliberately does not hard-code an LLM provider. Later adapters can implement
    chat, embeddings, structured output and tool calls behind this interface.
    """

    async def answer(self, prompt: str, context: list[dict]) -> dict:
        raise NotImplementedError("Attach an approved model provider in the next implementation pass.")
