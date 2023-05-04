from uuid import UUID
from enum import Enum
from typing import Optional

from pydantic import BaseModel, HttpUrl, EmailStr


class UserType(str, Enum):
    person = "person"
    bot = "bot"

    def __str__(self):
        return self.value


class Owner(BaseModel):
    type: str
    workspace: bool


class Person(BaseModel):
    email: EmailStr | None = None


class Bot(BaseModel):
    owner: Owner | None = None
    workspace_name: str | None = None


class User(BaseModel):
    object: str = "user"
    id: UUID | str
    type: UserType | None = None
    name: str | None = None
    avatar_url: HttpUrl | None = None
    person: Person | None = None
    bot: Bot | None = None

    class Config:
        use_enum_values = True

    def get_value(self):
        if self.name:
            return self.name
        else:
            return self.id
