from pydantic import BaseModel, Field
from typing import Optional

class ConversationRecord(BaseModel):
    dt: str                         # ISO date or datetime
    country_code: str = Field(..., min_length=2, max_length=3)
    text: str
    conversations: int = 1
    unique_users: Optional[int] = None
    # optional pre-labels
    top_category: Optional[str] = None
    primary_mode: Optional[str] = None
