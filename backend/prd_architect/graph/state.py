from typing import Optional
from pydantic import BaseModel


class PRDState(BaseModel):
    concept: str
    market_context: Optional[str] = None
    user_personas: Optional[str] = None
    user_journeys: Optional[str] = None
    acceptance_criteria: Optional[str] = None
