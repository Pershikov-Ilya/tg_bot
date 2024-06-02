from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User, Event
from app.schemas import UserCreate, EventCreate

async def get_user(db: AsyncSession, username: str):
    return await db.execute(select(User).filter(User.username == username)).scalar_one_or_none()

async def create_user(db: AsyncSession, user: UserCreate):
    db_user = User(username=user.username, hashed_password=user.password)  # Замените на хеширование пароля
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def create_event(db: AsyncSession, event: EventCreate):
    db_event = Event(**event.dict())
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event

async def get_events_for_user(db: AsyncSession, user_id: int):
    return await db.execute(select(Event).filter(Event.user_id == user_id)).scalars().all()
