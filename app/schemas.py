"""Schemas for HTTP requests"""
from typing import Optional

from pydantic import BaseModel, Field


class CreateTextRequest(BaseModel):
    """Create text request
    """
    title: str = Field(max_length=127)
    content: str = Field(max_length=2 ** 20)
    language: str = Field(max_length=3, min_length=3)
    author: Optional[str] = Field(max_length=127)
    description: Optional[str] = Field(max_length=512)


class ChangeCursorRequest(BaseModel):
    """Change cursor request
    """
    cursor: int = Field(ge=0)
