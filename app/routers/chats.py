# from fastapi import APIRouter, Depends
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.dependencies import get_db
# from app.schemas import ChatCreate
# from app.database import add_chat
#
# router = APIRouter()
#
# @router.post("/add_chat")
# async def add_chat(chat: ChatCreate, db: AsyncSession = Depends(get_db)):
#     return await add_chat(db, chat.chat_id, chat.user_id)