"""Module for working with MongoDB"""

import logging
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from pydantic import BaseModel, BaseConfig, Field
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import OperationFailure
from typing import Optional

from app.config import CONFIG

logger = logging.getLogger('db')


def get_text_collection():
    """Get or setup user collection from MongoDB"""
    client = MongoClient(CONFIG.mongodb_url)
    db: Database = client.prod
    texts: Collection = db.texts

    try:
        texts.create_index('user_id')
    except OperationFailure:
        logger.warning('User ID index already created')
    return texts


class OID(str):
    """Wrapper around ObjectId"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        """Validate ID
        """
        try:
            return ObjectId(str(v))
        except InvalidId as err:
            raise ValueError("Not a valid ObjectId") from err


class Text(BaseModel):
    id: Optional[OID] = Field(alias='_id')
    owner: OID
    title: str
    author: Optional[str]
    description: Optional[str]
    content: str

    class Config(BaseConfig):
        """Config
        """
        allow_population_by_field_name = True  # << Added
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),  # pylint: disable=unnecessary-lambda
            ObjectId: lambda oid: str(oid),  # pylint: disable=unnecessary-lambda
        }

    @classmethod
    def from_db(cls, obj: dict):
        """Load model from DB document
        """
        if obj is None:
            return None

        return Text(**obj)
