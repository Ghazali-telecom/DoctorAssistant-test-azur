from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from .user import UserBase, UserCreate, UserInDB, UserInDBBase, UserUpdate, User

# Shared properties

class ManagerBase(UserBase):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    role : str = Field('manager', const=True)

# Properties to receive via API on creation
class ManagerCreate(UserCreate, ManagerBase):
    pass


# Properties to receive via API on update
class ManagerUpdate(UserUpdate, ManagerBase):
    pass


class ManagerInDBBase(UserInDBBase, ManagerBase):
    class Config:
        orm_mode = True


# Additional properties to return via API
class Manager(User, ManagerBase):
    pass


# Additional properties stored in DB
class ManagerInDB(UserInDB, ManagerBase):
    pass


