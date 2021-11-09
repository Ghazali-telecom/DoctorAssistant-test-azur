from typing import List, Optional, Any, Dict, Optional, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.note import Note
from app.models.voice import Voice
from app.models.doctor_manager import DoctorManager
from app.models.assistant_manager import AssistantManager
from app.models.doctor_patient import DoctorPatient

from datetime import datetime
from app.schemas.note import NoteCreate, NoteUpdate
from app.schemas.user_doctor import Doctor
from app.schemas.user_patient import Patient


class CRUDNote(CRUDBase[Note, NoteCreate, NoteUpdate]):
    def create_with_assistant(
        self, db: Session, *, obj_in: NoteCreate, date_creation: datetime
    ) -> Note:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, date_creation = date_creation)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_note(
        self, db: Session, *, db_obj: Note, obj_in: Union[NoteUpdate, Dict[str, Any]]
    ) -> Note:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def get_all(
        self, db: Session
    ) -> List[Note]:
        return (
            db.query(self.model)
            .all()
        )
    
    def get_multi_by_doctor_id(
        self, db: Session, *, doctor_id: int, validated: Optional[bool]=None
    ) -> List[Note]:
        if type(validated) is bool:
            return (db.query(self.model)
            .join(Voice, Note.voice_id == Voice.id)
            .filter(Voice.doctor_id == doctor_id, Note.validated == validated)
            .all())
        return (db.query(self.model)
            .join(Voice, Note.voice_id == Voice.id)
            .filter(Voice.doctor_id == doctor_id)
            .all())

    def get_by_note_id(
        self, db: Session, *, id: int
    ) -> Note:
        return (
            db.query(self.model)
            .filter(Note.id == id)
            .first()
        )
    
    def get_multi_by_manager(
        self, db: Session, *, manager_id: int, validated: Optional[bool]=None
    ) -> List[Note]:
        if type(validated) is bool:
            return (db.query(self.model)
            .join(AssistantManager, AssistantManager.assistant_id == Note.assistant_id)
            .filter(AssistantManager.manager_id == manager_id, Note.validated==validated)
            .all())
        return (db.query(self.model)
            .join(AssistantManager, AssistantManager.assistant_id == Note.assistant_id)
            .filter(AssistantManager.manager_id == manager_id)
            .all())
    
    def get_multi_by_assistant(
        self, db: Session, *, assistant_id: int, validated: Optional[bool]=None
    ) -> List[Note]:
        if type(validated) is bool:
            return (
            db.query(self.model)
            .filter(Note.assistant_id==assistant_id, Note.validated==validated)
            .all())
        return (
            db.query(self.model)
            .filter(Note.assistant_id==assistant_id)
            .all())
    
    def get_multi_by_patient(
        self, db: Session, *, patient_id: int, validated: Optional[bool]=None
    ) -> List[Note]:
        if type(validated) is bool:
            return (
            db.query(self.model)
            .join(Voice, Voice.id == Note.voice_id)
            .filter(Voice.patient_id==patient_id, Note.validated==validated)
            .all())
        return (
            db.query(self.model)
            .join(Voice, Voice.id == Note.voice_id)
            .filter(Voice.patient_id==patient_id)
            .all())


note = CRUDNote(Note)
