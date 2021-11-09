from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.voice import Voice
from app.models.doctor_manager import DoctorManager
from app.models.assistant_manager import AssistantManager
from app.models.doctor_patient import DoctorPatient

from datetime import datetime
from app.schemas.voice import VoiceCreate, VoiceUpdate
from app.schemas.user_doctor import Doctor
from app.schemas.user_patient import Patient


class CRUDVoice(CRUDBase[Voice, VoiceCreate, VoiceUpdate]):
    def create_with_doctor(
        self, db: Session, *, obj_in: VoiceCreate, date_creation: datetime
    ) -> Voice:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, date_creation = date_creation)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_all(
        self, db: Session
    ) -> List[Voice]:
        return (
            db.query(self.model)
            .all()
        )
    
    def get_multi_by_doctor_id(
        self, db: Session, *, doctor_id: int, note_created: Optional[bool]=None
    ) -> List[Voice]:
        if type(note_created) is bool:
            return (db.query(self.model)
            .filter(Voice.doctor_id == doctor_id, Voice.note_created == note_created)
            .all())
        return (
            db.query(self.model)
            .filter(Voice.doctor_id == doctor_id)
            .all()
        )

    def get_by_voice_id(
        self, db: Session, *, id: int
    ) -> Voice:
        return (
            db.query(self.model)
            .filter(Voice.id == id)
            .first()
        )
    
    def get_multi_by_manager(
        self, db: Session, *, manager_id: int, note_created: Optional[bool]=None
    ) -> List[Voice]:
        if type(note_created) is bool:
            return (
            db.query(self.model)
            .join(DoctorManager, DoctorManager.doctor_id == Voice.doctor_id)
            .filter(DoctorManager.manager_id == manager_id, Voice.note_created==note_created)
            .all())
        return (
            db.query(self.model)
            .join(DoctorManager, DoctorManager.doctor_id == Voice.doctor_id)
            .filter(DoctorManager.manager_id == manager_id)
            .all()
        )
    
    def get_multi_by_assistant(
        self, db: Session, *, assistant_id: int, note_created: Optional[bool]=None
    ) -> List[Voice]:
        if type(note_created) is bool:
            return (
            db.query(self.model)
            .join(DoctorManager, DoctorManager.doctor_id == Voice.doctor_id)
            .join(AssistantManager, AssistantManager.manager_id == AssistantManager.manager_id)
            .filter(AssistantManager.assistant_id == assistant_id, Voice.note_created==note_created)
            .all())
        return (
            db.query(self.model)
            .join(DoctorManager, DoctorManager.doctor_id == Voice.doctor_id)
            .join(AssistantManager, AssistantManager.manager_id == AssistantManager.manager_id)
            .filter(AssistantManager.assistant_id == assistant_id)
            .all()
        )
    
    def get_multi_by_patient(
        self, db: Session, *, patient_id: int, doctor_id: Optional[int]=None ,note_created: Optional[bool]=None
    ) -> List[Voice]:
        if type(note_created) is bool and type(doctor_id) is int:
            return (
            db.query(self.model).filter(Voice.patient_id==patient_id, Voice.doctor_id==doctor_id, Voice.note_created==note_created).all())
        elif type(note_created) is bool:
            return (
            db.query(self.model).filter(Voice.patient_id==patient_id, Voice.note_created==note_created).all())
        else:
            return (db.query(self.model).filter(Voice.patient_id==patient_id).all())
    

voice = CRUDVoice(Voice)
