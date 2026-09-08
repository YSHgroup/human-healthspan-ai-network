from pydantic import BaseModel, Field

class ResearchQuestionCreate(BaseModel):
    project_id: str
    title: str = Field(min_length=3, max_length=500)
    description: str = Field(min_length=1, max_length=10000)

class ResearchQuestionOut(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    evidence_status: str
