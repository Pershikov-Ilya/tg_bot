from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.schemas import UserCreate
from app.database import get_user, create_user

router = APIRouter()

@router.post("/register", response_model=UserCreate)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await get_user(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await create_user(db, user)