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

# Common academic & Hinglish student typos dictionary (Google-like correction)
TYPO_MAP = {
    'exm': 'exam',
    'exms': 'exams',
    'kbb': 'kab',
    'syllbus': 'syllabus',
    'sylabus': 'syllabus',
    'syllubus': 'syllabus',
    'sylbus': 'syllabus',
    'sylabus': 'syllabus',
    'admison': 'admission',
    'admisn': 'admission',
    'admsn': 'admission',
    'semster': 'semester',
    'semstr': 'semester',
    'sem': 'semester',
    'deprtmnt': 'department',
    'dept': 'department',
    'timtbl': 'timetable',
    'timetbl': 'timetable',
    'atendnc': 'attendance',
    'attendence': 'attendance',
    'atendance': 'attendance',
    'reslt': 'result',
    'subjet': 'subject',
    'subjets': 'subjects',
    'elgibility': 'eligibility',
    'eligblity': 'eligibility',
    'collage': 'college',
    'colleg': 'college',
    'librry': 'library',
    'hostl': 'hostel',
    'scholrship': 'scholarship',
    'fclty': 'faculty',
    'crs': 'course',
    'corse': 'course',
    'projct': 'project',
    'asigmnt': 'assignment',
    'assignmnt': 'assignment',
    'notic': 'notice',
    'notis': 'notice',
    'calndr': 'calendar',
    'plcmnt': 'placement'
}

STOP_WORDS = {
    'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'in', 'to',
    'for', 'of', 'with', 'by', 'from', 'this', 'that', 'these', 'those',
    'ka', 'ki', 'ke', 'ko', 'se', 'me', 'pe', 'par', 'hai', 'hain', 'ho'
}

class Retriever:
    def _normalize_query(self, query: str) -> str:
        """Corrects typos and expands abbreviations just like Google Search."""
        tokens = re.findall(r'[a-zA-Z0-9]+', query.lower())
        corrected = [TYPO_MAP.get(t, t) for t in tokens]
        return " ".join(corrected) if corrected else query

    async def retrieve(self, query: str, db: AsyncSession) -> List[Dict]:
        normalized_query = self._normalize_query(query)
        
        # 1. Generate embedding using normalized query for superior semantic matching
        try:
            embeddings = await embedding_service.generate_embeddings([normalized_query])
            query_embedding = embeddings[0] if embeddings else None
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            query_embedding = None
        
        # 2. Semantic search in FAISS vector store
        semantic_results = []
        if query_embedding:
            try:
                semantic_results = vector_store.search(query_embedding, top_k=settings.RAG_TOP_K * 3)
            except Exception as e:
                logger.error(f"FAISS search failed: {e}")
                semantic_results = []
        
        # 3. Keyword candidate search (extract search tokens from both original and normalized queries)
        query_words = set(re.findall(r'[a-zA-Z0-9]{3,}', normalized_query.lower()))
        query_words.update(re.findall(r'[a-zA-Z0-9]{3,}', query.lower()))
        meaningful_words = [w for w in query_words if w not in STOP_WORDS]
        
        keyword_results = []
        if meaningful_words:
            try:
                conditions = [DocumentChunkDB.text.ilike(f"%{w}%") for w in meaningful_words[:6]]
                result = await db.execute(
                    select(DocumentChunkDB).where(or_(*conditions)).limit(settings.RAG_TOP_K * 3)
                )
                keyword_chunks = result.scalars().all()
                for c in keyword_chunks:
                    # Give higher keyword score for each matching keyword
                    match_count = sum(1 for w in meaningful_words if w in (c.text or "").lower())
                    kw_score = min(0.5, 0.15 * match_count)
                    keyword_results.append({"chunk_id": c.id, "score": kw_score})
            except Exception as e:
                logger.error(f"Keyword search error: {e}")
                keyword_results = []

        # 4. Hybrid Merge (Semantic + Keyword)
        merged = {}
        for r in semantic_results:
            merged[r["chunk_id"]] = r["score"] * settings.SEMANTIC_WEIGHT
            
        for r in keyword_results:
            cid = r["chunk_id"]
            if cid in merged:
                merged[cid] += r["score"]
            else:
                merged[cid] = r["score"]

        if not merged:
            return []

        # Sort candidates by combined relevance score
        sorted_candidates = sorted(merged.items(), key=lambda x: x[1], reverse=True)[:settings.RAG_TOP_K * 2]

        # 5. Fetch chunk details and filter by active/READY documents
        valid_chunks = []
        for chunk_id, score in sorted_candidates:
            # Pragmatic relevance threshold (avoids discarding valid context)
            if score < 0.20:
                continue

            chunk_res = await db.execute(select(DocumentChunkDB).where(DocumentChunkDB.id == chunk_id))
            chunk = chunk_res.scalar_one_or_none()
            if not chunk:
                continue

            doc_res = await db.execute(select(DocumentDB).where(DocumentDB.id == chunk.document_id))
            doc = doc_res.scalar_one_or_none()
            if not doc or doc.status != DocumentStatus.READY:
                continue

            valid_chunks.append({
                "chunk": chunk,
                "doc": doc,
                "score": score
            })

            if len(valid_chunks) >= settings.RAG_TOP_K:
                break

        return valid_chunks

retriever = Retriever()
