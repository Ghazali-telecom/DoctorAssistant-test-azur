from typing import Optional

from pydantic import BaseModel, EmailStr, root_validator


# Shared properties
class DoctorManagerBase(BaseModel):
    doctor_id : int
    manager_id : int


# Properties to receive via API on creation
class DoctorManagerCreate(DoctorManagerBase):
    pass


# Properties to receive via API on update
class DoctorManagerUpdate(DoctorManagerBase):
    doctor_id : Optional[int]=None
    manager_id : Optional[int]=None


class DoctorManagerInDBBase(DoctorManagerBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class DoctorManager(DoctorManagerInDBBase):
    pass


# Additional properties stored in DB
class DoctorManagerInDB(DoctorManagerInDBBase):
    pass
