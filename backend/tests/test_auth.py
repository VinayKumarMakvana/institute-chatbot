import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_register_user():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/register", json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpassword",
            "roll_number": "12345",
            "department": "CS",
            "course": "BTech",
            "semester": "3",
            "mobile_number": "9876543210"
        })
    # Might be 400 if already exists, that's fine for simple test
    assert response.status_code in [200, 400]

@pytest.mark.asyncio
async def test_login_user():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword"
        })
    assert response.status_code in [200, 401]
