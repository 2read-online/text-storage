"""Web application"""
import logging
from bson import ObjectId
from fastapi import FastAPI, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pymongo.collection import Collection
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import CONFIG
from app.db import get_text_collection, Text, TextDetail
from app.schemas import CreateTextRequest, ChangeCursorRequest

logging.basicConfig(level='DEBUG')

texts: Collection = get_text_collection()

app = FastAPI()


@AuthJWT.load_config
def get_config():
    """Load settings
    """
    return CONFIG


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(_request: Request, exc: AuthJWTException):
    """
    JWT exception
    :param _request:
    :param exc:
    :return:
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


def get_current_user(req: Request) -> ObjectId:
    """Get ID of authorized user
        """
    authorize = AuthJWT(req)
    authorize.jwt_required()
    return ObjectId(authorize.get_jwt_subject())


def find_text_and_check_permission(text_id: ObjectId, user_id: ObjectId) -> Text:
    """
    Find text in DB and check its owner
    :param text_id: text ID
    :param user_id: owner ID
    :return: found text document
    """
    text_db = texts.find_one({'_id': text_id})
    if text_db is None:
        raise HTTPException(status_code=404, detail="Text not found")
    if text_db['owner'] != user_id:
        raise HTTPException(status_code=403, detail="You have no permission to remove this text")
    return Text.from_db(text_db)


@app.get('/text/get/{text_id}')
def get_text(text_id: str, user_id: ObjectId = Depends(get_current_user)):
    """Get text from DB by its ID
    """
    return find_text_and_check_permission(ObjectId(text_id), user_id)


@app.post('/text/create')
def create_text(req: CreateTextRequest, user_id: ObjectId = Depends(get_current_user)):
    """Create a new text
    """
    text_db = texts.find_one({'title': req.title, 'owner': user_id})
    if text_db is not None:
        raise HTTPException(status_code=409, detail="You have already a text with this title")

    text = Text(owner=user_id, **req.dict())
    text_id = texts.insert_one(text.db()).inserted_id
    return {'id': str(text_id)}


@app.get('/text/list')
def list_texts(user_id: ObjectId = Depends(get_current_user)):
    """List texts of the user
    """
    texts_db = texts.find({'owner': user_id})
    return [TextDetail.from_db(text) for text in texts_db]


@app.delete('/text/remove/{text_id}')
def remove_text(text_id: str, user_id: ObjectId = Depends(get_current_user)):
    """Remove text
    """
    text_id = ObjectId(text_id)
    _ = find_text_and_check_permission(text_id, user_id)
    texts.delete_one({'_id': text_id})
    return {}


@app.post('/text/cursor/{text_id}')
def change_cursor(req: ChangeCursorRequest, text_id: str, user_id: ObjectId = Depends(get_current_user)):
    """Change reading cursor
    """
    text_id = ObjectId(text_id)
    text = find_text_and_check_permission(text_id, user_id)
    text.cursor = req.cursor

    texts.replace_one({'_id': text_id}, text.db())
    return {}
