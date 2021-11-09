from typing import Optional

from pydantic import BaseModel
from datetime import datetime

from .user_doctor import Doctor
from .user_patient import Patient

# Shared properties
class VoiceBase(BaseModel):
    path : str
    


# Properties to receive on item creation
class VoiceCreate(VoiceBase):
    doctor_id : int
    patient_id : int
    title: Optional[str] = None
    remarque : Optional[str] = None


# Properties to receive on item update
class VoiceUpdate(VoiceBase):
    pass


# Properties shared by models stored in DB
class VoiceInDBBase(VoiceBase):
    id: int
    doctor_id : int
    patient_id : int
    title: Optional[str]=None
    date_creation : datetime
    note_created : bool = False

    class Config:
        orm_mode = True


# Properties to return to client
class Voice(VoiceInDBBase):
    pass


# Properties properties stored in DB
class VoiceInDB(VoiceInDBBase):
    pass
