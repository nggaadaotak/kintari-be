from pydantic import BaseModel
from typing import Optional


class ChatQuerySchema(BaseModel):
    query: str
    context: Optional[str] = None


class ChatResponseSchema(BaseModel):
    query: str
    response: str
    source: Optional[str] = None
