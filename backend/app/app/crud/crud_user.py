from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

from app.models.doctor_manager import DoctorManager
from app.schemas.doctor_manager import DoctorManagerCreate, DoctorManagerUpdate

from app.models.doctor_patient import DoctorPatient
from app.schemas.doctor_patient import DoctorPatientCreate, DoctorPatientUpdate

from app.models.assistant_manager import AssistantManager
from app.schemas.assistant_manager import AssistantManagerCreate, AssistantManagerUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    def get_by_id(self, db: Session, *, id: int) -> Optional[User]:
        return db.query(User).filter(User.id == id).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
            role = obj_in.role
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser
    
    def role(self, user: User) -> str:
        return user.role

    def create_doctor_manager(self, db: Session, *, obj_in: DoctorManagerCreate) -> DoctorManager:
        db_obj = DoctorManager(
            doctor_id=obj_in.doctor_id,
            manager_id=obj_in.manager_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove_doctor_manager(self, db: Session, *, obj_in: DoctorManagerUpdate) -> DoctorManager:
        obj = db.query(DoctorManager).filter(doctor_id=obj_in.doctor_id,
            manager_id=obj_in.manager_id).first()
        db.delete(obj)
        db.commit()
        return obj
    
    def create_doctor_patient(self, db: Session, *, obj_in: DoctorPatientCreate) -> DoctorPatient:
        db_obj = DoctorPatient(
            doctor_id=obj_in.doctor_id,
            patient_id=obj_in.patient_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove_doctor_patient(self, db: Session, *, obj_in: DoctorPatientUpdate) -> DoctorPatient:
        obj = db.query(DoctorPatient).filter(doctor_id=obj_in.doctor_id,
            patient_id=obj_in.patient_id).first()
        db.delete(obj)
        db.commit()
        return obj
    
    def create_assistant_manager(self, db: Session, *, obj_in: AssistantManagerCreate) -> AssistantManager:
        db_obj = AssistantManager(
            assistant_id=obj_in.assistant_id,
            manager_id=obj_in.manager_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove_assistant_manager(self, db: Session, *, obj_in: AssistantManagerUpdate) -> AssistantManager:
        obj = db.query(AssistantManager).filter(assistant_id=obj_in.assistant_id,
            manager_id=obj_in.manager_id).first()
        db.delete(obj)
        db.commit()
        return obj
    
user = CRUDUser(User)
