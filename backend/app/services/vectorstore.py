import os
import faiss
import json
import numpy as np
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.index_path = settings.VECTOR_INDEX_PATH
        self.index_file = os.path.join(self.index_path, "index.faiss")
        self.mapping_file = os.path.join(self.index_path, "mappings.json")
        self.index = None
        self.mappings = {} # vector_id (int) -> chunk_id (str)
        self.next_id = 0
        self._ensure_dir()
        self.load()

    def _ensure_dir(self):
        os.makedirs(self.index_path, exist_ok=True)

    def load(self):
        if os.path.exists(self.index_file) and os.path.exists(self.mapping_file):
            try:
                self.index = faiss.read_index(self.index_file)
                with open(self.mapping_file, 'r') as f:
                    data = json.load(f)
                    self.mappings = {int(k): v for k, v in data["mappings"].items()}
                    self.next_id = data["next_id"]
                logger.info(f"Loaded vector store with {self.index.ntotal} vectors.")
            except Exception as e:
                logger.error(f"Failed to load vector store: {e}")
                self._init_empty()
        else:
            self._init_empty()

    def _init_empty(self):
        self.index = faiss.IndexIDMap(faiss.IndexFlatL2(self.dimension))
        self.mappings = {}
        self.next_id = 0

    def save(self):
        faiss.write_index(self.index, self.index_file)
        data = {
            "mappings": self.mappings,
            "next_id": self.next_id
        }
        with open(self.mapping_file, 'w') as f:
            json.dump(data, f)

    def add_embeddings(self, embeddings: list[list[float]], chunk_ids: list[str]) -> list[int]:
        if not embeddings:
            return []
            
        vectors = np.array(embeddings, dtype=np.float32)
        count = vectors.shape[0]
        
        ids = np.arange(self.next_id, self.next_id + count, dtype=np.int64)
        self.index.add_with_ids(vectors, ids)
        
        assigned_ids = []
        for i, vector_id in enumerate(ids):
            vid = int(vector_id)
            self.mappings[vid] = chunk_ids[i]
            assigned_ids.append(vid)
            
        self.next_id += count
        self.save()
        return assigned_ids

    def delete_by_chunk_ids(self, chunk_ids: list[str]):
        ids_to_remove = [vid for vid, cid in self.mappings.items() if cid in chunk_ids]
        if not ids_to_remove:
            return
            
        ids_array = np.array(ids_to_remove, dtype=np.int64)
        self.index.remove_ids(ids_array)
        
        for vid in ids_to_remove:
            del self.mappings[vid]
            
        self.save()

    def search(self, query_embedding: list[float], top_k: int) -> list[dict]:
        if not self.index or self.index.ntotal == 0:
            return []
        query_vector = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query_vector, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and int(idx) in self.mappings:
                chunk_id = self.mappings[int(idx)]
                sim_score = 1.0 / (1.0 + float(distances[0][i]))
                results.append({"chunk_id": chunk_id, "score": sim_score})
        return results

vector_store = VectorStore(dimension=768)
