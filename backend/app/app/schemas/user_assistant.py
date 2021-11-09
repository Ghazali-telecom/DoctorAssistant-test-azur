from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from .user import UserBase, UserCreate, UserInDB, UserInDBBase, UserUpdate, User

# Shared properties

class AssistantBase(UserBase):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    role : str = Field('assistant', const=True)

# Properties to receive via API on creation
class AssistantCreate(UserCreate, AssistantBase):
    pass


# Properties to receive via API on update
class AssistantUpdate(UserUpdate, AssistantBase):
    pass


class AssistantInDBBase(UserInDBBase, AssistantBase):
    class Config:
        orm_mode = True


# Additional properties to return via API
class Assistant(User, AssistantBase):
    pass


# Additional properties stored in DB
class AssistantInDB(UserInDB, AssistantBase):
    pass


