import pytest
from pydantic import ValidationError

from app.schemas import CreateTextRequest


def test__source_target_lan_validation():
    """Source and target languages can be the same
    """
    with pytest.raises(ValidationError, match='Target and source language cannot be the same'):
        CreateTextRequest(title='Title', content='Some text', sourceLang='eng', targetLang='eng')
