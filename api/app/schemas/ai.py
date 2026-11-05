"""AI chat API schemas."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    messages: list[ChatTurn] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def validate_turns(self) -> "ChatRequest":
        if self.messages[-1].role != "user":
            raise ValueError("The final chat message must be from the user")
        if sum(len(message.content) for message in self.messages) > 16000:
            raise ValueError("The chat history exceeds the maximum length")
        if any(not message.content.strip() for message in self.messages):
            raise ValueError("Chat messages cannot be blank")
        return self


class ChatResponse(BaseModel):
    answer: str
    provider: str
    model: str | None
    sources: list[str]
    source_notice: str
