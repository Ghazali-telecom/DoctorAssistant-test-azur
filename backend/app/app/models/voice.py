from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class Voice(Base):
    id = Column(Integer, primary_key=True, index=True)
    
    path = Column(String, index=True, nullable=False)
    title = Column(String, index=True, nullable=True)
    remarque = Column(String, index=True, nullable=True)
    note_created = Column(Boolean(), default=False)
    
    doctor_id = Column(Integer, ForeignKey("user.id"))
    doctor = relationship("User", foreign_keys=[doctor_id], backref="voices")

    patient_id = Column(Integer, ForeignKey("user.id"))
    patient = relationship("User", foreign_keys=[patient_id])
                    
    date_creation = Column(DateTime(), nullable= False)