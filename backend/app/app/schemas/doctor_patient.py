from typing import Optional

from pydantic import BaseModel, EmailStr


# Shared properties
class DoctorPatientBase(BaseModel):
    doctor_id : int
    patient_id : int


# Properties to receive via API on creation
class DoctorPatientCreate(DoctorPatientBase):
    pass


# Properties to receive via API on update
class DoctorPatientUpdate(DoctorPatientBase):
    doctor_id : Optional[int]=None
    patient_id : Optional[int]=None


class DoctorPatientInDBBase(DoctorPatientBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class DoctorPatient(DoctorPatientInDBBase):
    pass


# Additional properties stored in DB
class DoctorPatientInDB(DoctorPatientInDBBase):
    pass
