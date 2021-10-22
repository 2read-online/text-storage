"""Test CreateTextRequest"""
from app.schemas import CreateTextRequest


def test__source_target_lan_validation():
    """Source and target languages can be the same
    """
    CreateTextRequest(title='Title', content='Some text', sourceLang='eng', targetLang='eng')
