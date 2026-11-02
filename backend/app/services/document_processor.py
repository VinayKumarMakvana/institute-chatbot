import os
import re
import pdfplumber
import logging
from datetime import datetime, timezone
from app.core.config import settings
from app.models.document import DocumentStatus
from app.services.vectorstore import vector_store
from app.services.embeddings import embedding_service
from app.db.sqlite import AsyncSessionLocal
from sqlalchemy.future import select
from app.db.models import DocumentDB, DocumentChunkDB, UserDB, NotificationDB
import uuid

logger = logging.getLogger(__name__)

def utc_now():
    return datetime.utcnow()

def is_garbled_or_empty(pages_data: list[dict]) -> bool:
    """Checks if extracted text is empty, scanned image, or garbled font noise."""
    if not pages_data:
        return True
    total_text = " ".join([p.get("text", "") for p in pages_data])
    if len(total_text.strip()) < 40:
        return True
    
    # Check ratio of real alphanumeric words vs total length
    words = re.findall(r'[a-zA-Z0-9]{3,}', total_text)
    if len(total_text) > 200 and len(words) < 20:
        return True
    return False

class DocumentProcessor:
    async def process_document(self, document_id: str):
        async with AsyncSessionLocal() as db:
            try:
                result = await db.execute(select(DocumentDB).where(DocumentDB.id == document_id))
                doc = result.scalar_one_or_none()
                if not doc:
                    logger.error(f"Document {document_id} not found.")
                    return

                await self._update_status(db, doc, DocumentStatus.EXTRACTING, "Extracting text from PDF")
                pages_data = self._extract_text(doc.file_path)
                
                # Intelligent OCR Fallback: If text is scanned image or corrupted font encoding, use Gemini Vision OCR
                if is_garbled_or_empty(pages_data):
                    logger.info(f"PDF {doc.original_filename} has scanned/garbled text. Running Gemini Multimodal OCR...")
                    await self._update_status(db, doc, DocumentStatus.EXTRACTING, "Running AI OCR on scanned PDF")
                    pages_data = await self._extract_with_gemini_ocr(doc.file_path)

                await self._update_status(db, doc, DocumentStatus.CLEANING, "Cleaning extracted text")
                pages_data = self._clean_text(pages_data)
                
                await self._update_status(db, doc, DocumentStatus.CHUNKING, "Chunking text")
                chunks = self._chunk_text(pages_data, doc.id, doc.version)
                
                await self._update_status(db, doc, DocumentStatus.EMBEDDING, "Generating embeddings")
                texts = [c.text for c in chunks]
                embeddings = await embedding_service.generate_embeddings(texts)
                
                await self._update_status(db, doc, DocumentStatus.INDEXING, "Indexing into vector store")
                chunk_ids = [c.id for c in chunks] 
                vector_ids = vector_store.add_embeddings(embeddings, chunk_ids)
                
                # Insert chunks to sqlite
                if chunks:
                    db.add_all(chunks)
                    await db.commit()
                    
                # Mark READY
                doc.status = DocumentStatus.READY
                doc.processing_stage = "Document is ready"
                doc.total_pages = len(pages_data)
                doc.total_chunks = len(chunks)
                doc.processed_at = utc_now()
                await db.commit()
                logger.info(f"Document {document_id} successfully processed with {len(chunks)} chunks.")

                # Broadcast notification to all active students
                try:
                    users_res = await db.execute(select(UserDB).where(UserDB.is_active == True, UserDB.role == "USER"))
                    active_students = users_res.scalars().all()
                    doc_notifs = []
                    cat_display = f" ({doc.category})" if doc.category else ""
                    for st in active_students:
                        doc_notifs.append(NotificationDB(
                            user_id=st.id,
                            type="DOCUMENT",
                            title=f"New Study Material: {doc.title}",
                            message=f"'{doc.title}'{cat_display} has been added to the library. You can now view it and ask the AI chatbot questions about it.",
                            update_id=doc.id,
                            is_read=False,
                            created_at=utc_now()
                        ))
                    if doc_notifs:
                        db.add_all(doc_notifs)
                        await db.commit()
                        logger.info(f"Dispatched {len(doc_notifs)} notifications for new document {doc.title}")
                except Exception as ne:
                    logger.error(f"Failed to create document notification: {ne}")
                
            except Exception as e:
                logger.error(f"Processing failed for {document_id}: {e}")
                await self._update_status(db, doc, DocumentStatus.FAILED, f"Processing failed: {str(e)}", error=str(e))

    async def _update_status(self, db, doc: DocumentDB, status: str, stage: str, error: str = None):
        doc.status = status
        doc.processing_stage = stage
        doc.updated_at = utc_now()
        if error:
            doc.processing_error = error
        await db.commit()

    def _extract_text(self, file_path: str) -> list[dict]:
        pages_data = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        pages_data.append({"page_num": i + 1, "text": text.strip()})
        except Exception as e:
            logger.warning(f"pdfplumber extraction error: {e}")
        return pages_data

    async def _extract_with_gemini_ocr(self, file_path: str) -> list[dict]:
        """Uses Gemini Vision / Multimodal capability to extract text from scanned or custom-font PDFs."""
        try:
            from google.genai import types
            from app.services.rag.llm_provider import llm_provider
            if not llm_provider.client:
                return []

            with open(file_path, "rb") as f:
                pdf_bytes = f.read()

            part = types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
            prompt = (
                "You are an expert document OCR system. Extract all readable text, tables, schedules, "
                "dates, and important details from this PDF. Maintain structure and accuracy. "
                "Output the clean extracted content in text and markdown tables."
            )
            response = llm_provider.client.models.generate_content(
                model=settings.LLM_MODEL,
                contents=[part, prompt]
            )
            if response and response.text:
                return [{"page_num": 1, "text": response.text.strip()}]
        except Exception as e:
            logger.error(f"Gemini OCR fallback failed: {e}")
        return []

    def _clean_text(self, pages_data: list[dict]) -> list[dict]:
        for page in pages_data:
            text = page["text"]
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = re.sub(r'[ \t]+', ' ', text)
            page["text"] = text.strip()
        return pages_data

    def _chunk_text(self, pages_data: list[dict], document_id: str, version: int) -> list[DocumentChunkDB]:
        chunks = []
        chunk_size = settings.CHUNK_SIZE
        overlap = settings.CHUNK_OVERLAP
        chunk_idx = 0
        
        for page in pages_data:
            text = page["text"]
            page_num = page["page_num"]
            
            start = 0
            while start < len(text):
                end = min(start + chunk_size, len(text))
                if end < len(text):
                    last_space = text.rfind('\n', start, end)
                    if last_space == -1 or last_space < start + chunk_size // 2:
                        last_space = text.rfind(' ', start, end)
                    if last_space != -1 and last_space > start + chunk_size // 2:
                        end = last_space
                        
                chunk_text = text[start:end].strip()
                if chunk_text:
                    chunk = DocumentChunkDB(
                        id=str(uuid.uuid4()),
                        document_id=document_id,
                        chunk_index=chunk_idx,
                        text=chunk_text,
                        page_number=page_num,
                        created_at=utc_now()
                    )
                    chunks.append(chunk)
                    chunk_idx += 1
                    
                start = end - overlap
                if start < 0:
                    start = 0
                if start >= len(text) or end >= len(text):
                    break
                    
        return chunks

document_processor = DocumentProcessor()
