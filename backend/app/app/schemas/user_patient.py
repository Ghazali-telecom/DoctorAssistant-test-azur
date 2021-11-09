from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from .user import UserBase, UserCreate, UserInDB, UserInDBBase, UserUpdate, User

# Shared properties

class PatientBase(UserBase):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    role : str = Field('patient', const=True)

# Properties to receive via API on creation
class PatientCreate(UserCreate, PatientBase):
    pass


# Properties to receive via API on update
class PatientUpdate(UserUpdate, PatientBase):
    pass


class PatientInDBBase(UserInDBBase, PatientBase):
    class Config:
        orm_mode = True


# Additional properties to return via API
class Patient(User, PatientBase):
    pass


# Additional properties stored in DB
class PatientInDB(UserInDB, PatientBase):
    pass


