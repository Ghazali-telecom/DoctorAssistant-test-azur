from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from .user import UserBase, UserCreate, UserInDB, UserInDBBase, UserUpdate, User

# Shared properties

class DoctorBase(UserBase):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    role : str = Field('doctor', const=True)

# Properties to receive via API on creation
class DoctorCreate(UserCreate, DoctorBase):
    pass


# Properties to receive via API on update
class DoctorUpdate(UserUpdate, DoctorBase):
    pass


class DoctorInDBBase(UserInDBBase, DoctorBase):
    class Config:
        orm_mode = True


# Additional properties to return via API
class Doctor(User, DoctorBase):
    pass


# Additional properties stored in DB
class DoctorInDB(UserInDB, DoctorBase):
    pass


