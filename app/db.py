"""Module for working with MongoDB"""
import logging
from typing import Optional
from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from pydantic import BaseModel, BaseConfig, Field
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import OperationFailure


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


class MongoModel(BaseModel):
    """Base mongo document with ID"""
    id: Optional[OID]

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

        return cls(id=obj['_id'], **obj)

    def db(self) -> dict:
        """Export to mongo document"""
        data: dict = self.dict(exclude_none=True)
        if 'id' in data:
            data['_id'] = data.pop('id')

        return data


class TextDetail(MongoModel):
    """Text detail without content"""
    owner: OID
    title: str
    source_lang: str = Field(alias='sourceLang')
    target_lang: str = Field(alias='targetLang')
    author: Optional[str]
    description: Optional[str]


class Text(TextDetail):
    """Text document"""
    content: str
    cursor: int = 0
