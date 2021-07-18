"""Schemas for HTTP requests"""
from typing import Optional

from pydantic import BaseModel, Field, validator


class CreateTextRequest(BaseModel):
    """Create text request
    """
    title: str = Field(max_length=127)
    content: str = Field(max_length=2 ** 20)
    source_lang: str = Field(max_length=3, min_length=3, alias='sourceLang')
    target_lang: str = Field(max_length=3, min_length=3, alias='targetLang')
    author: Optional[str] = Field(max_length=127)
    description: Optional[str] = Field(max_length=512)

    @validator('target_lang')
    def passwords_match(cls, v, values, **kwargs):  # pylint: disable=no-self-argument,no-self-use,unused-argument
        """Check if target and source languages are different
        """
        if 'source_lang' in values and v == values['source_lang']:
            raise ValueError('Target and source language cannot be the same')
        return v


class ChangeCursorRequest(BaseModel):
    """Change cursor request
    """
    cursor: int = Field(ge=0)
