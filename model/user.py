import datetime
from beanie import Document, Indexed
from pydantic import Field
from typing import Annotated


class User(Document):
    username: Annotated[str, Indexed(unique=True, name="username_idx")] = Field(...)
    first_name: str
    last_name: str
    is_active: bool = True

    role: bool = False
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    is_superuper: bool = False

    class Settings:
        name = "users"
        use_state_management = True

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True,
                "role": "leader",
                "is_superuser": False,
            }
        }
