from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, backref

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class AssistantManager(Base):
    id = Column(Integer, primary_key=True, index=True)
    assistant_id = Column(Integer, ForeignKey("user.id"))
    manager_id = Column(Integer, ForeignKey("user.id"))