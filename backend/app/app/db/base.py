# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.item import Item  # noqa
from app.models.voice import Voice  # noqa
from app.models.note import Note  # noqa
from app.models.assistant_manager import AssistantManager
from app.models.doctor_manager import DoctorManager
from app.models.doctor_patient import DoctorPatient

