import numpy as np
from app.core.config import settings

class EmbeddingService:
    def __init__(self):
        self.provider = settings.AI_PROVIDER.lower()
        self.model = settings.EMBEDDING_MODEL
        self.dimension = 768
        
        if self.provider == "gemini":
            try:
                from google import genai
                self.client = genai.Client(api_key=settings.AI_API_KEY)
            except ImportError:
                self.client = None

    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
            
        if self.provider == "mock":
            # Generate deterministic mock embeddings (for tests)
            np.random.seed(42)
            return [np.random.rand(self.dimension).tolist() for _ in texts]
            
        elif self.provider == "gemini" and self.client:
            try:
                # Wrap in sync wrapper or run in executor if necessary
                response = self.client.models.embed_content(
                    model=self.model,
                    contents=texts
                )
                if isinstance(response.embeddings, list):
                    return [emb.values for emb in response.embeddings]
                return [response.embeddings.values]
            except Exception as e:
                raise Exception(f"Failed to generate embeddings: {e}")
        else:
            raise Exception("Unsupported or unconfigured AI_PROVIDER")

embedding_service = EmbeddingService()
