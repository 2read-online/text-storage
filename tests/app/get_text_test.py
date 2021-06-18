# pylint: disable=redefined-outer-name
"""Test get text API"""
from bson import ObjectId

from tests.app.conftest import texts, get_detail


def test__get_text_ok(client, headers, text_db):
    """Should get text by its ID"""
    texts.find_one.return_value = text_db

    resp = client.get(f'/text/get/{text_db["_id"]}', headers=headers)

    texts.find_one.assert_called_with({'_id': text_db["_id"]})
    assert resp.status_code == 200


def test__get_text_not_exist(client, headers, text_id):
    """Should return 404 if text doesn't exist"""
    texts.find_one.return_value = None

    resp = client.get(f'/text/get/{text_id}', headers=headers)

    texts.delete_one.asset_not_called()
    assert resp.status_code == 404
    assert get_detail(resp.content) == "Text not found"


def test__get_text_not_permission(client, headers, text_db):
    """Should return 403 if the text doesn't belong to the user"""
    text_db['owner'] = ObjectId()
    texts.find_one.return_value = text_db

    resp = client.get(f'/text/get/{text_db["_id"]}', headers=headers)

    assert resp.status_code == 403
    assert get_detail(resp.content) == "You have no permission to remove this text"


def test__get_text_no_jwt(client):
    """Should check access token"""
    resp = client.get('/text/get/some_id', headers={})

    assert resp.status_code == 401
    assert get_detail(resp.content) == "Missing Authorization Header"
