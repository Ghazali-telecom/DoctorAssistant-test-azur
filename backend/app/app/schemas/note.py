from typing import Optional, Union

from pydantic import BaseModel
from datetime import datetime

from .user_assistant import Assistant
from .voice import Voice


# Shared properties
class NoteBase(BaseModel):
    content_txt : Optional[str] = None
    


# Properties to receive on item creation
class NoteCreate(NoteBase):
    voice_id : int
    assistant_id : int
    
    

# Properties to receive on item update
class NoteUpdate(NoteBase):
    validated : Optional[bool] = None
    date_modification : datetime
    modifier_id : int
    


# Properties shared by models stored in DB
class NoteInDBBase(NoteBase):
    id: int
    voice_id : int
    validated : bool
    assistant_id : int
    date_creation : datetime
    modifier_id : int
    date_modification : datetime

    class Config:
        orm_mode = True


# Properties to return to client
class Note(NoteInDBBase):
    pass


# Properties properties stored in DB
class NoteInDB(NoteInDBBase):
    pass
