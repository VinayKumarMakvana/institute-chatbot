import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.main import app
import jwt
from datetime import datetime, timedelta, timezone

# We need a mock user token
def create_mock_token(user_id="1"):
    from app.core.config import settings
    payload = {
        "sub": user_id,
        "role": "USER",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=60)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

@pytest_asyncio.fixture(autouse=True)
async def setup_db_test():
    yield


@pytest.mark.asyncio
async def test_chat_creation_and_save():
    token = create_mock_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create chat by sending a message
        res = await ac.post("/api/v1/chat", json={"message": "Test question"}, headers=headers)
        assert res.status_code == 200
        data = res.json()["data"]
        chat_id = data["chat_id"]
        message_id = data["message_id"]
        
        # Save answer
        res_save = await ac.post("/api/v1/saved-answers", json={"message_id": message_id}, headers=headers)
        assert res_save.status_code == 200
        saved_id = res_save.json()["data"]["id"]
        
        # Get saved answers
        res_list = await ac.get("/api/v1/saved-answers", headers=headers)
        assert res_list.status_code == 200
        assert len(res_list.json()["data"]) == 1
        
        # Unsave
        res_unsave = await ac.delete(f"/api/v1/saved-answers/{saved_id}", headers=headers)
        assert res_unsave.status_code == 200
        
        # Get saved answers again
        res_list2 = await ac.get("/api/v1/saved-answers", headers=headers)
        assert len(res_list2.json()["data"]) == 0
        
        # Get chat details
        res_chat = await ac.get(f"/api/v1/chats/{chat_id}", headers=headers)
        assert res_chat.status_code == 200
        assert len(res_chat.json()["data"]["messages"]) == 2
        
        # Delete chat
        res_del = await ac.delete(f"/api/v1/chats/{chat_id}", headers=headers)
        assert res_del.status_code == 200
        
        # Get chat list
        res_chats = await ac.get("/api/v1/chats", headers=headers)
        assert len(res_chats.json()["data"]) == 0
