import os
import shutil
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone

from app.models.document import DocumentResponse, DocumentStatus, DocumentUpdate
from app.models.response import StandardResponse
from app.models.user import UserResponse
from app.api.v1 import deps
from app.db.sqlite import get_db
from app.db.models import DocumentDB, DocumentChunkDB
from app.core.config import settings
from app.services.document_processor import document_processor
from app.services.vectorstore import vector_store

router = APIRouter()

def utc_now():
    return datetime.utcnow()

@router.post("", response_model=StandardResponse[DocumentResponse])
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    document_type: str = Form("general"),
    category: str = Form(None),
    semester: str = Form(None),
    current_admin: UserResponse = Depends(deps.require_admin),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid MIME type")
        
    os.makedirs(settings.DOCUMENT_STORAGE_PATH, exist_ok=True)
    
    doc_id = str(uuid.uuid4())
    safe_filename = f"{doc_id}.pdf"
    file_path = os.path.join(settings.DOCUMENT_STORAGE_PATH, safe_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file_size = os.path.getsize(file_path)
    if file_size > settings.MAX_PDF_SIZE_MB * 1024 * 1024:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"File exceeds maximum size of {settings.MAX_PDF_SIZE_MB}MB")

    now = utc_now()
    doc = DocumentDB(
        id=doc_id,
        title=title,
        original_filename=file.filename,
        stored_filename=safe_filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type,
        document_type=document_type,
        category=category,
        semester=semester,
        version=1,
        status=DocumentStatus.UPLOADED,
        processing_stage="File uploaded",
        uploaded_by=current_admin.email,
        created_at=now,
        updated_at=now
    )
    
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    
    doc_resp = _map_doc_response(doc)
    
    # Trigger processing
    background_tasks.add_task(document_processor.process_document, doc_id)
    
    return StandardResponse(success=True, message="Document uploaded and processing started.", data=doc_resp)

@router.get("", response_model=StandardResponse[List[DocumentResponse]])
async def list_documents(current_admin: UserResponse = Depends(deps.require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DocumentDB).order_by(DocumentDB.created_at.desc()).limit(1000))
    docs = result.scalars().all()
    data = [_map_doc_response(d) for d in docs]
    return StandardResponse(success=True, message="Documents retrieved.", data=data)

@router.get("/library", response_model=StandardResponse[List[DocumentResponse]])
async def get_document_library(current_user: UserResponse = Depends(deps.get_current_user), db: AsyncSession = Depends(get_db)):
    # Only return READY documents for regular users
    result = await db.execute(select(DocumentDB).where(DocumentDB.status == "READY").order_by(DocumentDB.created_at.desc()).limit(1000))
    docs = result.scalars().all()
    data = [_map_doc_response(d) for d in docs]
    return StandardResponse(success=True, message="Document library retrieved.", data=data)

@router.get("/{document_id}", response_model=StandardResponse[DocumentResponse])
async def get_document(document_id: str, current_admin: UserResponse = Depends(deps.require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DocumentDB).where(DocumentDB.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return StandardResponse(success=True, message="Document retrieved.", data=_map_doc_response(doc))

@router.delete("/{document_id}", response_model=StandardResponse[None])
async def delete_document(document_id: str, current_admin: UserResponse = Depends(deps.require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DocumentDB).where(DocumentDB.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    chunk_res = await db.execute(select(DocumentChunkDB).where(DocumentChunkDB.document_id == document_id))
    chunks = chunk_res.scalars().all()
    chunk_ids = [c.id for c in chunks]
    
    if chunk_ids:
        vector_store.delete_by_chunk_ids(chunk_ids)
        for c in chunks:
            await db.delete(c)
            
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)
        
    await db.delete(doc)
    await db.commit()
    
    return StandardResponse(success=True, message="Document and associated data deleted.", data=None)

@router.post("/{document_id}/reprocess", response_model=StandardResponse[DocumentResponse])
async def reprocess_document(
    document_id: str, 
    background_tasks: BackgroundTasks,
    current_admin: UserResponse = Depends(deps.require_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(DocumentDB).where(DocumentDB.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    chunk_res = await db.execute(select(DocumentChunkDB).where(DocumentChunkDB.document_id == document_id))
    chunks = chunk_res.scalars().all()
    chunk_ids = [c.id for c in chunks]
    
    if chunk_ids:
        vector_store.delete_by_chunk_ids(chunk_ids)
        for c in chunks:
            await db.delete(c)
            
    doc.status = DocumentStatus.UPLOADED
    doc.processing_stage = "Reprocessing initiated"
    doc.processing_error = None
    doc.total_pages = 0
    doc.total_chunks = 0
    doc.updated_at = utc_now()
    await db.commit()
    
    background_tasks.add_task(document_processor.process_document, document_id)
    await db.refresh(doc)
    return StandardResponse(success=True, message="Reprocessing started.", data=_map_doc_response(doc))

@router.put("/{document_id}", response_model=StandardResponse[DocumentResponse])
async def update_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(None),
    title: str = Form(None),
    document_type: str = Form(None),
    category: str = Form(None),
    semester: str = Form(None),
    current_admin: UserResponse = Depends(deps.require_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(DocumentDB).where(DocumentDB.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    doc.updated_at = utc_now()
    if title is not None: doc.title = title
    if document_type is not None: doc.document_type = document_type
    if category is not None: doc.category = category
    if semester is not None: doc.semester = semester
    
    requires_reprocessing = False
    
    if file:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
            
        new_version = doc.version + 1
        safe_filename = f"{document_id}_v{new_version}.pdf"
        file_path = os.path.join(settings.DOCUMENT_STORAGE_PATH, safe_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        file_size = os.path.getsize(file_path)
        if file_size > settings.MAX_PDF_SIZE_MB * 1024 * 1024:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="File too large")
            
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
            
        doc.original_filename = file.filename
        doc.stored_filename = safe_filename
        doc.file_path = file_path
        doc.file_size = file_size
        doc.mime_type = file.content_type
        doc.version = new_version
        doc.status = DocumentStatus.UPLOADED
        doc.processing_stage = "File replaced, waiting to process"
        doc.processing_error = None
        doc.total_pages = 0
        doc.total_chunks = 0
        requires_reprocessing = True
        
    await db.commit()
    
    if requires_reprocessing:
        chunk_res = await db.execute(select(DocumentChunkDB).where(DocumentChunkDB.document_id == document_id))
        chunks = chunk_res.scalars().all()
        chunk_ids = [c.id for c in chunks]
        if chunk_ids:
            vector_store.delete_by_chunk_ids(chunk_ids)
            for c in chunks:
                await db.delete(c)
            await db.commit()
            
        background_tasks.add_task(document_processor.process_document, document_id)
        
    await db.refresh(doc)
    msg = "Document replaced and processing started." if requires_reprocessing else "Document updated."
    return StandardResponse(success=True, message=msg, data=_map_doc_response(doc))
    
def _map_doc_response(doc: DocumentDB) -> DocumentResponse:
    return DocumentResponse(
        id=doc.id,
        title=doc.title,
        original_filename=doc.original_filename,
        stored_filename=doc.stored_filename,
        file_path=doc.file_path,
        file_size=doc.file_size,
        mime_type=doc.mime_type,
        document_type=doc.document_type,
        category=doc.category,
        semester=doc.semester,
        status=doc.status,
        processing_stage=doc.processing_stage,
        processing_error=doc.processing_error,
        version=doc.version,
        total_pages=doc.total_pages,
        total_chunks=doc.total_chunks,
        uploaded_by=doc.uploaded_by,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        processed_at=doc.processed_at
    )
