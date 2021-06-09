import json
from bson import ObjectId

from tests.app.conftest import texts


def test__list_ok(client, headers, user_id: ObjectId):
    """Should pass valid request and return access token"""
    text_detail = {
        '_id': str(ObjectId()),
        'owner': str(user_id),
        'title': 'Title',
        'content': 'Content1',
        'author': None,
        'description': None
    }
    texts.find.return_value = [text_detail]

    resp = client.get('/text/list', headers=headers)
    texts.find.assert_called_with({'owner': user_id})
    assert resp.status_code == 200
    assert json.loads(resp.content) == [text_detail]


def test__list_no_jwt(client):
    resp = client.get('/text/list', headers={})

    assert resp.status_code == 401
    assert json.loads(resp.content)['detail'] == "Missing Authorization Header"
