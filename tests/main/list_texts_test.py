"""Test list request"""
import json
from bson import ObjectId

from tests.main.conftest import texts, get_detail


def test__list_ok(client, headers, user_id: ObjectId, text_db):
    """_Should list of texts without the content for the logged user"""
    texts.find.return_value = [text_db]

    resp = client.get('/text/list', headers=headers)
    texts.find.assert_called_with({'owner': user_id})
    assert resp.status_code == 200

    resp_data = json.loads(resp.content)
    assert resp_data[0]['id'] == str(text_db['_id'])
    assert resp_data[0]['owner'] == str(user_id)
    assert resp_data[0]['sourceLang'] == text_db['source_lang']
    assert resp_data[0]['targetLang'] == text_db['target_lang']
    assert resp_data[0]['author'] is None
    assert resp_data[0]['description'] is None
    assert 'content' not in resp_data[0]


def test__list_no_jwt(client):
    """Should check access token"""
    resp = client.get('/text/list', headers={})

    assert resp.status_code == 401
    assert get_detail(resp.content) == "Missing Authorization Header"
