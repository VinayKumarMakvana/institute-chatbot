import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.rag.language_detector import language_detector
from app.services.rag.retriever import retriever
from app.services.rag.context_builder import context_builder
from app.services.rag.prompt_builder import prompt_builder
from app.services.rag.llm_provider import llm_provider
from app.services.holiday_service import holiday_service
from app.models.chat import ChatResponse, SourceReference

logger = logging.getLogger(__name__)

class RAGService:
    async def ask(self, query: str, db: AsyncSession) -> ChatResponse:
        # 1. Detect language (guaranteed to be 'hindi', 'hinglish', or 'english')
        lang_info = language_detector.detect(query)
        lang_code = lang_info.get("language_code", "english")
        
        # 2. Check Holiday & Admin announcement intelligence
        holiday_intel = None
        try:
            holiday_intel = await holiday_service.check_holidays(query, db)
        except Exception as e:
            logger.error(f"Holiday check error: {e}")
            holiday_intel = None

        # 3. Retrieve chunks from college PDFs via hybrid vector + keyword search
        candidates = []
        try:
            candidates = await retriever.retrieve(query, db)
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            candidates = []
            
        # 4. Build context from retrieved chunks
        context_str = context_builder.build(candidates) if candidates else ""
        
        # 5. Build prompt with GPT-like assistance + strict language rules + holiday intelligence
        prompt_data = prompt_builder.build(query, context_str, lang_code, holiday_intel=holiday_intel)
        
        # 6. Generate Answer via Gemini
        try:
            answer_text = await llm_provider.generate(
                prompt=prompt_data["prompt"],
                system_instruction=prompt_data["system_instruction"]
            )
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            if lang_code == "hinglish":
                answer_text = "Server par temporary traffic hai, kripya 1 minute baad dobara try karein."
            elif lang_code == "hindi":
                answer_text = "सर्वर पर अस्थायी समस्या है, कृपया कुछ समय बाद पुनः प्रयास करें।"
            else:
                answer_text = "The AI service is temporarily experiencing high traffic. Please try again in a moment."
        
        # 7. Format sources
        sources = []
        seen = set()
        for item in candidates:
            chunk = item.get("chunk")
            doc = item.get("doc")
            if not doc or not chunk:
                continue
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
