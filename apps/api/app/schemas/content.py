from pydantic import BaseModel, Field

class PostCreate(BaseModel):
    author_id: str
    body: str = Field(min_length=1, max_length=10000)

class PostOut(BaseModel):
    id: str
    author_id: str
    body: str
