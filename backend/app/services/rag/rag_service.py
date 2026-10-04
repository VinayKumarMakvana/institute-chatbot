import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.rag.language_detector import language_detector
from app.services.rag.retriever import retriever
from app.services.rag.context_builder import context_builder
from app.services.rag.prompt_builder import prompt_builder
from app.services.rag.llm_provider import llm_provider
from app.models.chat import ChatResponse, SourceReference

logger = logging.getLogger(__name__)

class RAGService:
    async def ask(self, query: str, db: AsyncSession) -> ChatResponse:
        # 1. Detect language
        lang_info = language_detector.detect(query)
        lang_code = lang_info.get("language_code", "en")
        
        # 2. Retrieve chunks
        candidates = await retriever.retrieve(query, db)
        
        if not candidates:
            return ChatResponse(
                answer="I couldn't find sufficient information about this in the available documents.",
                language=lang_code,
                sources=[]
            )
            
        # 3. Build context
        context_str = context_builder.build(candidates)
        
        # 4. Build prompt
        prompt_data = prompt_builder.build(query, context_str, lang_code)
        
        # 5. Generate Answer
        answer_text = await llm_provider.generate(
            prompt=prompt_data["prompt"],
            system_instruction=prompt_data["system_instruction"]
        )
        
        # 6. Format sources
        sources = []
        seen = set()
        for item in candidates:
            chunk = item["chunk"]
            doc = item["doc"]
            doc_id = str(doc.id)
            page = chunk.page_number or 0
            key = f"{doc_id}_{page}"
            if key not in seen:
                sources.append(SourceReference(
                    document_id=doc_id,
                    document_title=doc.title or "",
                    page_start=page,
                    page_end=page
                ))
                seen.add(key)
                
        return ChatResponse(
            answer=answer_text.strip(),
            language=lang_code,
            sources=sources
        )

rag_service = RAGService()
