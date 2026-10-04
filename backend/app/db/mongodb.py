from motor.motor_asyncio import AsyncIOMotorClient
import pymongo
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db_client = MongoDB()

async def connect_to_mongo():
    logger.info("Connecting to MongoDB...")
    db_client.client = AsyncIOMotorClient(settings.MONGODB_URI)
    db_client.db = db_client.client[settings.MONGODB_DATABASE]
    # Check connection
    try:
        await db_client.client.admin.command('ping')
        logger.info(f"Connected to MongoDB. Database: {settings.MONGODB_DATABASE}")
        await create_indexes()
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        raise e

async def close_mongo_connection():
    logger.info("Closing MongoDB connection...")
    if db_client.client:
        db_client.client.close()
        logger.info("MongoDB connection closed.")

def get_database():
    return db_client.db

async def create_indexes():
    if db_client.db is not None:
        logger.info("Ensuring database indexes...")
        await db_client.db.users.create_index([("email", pymongo.ASCENDING)], unique=True)
        await db_client.db.documents.create_index([("status", pymongo.ASCENDING)])
        await db_client.db.document_chunks.create_index([("document_id", pymongo.ASCENDING)])
        await db_client.db.document_chunks.create_index([("vector_id", pymongo.ASCENDING)])
        await db_client.db.chats.create_index([("user_id", pymongo.ASCENDING), ("is_deleted", pymongo.ASCENDING)])
        await db_client.db.chats.create_index([("updated_at", pymongo.DESCENDING)])
        await db_client.db.chat_messages.create_index([("chat_id", pymongo.ASCENDING), ("created_at", pymongo.ASCENDING)])
        await db_client.db.saved_answers.create_index([("user_id", pymongo.ASCENDING)])
        await db_client.db.saved_answers.create_index([("message_id", pymongo.ASCENDING)])
        
        await db_client.db.live_updates.create_index([("status", pymongo.ASCENDING)])
        await db_client.db.live_updates.create_index([("published_at", pymongo.DESCENDING)])
        await db_client.db.live_updates.create_index([("created_at", pymongo.DESCENDING)])
        
        await db_client.db.notifications.create_index([("user_id", pymongo.ASCENDING), ("is_read", pymongo.ASCENDING)])
        await db_client.db.notifications.create_index([("user_id", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)])
        await db_client.db.notifications.create_index([("user_id", pymongo.ASCENDING), ("update_id", pymongo.ASCENDING)])

