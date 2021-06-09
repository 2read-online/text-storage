from pydantic import BaseModel, Field
from typing import Optional


class CreateTextRequest(BaseModel):
    title: str = Field(max_length=127)
    content: str = Field(max_length=2 ** 20)
    author: Optional[str] = Field(max_length=127)
    description: Optional[str] = Field(max_length=512)
