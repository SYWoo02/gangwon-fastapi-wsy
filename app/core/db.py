import logging
import os
import chromadb
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("chroma")

class ChromaDBConfig:
    def __init__(self):
        self.host = os.getenv("CHROMA_HOST", "localhost")
        self.port = int(os.getenv("CHROMA_PORT", "8800"))
        self.collection_name = os.getenv("CHROMA_COLLECTION_NAME", "upstage_embeddings")
        logger.info(self.host, self.port, self.collection_name)


class ChromaDBConnection:
    _instance: Optional['ChromaDBConnection'] = None
    _client: Optional[chromadb.HttpClient] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            config = ChromaDBConfig()
            self._client = chromadb.HttpClient(host=config.host, port=config.port)

    @property
    def client(self) -> chromadb.HttpClient:
        return self._client

    def get_collection(self, collection_name: str = None):
        config = ChromaDBConfig()
        name = collection_name or config.collection_name
        return self._client.get_or_create_collection(
            name=name,
            metadata={"description": "Upstage Solar2 embeddings collection"}
        )


def get_chroma_client() -> chromadb.HttpClient:
    """ChromaDB 클라이언트를 반환하는 의존성 함수"""
    connection = ChromaDBConnection()
    return connection.client


def get_chroma_collection(collection_name: str = None):
    """ChromaDB 컬렉션을 반환하는 의존성 함수"""
    connection = ChromaDBConnection()
    return connection.get_collection(collection_name)