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
from app.schemas import CreateTextRequest

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


@app.post('/text/create')
def create_text(req: CreateTextRequest, authorize: AuthJWT = Depends()):
    """Create a new text
    """
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    text_db = texts.find_one({'title': req.title, 'owner': ObjectId(user_id)})
    if text_db is not None:
        raise HTTPException(status_code=409, detail="You have already a text with this title")

    text_db = Text(owner=user_id, **req.dict())
    text_id = texts.insert_one(text_db.dict(exclude_none=True)).inserted_id
    return {'id': str(text_id)}


@app.get('/text/list')
def list_texts(authorize: AuthJWT = Depends()):
    """List texts of the user
    """
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    texts_db = texts.find({'owner': ObjectId(user_id)})
    return [TextDetail.from_db(text) for text in texts_db]


@app.delete('/text/remove/{text_id}')
def remove_text(text_id: str, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    q = {'_id': ObjectId(text_id)}
    text_db = texts.find_one(q)
    if text_db is None:
        raise HTTPException(status_code=404, detail="Text not found")

    user_id = ObjectId(authorize.get_jwt_subject())
    if text_db['owner'] != user_id:
        raise HTTPException(status_code=403, detail="You have no permission to remove this text")

    texts.delete_one(q)
    return {}
