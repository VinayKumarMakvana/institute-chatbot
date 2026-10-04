import pytest
import os
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.document import DocumentStatus

@pytest.fixture
def mock_admin_token():
    from app.core.security import create_access_token
    from app.core.config import settings
    return create_access_token({"sub": settings.ADMIN_EMAIL, "role": "ADMIN"})

@pytest.fixture
def mock_user_token():
    from app.core.security import create_access_token
    return create_access_token({"sub": "1", "role": "USER"})

@pytest.mark.asyncio
async def test_upload_document_unauthorized():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/documents")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_upload_document_user_forbidden(mock_user_token):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/documents",
            headers={"Authorization": f"Bearer {mock_user_token}"}
        )
    assert response.status_code == 403

# We skip full e2e DB tests here without mongomock, but we can verify route protection works.
