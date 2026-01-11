from app.repository.vector_repo import VectorRepository
from app.service.embedding_service import EmbeddingService

class VectorService:
    def __init__(
        self,
        vector_repository: VectorRepository,
        embedding_service: EmbeddingService,
    ):
        self.vector_repository = vector_repository
        self.embedding_service = embedding_service

    def add_documents(self, documents, metadatas=None):
        embeddings = self.embedding_service.create_embeddings(documents)
        self.vector_repository.add_documents(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search(self, query: str, n_results: int = 3):
        query_embedding = self.embedding_service.create_embedding(query)
        return self.vector_repository.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )

    def get_collection_info(self):
        return self.vector_repository.get_collection_info()