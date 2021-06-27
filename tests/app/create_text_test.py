# pylint: disable=redefined-outer-name
"""Test create text request"""
import json

import pytest
from bson import ObjectId

from tests.app.conftest import texts, get_detail


@pytest.fixture
def valid_request():
    """Valid HTTP request"""
    return json.dumps({
        'title': 'Title', 'content': 'Content',
        'language': 'eng', 'translationLanguage': 'rus'
    })


def test__create_ok(client, headers, valid_request, user_id: ObjectId):
    """Should creat a new text in DB for logged user"""
    texts.find_one.return_value = None

    resp = client.post('/text/create', valid_request, headers=headers)

    assert resp.status_code == 200

    texts.find_one.assert_called_with({'title': 'Title', 'owner': user_id})
    texts.insert_one.assert_called_with(
        {'owner': user_id, 'title': 'Title', 'content': 'Content', 'cursor': 0, 'language': 'eng',
         'translation_language': 'rus'})


def test__create_no_jwt(client, valid_request):
    """Should check access token"""
    resp = client.post('/text/create', valid_request, headers={})

    assert resp.status_code == 401
    assert get_detail(resp.content) == "Missing Authorization Header"


def test__create_title_exists(client, headers, valid_request):
    """Should not create a text with the same title"""
    texts.find_one.return_value = {}

    resp = client.post('/text/create', valid_request, headers=headers)

    assert resp.status_code == 409
    assert get_detail(resp.content) == "You have already a text with this title"
