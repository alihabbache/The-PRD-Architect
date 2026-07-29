from pydantic import BaseModel


class GenerateRequest(BaseModel):
    concept: str


class HealthResponse(BaseModel):
    status: str
