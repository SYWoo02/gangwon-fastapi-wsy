import os
from typing import List
from openai import OpenAI
from dotenv import load_dotenv

from app.repository.client.upstage_client import UpstageClient

load_dotenv()


class EmbeddingService:
    def __init__(self):
        self._client = UpstageClient()

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        # 정제 작업은 했다 가정
        return self._client.create_embeddings(texts=texts)

    def create_embedding(self, text: str) -> List[float]:
        return self._client.create_embeddings([text])[0]