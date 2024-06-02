from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class EventCreate(BaseModel):
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    user_id: int

class Event(BaseModel):
    id: int
    title: str
    description: str
    start_time: datetime
    end_time: datetime

    class Config:
        orm_mode = True