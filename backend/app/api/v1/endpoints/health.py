from fastapi import APIRouter
from app.models.response import StandardResponse
from app.db.mongodb import db_client

router = APIRouter()

@router.get("/", response_model=StandardResponse)
async def health_check():
    # Check db status
    db_status = "disconnected"
    try:
        if db_client.client:
            await db_client.client.admin.command('ping')
            db_status = "connected"
    except Exception:
        db_status = "error"
        
    return StandardResponse(
        success=True,
        message="Backend is running.",
        data={"database": db_status}
    )
