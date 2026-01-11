import os
from typing import List

from openai import OpenAI


class UpstageClient:

    def __init__(self):
        api_key = os.getenv("UPSTAGE_API_KEY")
        if not api_key:
            raise ValueError("UPSTAGE_API_KEY environment variable is required")
        self.client = OpenAI(api_key=api_key, base_url="https://api.upstage.ai/v1")

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        try:
            response = self.client.embeddings.create(
                model="solar-embedding-1-large-query",
                input=texts
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            raise RuntimeError(f"Failed to create embeddings: {str(e)}")

    def create_embedding(self, text: str) -> List[float]:
        return self.create_embeddings([text])[0]