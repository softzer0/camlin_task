from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.utils import generate_objectid, get_current_time


class User(BaseModel):
    id: str = Field(default_factory=generate_objectid)
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=get_current_time)
    updated_at: datetime = Field(default_factory=get_current_time)
