import asyncio
from app.services.rag.rag_service import rag_service
from app.db.mongodb import connect_to_mongo, close_mongo_connection

async def test():
    await connect_to_mongo()
    try:
        response = await rag_service.ask("What is the exam date?")
        print("Response:", response.answer)
        print("Language:", response.language)
        print("Sources:", response.sources)
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(test())
