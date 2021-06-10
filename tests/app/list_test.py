"""Test list request"""
import json
from bson import ObjectId

from tests.app.conftest import texts


def test__list_ok(client, headers, user_id: ObjectId):
    """_Should list of texts without the content for the logged user"""
    text_db = {
        '_id': ObjectId(),
        'owner': user_id,
        'title': 'Title',
        'content': 'Content'
    }

    texts.find.return_value = [text_db]

    resp = client.get('/text/list', headers=headers)
    texts.find.assert_called_with({'owner': user_id})
    assert resp.status_code == 200

    resp_data = json.loads(resp.content)
    assert resp_data[0]['id'] == str(text_db['_id'])
    assert resp_data[0]['owner'] == str(user_id)
    assert resp_data[0]['author'] is None
    assert resp_data[0]['description'] is None
    assert 'content' not in resp_data[0]


def test__list_no_jwt(client):
    """Should check access token"""
    resp = client.get('/text/list', headers={})

    assert resp.status_code == 401
    assert json.loads(resp.content)['detail'] == "Missing Authorization Header"
