from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship, backref

from app.db.base_class import Base


if TYPE_CHECKING:
    from .user import User  # noqa: F401
    from .voice import Voice  # noqa: F401


class Note(Base):
    id = Column(Integer, primary_key=True, index=True)

    content_txt = Column(String, index=True)
    validated = Column(Boolean(), default=False)
    
    voice_id = Column(Integer, ForeignKey("voice.id"))
    voice = relationship("Voice", foreign_keys=[voice_id], backref=backref("voice", uselist=False))

    assistant_id = Column(Integer, ForeignKey("user.id"))
    assistant = relationship("User", foreign_keys=[assistant_id], backref="notes")

    modifier_id = Column(Integer, ForeignKey("user.id"), nullable=True)
                    
    date_creation = Column(DateTime, nullable= False)
    date_modification = Column(DateTime, nullable= True)