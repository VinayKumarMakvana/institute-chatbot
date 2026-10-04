import re
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from app.db.models import DocumentChunkDB, DocumentDB
from app.models.document import DocumentStatus
from app.services.vectorstore import vector_store
from app.services.embeddings import embedding_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Retriever:
    async def retrieve(self, query: str, db: AsyncSession) -> List[Dict]:
        query_embedding = (await embedding_service.generate_embeddings([query]))[0]
        
        # 1. Semantic candidates
        semantic_results = vector_store.search(query_embedding, top_k=settings.RAG_TOP_K * 2)
        
        # 2. Keyword candidates
        words = [w for w in query.split() if len(w) > 3]
        keyword_results = []
        if words:
            conditions = [DocumentChunkDB.text.ilike(f"%{w}%") for w in words]
            result = await db.execute(
                select(DocumentChunkDB).where(or_(*conditions)).limit(settings.RAG_TOP_K * 2)
            )
            keyword_chunks = result.scalars().all()
            for c in keyword_chunks:
                keyword_results.append({"chunk_id": c.id, "score": settings.KEYWORD_WEIGHT})
                
        # 3. Merge and deduplicate
        merged = {}
        for r in semantic_results:
            merged[r["chunk_id"]] = r["score"] * settings.SEMANTIC_WEIGHT
        for r in keyword_results:
            if r["chunk_id"] in merged:
                merged[r["chunk_id"]] += r["score"]
            else:
                merged[r["chunk_id"]] = r["score"]
                
        # Sort by combined score
        sorted_candidates = sorted(merged.items(), key=lambda x: x[1], reverse=True)[:settings.RAG_TOP_K * 3]
        
        if settings.RAG_DEBUG:
            logger.info(f"Candidates before filtering: {len(sorted_candidates)}")
            
        # 4. Fetch chunk details and filter by active/READY documents
        valid_chunks = []
        for chunk_id, score in sorted_candidates:
            if score < settings.RAG_MIN_RELEVANCE_SCORE:
                continue
                
            chunk_res = await db.execute(select(DocumentChunkDB).where(DocumentChunkDB.id == chunk_id))
            chunk = chunk_res.scalar_one_or_none()
            if not chunk:
                continue
                
            doc_res = await db.execute(select(DocumentDB).where(DocumentDB.id == chunk.document_id))
            doc = doc_res.scalar_one_or_none()
            if not doc or doc.status != DocumentStatus.READY:
                continue
                
            # SQLite DocumentChunkDB does not have document_version natively mapped in models above, skipping version check for simplicity
                
            valid_chunks.append({
                "chunk": chunk,
                "doc": doc,
                "score": score
            })
            
            if len(valid_chunks) >= settings.RAG_TOP_K:
                break
                
        return valid_chunks

retriever = Retriever()
