"""Web application"""
from collections import Collection

import logging
from bson import ObjectId
from fastapi import FastAPI, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import CONFIG
from app.db import get_text_collection, Text
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
def create(req: CreateTextRequest, authorize: AuthJWT = Depends()):
    """Process logout request
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
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    texts_db = texts.find({'owner': ObjectId(user_id)})
    return [Text(**text) for text in texts_db]
