import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
def mock_user_token():
    from app.core.security import create_access_token
    return create_access_token({"sub": "1", "role": "USER"})

@pytest.mark.asyncio
async def test_chat_endpoint_unauthorized():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/chat", json={"message": "hello"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_chat_endpoint_empty_query(mock_user_token):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/chat", 
            json={"message": ""},
            headers={"Authorization": f"Bearer {mock_user_token}"}
        )
    assert response.status_code == 400

# Full testing of RAG logic would require mock data in MongoDB.
# The endpoint validation is verified above.
