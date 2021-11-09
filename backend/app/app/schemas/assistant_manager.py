from typing import Optional

from pydantic import BaseModel, EmailStr


# Shared properties
class AssistantManagerBase(BaseModel):
    assistant_id : int
    manager_id : int


# Properties to receive via API on creation
class AssistantManagerCreate(AssistantManagerBase):
    pass


# Properties to receive via API on update
class AssistantManagerUpdate(AssistantManagerBase):
    assistant_id : Optional[int]=None
    manager_id : Optional[int]=None


class AssistantManagerInDBBase(AssistantManagerBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class AssistantManager(AssistantManagerInDBBase):
    pass


# Additional properties stored in DB
class AssistantManagerInDB(AssistantManagerInDBBase):
    pass
