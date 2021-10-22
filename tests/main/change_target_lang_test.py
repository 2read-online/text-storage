# pylint: disable=redefined-outer-name
"""Test target lang changing"""
import pytest
from bson import ObjectId

from app.schemas import ChangeLanguageRequest
from tests.main.conftest import get_detail
from tests.main.conftest import texts


@pytest.fixture
def valid_request() -> str:
    """Valid request
    """
    return ChangeLanguageRequest(lang='ita').json()


def test__target_lang_ok(client, valid_request, headers, text_db):
    """Should change target lang of text
    """
    texts.find_one.return_value = text_db

    resp = client.post(f'/text/target_lang/{text_db["_id"]}', valid_request, headers=headers)

    text_db.update({'target_lang': 'ita'})
    texts.find_one.assert_called_with({'_id': text_db['_id']})
    texts.replace_one.assert_called_with({'_id': text_db['_id']}, text_db)
    assert resp.status_code == 200


def test__target_lang_not_exist(client, valid_request, headers, text_id):
    """Should return 404 if text doesn't exist"""
    texts.find_one.return_value = None

    resp = client.post(f'/text/target_lang/{text_id}', valid_request, headers=headers)

    assert resp.status_code == 404
    assert get_detail(resp.content) == "Text not found"


def test__target_lang_not_permission(client, valid_request, headers, text_db):
    """Should return 403 if the text doesn't belong to the user"""
    text_db['owner'] = ObjectId()
    texts.find_one.return_value = text_db

    resp = client.post(f'/text/target_lang/{text_db["_id"]}', valid_request, headers=headers)

    assert resp.status_code == 403
    assert get_detail(resp.content) == "You have no permission to remove this text"


def test__target_lang_no_jwt(client, valid_request):
    """Should check access token"""
    resp = client.post('/text/target_lang/some_id', valid_request, headers={})

    assert resp.status_code == 401
    assert get_detail(resp.content) == "Missing Authorization Header"
