import pymongo
from src.config import MONGODB_URI
import logging

logger = logging.getLogger(__name__)

class Database:
    _instance = None
    _client = None
    _db = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Database()
        return cls._instance
    
    def __init__(self):
        if Database._instance is not None:
            raise Exception("Cette classe est un singleton!")
        self.connect()
    
    def connect(self):
        try:
            logger.info("Connexion à MongoDB...")
            self._client = pymongo.MongoClient(MONGODB_URI)
            self._db = self._client.get_database("messenger_bot")
            logger.info("Connexion à MongoDB établie")
        except Exception as e:
            logger.error(f"Erreur de connexion à MongoDB: {str(e)}")
            raise
    
    def get_collection(self, collection_name):
        if self._db is None:
            self.connect()
        return self._db[collection_name]
    
    def close(self):
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("Connexion à MongoDB fermée")