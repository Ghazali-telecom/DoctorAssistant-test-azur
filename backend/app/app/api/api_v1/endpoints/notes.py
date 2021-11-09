from typing import Any, List, Optional
from itertools import chain

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from datetime import datetime
from app import crud, models, schemas
from app.api import deps

from app.models.doctor_manager import DoctorManager
from app.models.assistant_manager import AssistantManager
from app.models.doctor_patient import DoctorPatient
from app.models.voice import Voice

router = APIRouter()

@router.get("/", response_model=List[schemas.Note])
def read_notes(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    
) -> Any:
    """
    Retrieve notes.
    Only super users can retrieve all notes
    """
    if crud.user.is_superuser(current_user):
        notes = crud.note.get_all(db)
    else:
        raise HTTPException(status_code=401, detail="Not enough permissions")
    return notes

 #to change after having the relationship crud
@router.get("/{note_id}", response_model=schemas.Note)
def read_note_by_id(
    *,
    db: Session = Depends(deps.get_db),
    note_id : int,
    current_user: models.User = Depends(deps.get_current_active_user),
    
) -> Any:
    """
    Retrieve note by id.
    Only super user, th assistant of this note, is manaer or the doctor can retrieve it
    """
     #to change after having the relationship crud
    note = crud.note.get_by_note_id(db, id=note_id)
    if note:
        manager_idx = db.query(AssistantManager).filter(AssistantManager.assistant_id == note.assistant_id).\
                                    with_entities(AssistantManager.manager_id).all()
        manager_idx = list(chain(*manager_idx))
        doctor_idx = db.query(Voice).filter(Voice.id == note.assistant_id).\
                                    with_entities(Voice.doctor_id).all()
        doctor_idx = list(chain(*doctor_idx))

        if current_user.id == note.assistant_id or current_user.id == note.modifier_id or current_user.is_superuser:
            return note
        elif current_user.id in manager_idx:
            return note
        elif current_user.id in doctor_idx:
            return note
        else:
            raise HTTPException(status_code=400, detail="Not enough permissions")
    else:
        raise HTTPException(status_code=404, detail="No note found with given note id")
    return note

@router.post("/", response_model=schemas.Note)
def create_note(
    *,
    db: Session = Depends(deps.get_db),
    note_in: schemas.NoteCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new note.
    Only assistants and super user can create notes
    """
    if current_user.role != 'assistant' and not current_user.is_superuser:
        raise HTTPException(
            status_code=401,
            detail="You have not the right to create note.",
        )
    
    voice = crud.voice.get_by_voice_id(db, id=note_in.voice_id)
    if not voice:
        raise HTTPException(
            status_code=404,
            detail="The given voice id is not found",
        )
    
    if voice.note_created:
        raise HTTPException(
            status_code=505,
            detail="Note already created for this voice",
        )
    
    note = crud.note.create_with_assistant(db=db, obj_in=note_in, date_creation=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    crud.voice.update(db=db, db_obj=voice, obj_in=dict({'note_created':True}))
    return note

@router.put("/{note_id}", response_model=schemas.Note)
def update_note(
    *,
    db: Session = Depends(deps.get_db),
    note_in: schemas.NoteUpdate,
    note_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Modify note
    Assistant doctor or manager related to this note
    """
    
    note = crud.note.get_by_note_id(db, id=note_id)
    
    if note:
        manager_idx = db.query(AssistantManager).filter(AssistantManager.assistant_id == note.assistant_id).\
                                    with_entities(AssistantManager.manager_id).all()
        manager_idx = list(chain(*manager_idx))
        doctor_idx = db.query(Voice).filter(Voice.id == note.assistant_id).\
                                    with_entities(Voice.doctor_id).all()
        doctor_idx = list(chain(*doctor_idx))

        if current_user.id in manager_idx or current_user.is_superuser:
            note_in.modifier_id = current_user.id
            note_in.date_modification = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            note = crud.note.update_note(db=db, db_obj = note, obj_in=note_in)
        elif current_user.id == note.assistant_id or current_user.id == note.modifier_id \
             or current_user.id in doctor_idx:
            note_in.modifier_id = current_user.id
            note_in.validated = False
            note_in.date_modification = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            note = crud.note.update_note(db=db, db_obj = note, obj_in=note_in)
            return note
        else:
            raise HTTPException(status_code=400, detail="Not enough permissions")
    else:
        raise HTTPException(
            status_code=404,
            detail="No note fund with the given id.",
        )
    
    return note

#############################################

@router.get("/doctor/{doctor_id}", response_model=List[schemas.Note])
def read_doctor_notes(
    *,
    db: Session = Depends(deps.get_db),
    doctor_id: int,
    validated: Optional[bool]=None,
    current_user: models.User = Depends(deps.get_current_active_user),
    
) -> Any:
    """
    Retrieve doctor notes.
    Only a doctor or super user can retrieve them
    """
    if current_user.role != "doctor" and not current_user.is_superuser:
        HTTPException(status_code=400, detail="Not enough permissions")

    if crud.user.is_superuser(current_user) or current_user.id  == doctor_id:
        notes = crud.note.get_multi_by_doctor_id(db, doctor_id=doctor_id, validated=validated)
    else :
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return notes

@router.get("/manager/{manager_id}", response_model=List[schemas.Note])
def read_manager_notes(
    *,
    db: Session = Depends(deps.get_db),
    manager_id: int,
    validated: Optional[bool]=None,
    current_user: models.User = Depends(deps.get_current_active_user),
    
) -> Any:
    """
    Retrieve voices.
    manager or super user
    """
    if current_user.role != "manager" and not current_user.is_superuser:
        HTTPException(status_code=400, detail="Not enough permissions")
    if crud.user.is_superuser(current_user) or current_user.id  == manager_id:
        notes = crud.note.get_multi_by_manager(db, manager_id=manager_id, validated=validated)
    else :
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return notes

@router.get("/patient/{patient_id}", response_model=List[schemas.Note])
def read_patient_voices(
    *,
    db: Session = Depends(deps.get_db),
    patient_id: int,
    validated: Optional[bool]=None,
    current_user: models.User = Depends(deps.get_current_active_user),
    
) -> Any:
    """
    Retrieve voices.
    Only the patient or his doctor can retrieve the patient voices (also super user)
    """
    doctor_idx = db.query(DoctorPatient).filter(DoctorPatient.patient_id == patient_id).with_entities(DoctorPatient.doctor_id).all()
    doctor_idx = list(chain(*doctor_idx))

    if crud.user.is_superuser(current_user) or current_user.id  == patient_id or current_user.id in doctor_idx:
        notes = crud.note.get_multi_by_patient(db, patient_id=patient_id, validated=validated)
    else :
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return notes


