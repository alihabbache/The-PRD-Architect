from pydantic import BaseModel, Field, field_validator


class GenerateRequest(BaseModel):
    concept: str = Field(
        min_length=10,
        max_length=2000,
        description="Product concept description (10–2000 characters)",
    )

    @field_validator("concept")
    @classmethod
    def strip_and_validate(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 10:
            raise ValueError("concept must be at least 10 characters after stripping whitespace")
        return v


class HealthResponse(BaseModel):
    status: str
