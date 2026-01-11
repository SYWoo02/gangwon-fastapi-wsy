from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.core.db import get_chroma_collection
from chromadb import Client
from chromadb.config import Settings

client = Client(
    Settings(
        persist_directory="/chroma/.chroma"
    )
)

class VectorRepository(ABC):
    @abstractmethod
    def add_documents(self, documents: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]] = None,
                      ids: List[str] = None):
        pass

    @abstractmethod
    def query(self, query_embeddings: List[List[float]], n_results: int = 5, include: List[str] = None) -> Dict[
        str, Any]:
        pass

    @abstractmethod
    def delete_documents(self, ids: List[str]):
        pass

    @abstractmethod
    def get_collection_info(self) -> Dict[str, Any]:
        pass


class ChromaDBRepository(VectorRepository):
    def __init__(self, collection_name: str = None):
        self.collection = get_chroma_collection(collection_name)

    def add_documents(
            self,
            documents: List[str],
            embeddings: List[List[float]],
            metadatas: List[Dict[str, Any]] = None,
            ids: List[str] = None,
    ):
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]

        if metadatas is None:
            metadatas = [{"text": doc} for doc in documents]

        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, query_embeddings: List[List[float]], n_results: int = 5, include: List[str] = None) -> Dict[
        str, Any]:
        if include is None:
            include = ["documents", "metadatas", "distances"]

        return self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            include=include
        )

    def delete_documents(self, ids: List[str]):
        self.collection.delete(ids=ids)

    def get_collection_info(self) -> Dict[str, Any]:
        return {
            "name": self.collection.name,
            "count": self.collection.count(),
            "metadata": self.collection.metadata
        }