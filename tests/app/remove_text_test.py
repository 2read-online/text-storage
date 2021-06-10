# pylint: disable=redefined-outer-name
"""Test remove text API"""
import pytest
from bson import ObjectId

from tests.app.conftest import texts, get_detail


@pytest.fixture
def text_id():
    """Random text ID"""
    return ObjectId()


def test__remove_text_ok(client, headers, user_id: ObjectId, text_id: ObjectId):
    """Should remove text by its ID"""
    text_db = {
        '_id': text_id,
        'owner': user_id,
        'title': 'Title',
        'content': 'Content'
    }

    texts.find_one.return_value = text_db

    resp = client.delete(f'/text/remove/{text_id}', headers=headers)

    texts.find_one.assert_called_with({'_id': text_id})
    texts.delete_one.assert_called_with({'_id': text_id})
    assert resp.status_code == 200


def test__remove_text_not_exist(client, headers, text_id):
    """Should return 404 if text doesn't exist"""
    texts.find_one.return_value = None

    resp = client.delete(f'/text/remove/{text_id}', headers=headers)

    texts.delete_one.asset_not_called()
    assert resp.status_code == 404
    assert get_detail(resp.content) == "Text not found"


def test__remove_text_not_permission(client, headers, text_id):
    """Should return 403 if the text doesn't belong to the user"""
    text_db = {
        '_id': text_id,
        'owner': ObjectId(),
        'title': 'Title',
        'content': 'Content'
    }

    texts.find_one.return_value = text_db

    resp = client.delete(f'/text/remove/{text_id}', headers=headers)

    texts.delete_one.asset_not_called()
    assert resp.status_code == 403
    assert get_detail(resp.content) == "You have no permission to remove this text"


def test__remove_text_no_jwt(client):
    """Should check access token"""
    resp = client.delete('/text/remove/some_id', headers={})

    assert resp.status_code == 401
    assert get_detail(resp.content) == "Missing Authorization Header"
