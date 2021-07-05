"""Mongodb client init."""
import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection


class Singleton(type):
    """Singleton pattern class."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MongoDbClient(metaclass=Singleton):  # pylint:disable=too-few-public-methods
    """Singleton for mongo db client."""
    def __init__(self):
        self._init_client()

    def _init_client(self):
        uri = os.getenv('MONGODB_URI', 'mongodb://localhost')
        self.client = AsyncIOMotorClient(uri)


def get_client() -> AsyncIOMotorClient:
    """Return MongoClient object."""
    return MongoDbClient().client


def get_posts_collection() -> AsyncIOMotorCollection:
    """Return posts collection from the cyclemap db."""
    motor_client = get_client()
    return motor_client['cyclemap_db']['posts_collection']
