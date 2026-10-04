import os
os.environ["JWT_SECRET"] = "test_secret_for_pytest"
os.environ["ADMIN_PASSWORD_HASH"] = "$2b$12$testmockhashforadmin"
os.environ["AI_PROVIDER"] = "mock"

import pytest
import pytest_asyncio
from app.db.sqlite import init_db, AsyncSessionLocal
from sqlalchemy import text

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    await init_db()
    async with AsyncSessionLocal() as session:
        await session.execute(text("DELETE FROM saved_answers"))
        await session.execute(text("DELETE FROM chat_messages"))
        await session.execute(text("DELETE FROM chats"))
        await session.execute(text("DELETE FROM users"))
        await session.execute(text("INSERT INTO users (id, email, name, hashed_password, role, is_active, created_at) VALUES ('1', 'mock@example.com', 'Mock User', 'hash', 'USER', 1, '2023-10-04T12:00:00')"))
        await session.commit()
    yield
