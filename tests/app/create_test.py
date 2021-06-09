import json
import pytest
from bson import ObjectId

from app.schemas import CreateTextRequest
from tests.app.conftest import texts


@pytest.fixture
def valid_request():
    return CreateTextRequest(title='Title', content='Content').json();


def test__create_ok(client, headers, valid_request, user_id: ObjectId):
    texts.find_one.return_value = None

    resp = client.post('/text/create', valid_request, headers=headers)

    assert resp.status_code == 200

    texts.find_one.assert_called_with({'title': 'Title', 'owner': ObjectId('60c0b2d700569d97f8a93dcd')})
    texts.insert_one.assert_called_with(
        {'owner': user_id, 'title': 'Title', 'content': 'Content'})


def test__create_no_jwt(client, valid_request):
    resp = client.post('/text/create', valid_request, headers={})

    assert resp.status_code == 401
    assert json.loads(resp.content)['detail'] == "Missing Authorization Header"


def test__create_title_exists(client, headers, valid_request):
    texts.find_one.return_value = {}

    resp = client.post('/text/create', valid_request, headers=headers)

    assert resp.status_code == 409
    assert json.loads(resp.content)['detail'] == "You have already a text with this title"
