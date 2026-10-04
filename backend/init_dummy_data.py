import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone

from app.db.models import Base, UserDB, LiveUpdateDB, ChatDB, ChatMessageDB, NotificationDB
from app.core.security import get_password_hash

DATABASE_URL = "sqlite+aiosqlite:///./edubot.db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def get_utc_now():
    return datetime.now(timezone.utc)

async def init_dummy_data():
    async with engine.begin() as conn:
        # Don't drop all tables if we want to keep structure, but for this demo let's ensure they are created
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as session:
        # Create Admin
        admin = UserDB(
            email="admin@institute.edu",
            name="Admin User",
            hashed_password=get_password_hash("admin123"),
            role="ADMIN",
            is_active=True
        )
        
        # Create User
        user = UserDB(
            email="vinay@student.edu",
            name="Vinay",
            hashed_password=get_password_hash("student123"),
            role="USER",
            roll_number="BCA2026001",
            course="BCA",
            semester="2",
            is_active=True
        )
        
        session.add(admin)
        session.add(user)
        
        # Add Live Updates
        updates = [
            LiveUpdateDB(
                title="Exam Schedule Updated",
                content="The mid-term exam schedule has been updated. Please check the latest PDF.",
                category="Exam",
                priority="HIGH",
                status="PUBLISHED",
                created_by="Admin",
                published_at=get_utc_now() - timedelta(days=2)
            ),
            LiveUpdateDB(
                title="New Scholarship Notice",
                content="Applications for the state scholarship are open.",
                category="Scholarship",
                priority="NORMAL",
                status="PUBLISHED",
                created_by="Admin",
                published_at=get_utc_now() - timedelta(days=1)
            ),
            LiveUpdateDB(
                title="Seminar on AI",
                content="Join us for a seminar on AI next week in the main auditorium.",
                category="Event",
                priority="NORMAL",
                status="PUBLISHED",
                created_by="Admin",
                published_at=get_utc_now() - timedelta(days=3)
            )
        ]
        session.add_all(updates)
        
        # Add Notifications for User
        notifications = [
            NotificationDB(user_id=user.id, type="UPDATE", title="Exam Schedule Updated", message="New exam schedule posted."),
            NotificationDB(user_id=user.id, type="UPDATE", title="New Scholarship Notice", message="Scholarship applications are open."),
            NotificationDB(user_id=user.id, type="SYSTEM", title="Welcome", message="Welcome to the Institution AI Assistant.")
        ]
        session.add_all(notifications)
        
        # Add a mock chat history
        chat = ChatDB(user_id=user.id, title="BCA Syllabus Enquiry", message_count=2)
        session.add(chat)
        
        await session.flush() # flush to get chat.id
        
        msg1 = ChatMessageDB(
            chat_id=chat.id,
            role="user",
            content="BCA 2nd semester ka syllabus batao"
        )
        msg2 = ChatMessageDB(
            chat_id=chat.id,
            role="assistant",
            content="Bilkul! Yahan BCA 2nd Semester ka complete syllabus hai. 😊\n\n**BCA 2nd Semester – Subjects**\n1. Programming with C and C++\n2. Digital Electronics\n3. Computer Organization and Architecture\n4. Discrete Mathematics\n5. Communication Skills\n6. Environmental Studies\n\nAgar aap kisi specific subject ka detailed syllabus, important topics, previous year questions ya notes chahte ho, to mujhe bataye. Main uski complete information provide kar dunga."
        )
        session.add_all([msg1, msg2])
        
        try:
            await session.commit()
            print("Dummy data populated successfully!")
        except Exception as e:
            await session.rollback()
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(init_dummy_data())
