import pytest
import pytest_asyncio
from app.db.sqlite import init_db

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    await init_db()
    yield
