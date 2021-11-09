import os
import aiofiles

from typing import Any, List, Optional
from itertools import chain
from pathlib import Path


from fastapi import APIRouter, Depends, HTTPException
from fastapi import File, UploadFile, Form
from sqlalchemy.orm import Session
import uuid

from datetime import datetime
from app import crud, models, schemas
from app.api import deps

from app.models.doctor_manager import DoctorManager
from app.models.assistant_manager import AssistantManager
from app.models.doctor_patient import DoctorPatient

router = APIRouter()


@router.get("/", response_model=List[schemas.Voice])
def read_voices(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    
) -> Any:
    """
    Retrieve all voices. Only super user can use it
    """
    if crud.user.is_superuser(current_user):
        voices = crud.voice.get_all(db)
    else:
        HTTPException(status_code=400, detail="Not enough permissions")
    return voices

 #to change after having the relationship crud
@router.get("/{voice_id}", response_model=schemas.Voice)
def read_voice_by_id(
    *,
    db: Session = Depends(deps.get_db),
    voice_id : int,
    current_user: models.User = Depends(deps.get_current_active_user),
    
) -> Any:
    """
    Retrieve voices. Only the doctor of the patient, the assistant owner of the voice or his manager can retrieve it
    """
     #to change after having the relationship crud
    voice = crud.voice.get_by_voice_id(db, id=voice_id)
    if voice:
        manager_idx = db.query(DoctorManager).filter(DoctorManager.doctor_id == voice.doctor_id).\
                                        with_entities(DoctorManager.manager_id).all()
        manager_idx = list(chain(*manager_idx))
        assistant_idx = db.query(AssistantManager).filter(AssistantManager.manager_id in manager_idx).\
                                        with_entities(AssistantManager.assistant_id).all()
        assistant_idx = list(chain(*assistant_idx))

        if current_user.id == voice.doctor_id:
            return voice
        elif current_user.id == voice.patient_id:
            return voice
        elif current_user.id in manager_idx:
            return voice
        elif current_user.id in assistant_idx:
            return voice
        else:
            HTTPException(status_code=400, detail="Not enough permissions")
    return voice



@router.get("/doctor/{doctor_id}", response_model=List[schemas.Voice])
def read_doctor_voices(
    *,
    db: Session = Depends(deps.get_db),
    doctor_id: int,
    note_created: Optional[bool]=None,
    current_user: models.User = Depends(deps.get_current_active_user),
    
) -> Any:
    """
    Retrieve voices related to a doctors. 
    Only That dctor and a super user can use it
    """
    if (crud.user.is_superuser(current_user) or current_user.id  == doctor_id):
        voices = crud.voice.get_multi_by_doctor_id(db, doctor_id=doctor_id, note_created=note_created)
    else :
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return voices

@router.get("/manager/{manager_id}", response_model=List[schemas.Voice])
def read_manager_voices(
    *,
    db: Session = Depends(deps.get_db),
    manager_id: int,
    note_created: Optional[bool]=None,
    current_user: models.User = Depends(deps.get_current_active_user),
    
) -> Any:
    """
    Retrieve voices related to that manager.
    Only that manager and super user can use it
    """
    if (crud.user.is_superuser(current_user) or current_user.id  == manager_id):
        voices = crud.voice.get_multi_by_manager(db, manager_id=manager_id, note_created=note_created)
    else :
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return voices


@router.get("/patient/{patient_id}", response_model=List[schemas.Voice])
def read_patient_voices(
    *,
    db: Session = Depends(deps.get_db),
    patient_id: int,
    note_created: Optional[bool]=None,
    current_user: models.User = Depends(deps.get_current_active_user),
    
) -> Any:
    """
    Retrieve patient voices.
    if it's the patient session (or super user), it will retrieve all patient voices
    if it's the doctor session , it will retrieve the patient-doctors related voices
    """
    #to change after having the relationship crud
    doctor_idx = db.query(DoctorPatient).filter(DoctorPatient.patient_id == patient_id).\
                                        with_entities(DoctorPatient.doctor_id).all()
    doctor_idx = list(chain(*doctor_idx))

    if (crud.user.is_superuser(current_user) or current_user.id  == patient_id):
        voices = crud.voice.get_multi_by_patient(db, patient_id=patient_id, note_created=note_created)
    elif current_user.role == 'doctor' and current_user.id in doctor_idx:
        voices = crud.voice.get_multi_by_patient(db, patient_id=patient_id, doctor_id=current_user.id, note_created=note_created)
    else :
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return voices

@router.post("/", response_model=schemas.Voice)
async def create_voice(
    *,
    db: Session = Depends(deps.get_db),
    doctor_id : int = Form(...),
    patient_id : int = Form(...),
    title: Optional[str] = Form(None),
    remarque : Optional[str] = Form(None),
    voice_file: UploadFile=File(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new item.
    Only doctors and super users can create voices
    """
    voice_in = schemas.VoiceCreate(path='', doctor_id=doctor_id, patient_id=patient_id, title=title, remarque=remarque)
    if (current_user.role != 'doctor' or current_user.id != voice_in.doctor_id) and (not current_user.is_superuser):
        raise HTTPException(
            status_code=401,
            detail="You have not the right the right to write a voice.",
        )
    #to change after having the relationship crud
    patient = crud.user.get_by_id(db=db, id=voice_in.patient_id)
    if not patient:
        raise HTTPException(
            status_code=404,
            detail="No patient with the given id is found in the DB",
        )
    if patient.role != 'patient':
        raise HTTPException(
            status_code=405,
            detail="The id of the given patient is not related to a patient",
        )
    
    doctor_idx = db.query(DoctorPatient).filter(DoctorPatient.patient_id == voice_in.patient_id).\
                                        with_entities(DoctorPatient.doctor_id).all()
    doctor_idx = list(chain(*doctor_idx))

    if not voice_in.doctor_id in doctor_idx:
        raise HTTPException(
                status_code=405,
                detail="This patient is not related to doctor, please ask the admin to relate it to the doctor",
            )
    
    filename = str(uuid.uuid4())
    storage_path = list(Path(os.path.abspath(__file__)).parents)[-2]
    voice_save_path = os.path.abspath(os.path.join(storage_path, 'storage',filename+'_'+voice_file.filename))
    print("voice_save_path", voice_save_path)
    voice_in.path = voice_save_path
    async with aiofiles.open(voice_save_path, 'wb') as out_file:
        while True:
            contents = await voice_file.read(1024)
            if not contents:
                break
            await out_file.write(contents)
    
    voice = crud.voice.create_with_doctor(db=db, obj_in=voice_in, date_creation=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
    return voice