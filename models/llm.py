from pydantic import BaseModel


class SourceItem(BaseModel):
    file: str
    id: int
    hybrid_score: float


class LlmResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
