from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.utils import send_new_account_email

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    Only super user can retrieve a list of all users
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new user.
    Only super user can create users and doctors who can create patient
    """
    if not current_user.is_superuser or (current_user.role != 'doctor' and user_in.role != 'patient'):
        raise HTTPException(
            status_code=401,
            detail="Only super user can create users or doctors who can create patient",
        )
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = crud.user.create(db, obj_in=user_in)
    if settings.EMAILS_ENABLED and user_in.email:
        send_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
    return user


@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me", response_model=schemas.User)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.post("/open", response_model=schemas.User)
def create_user_open(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(...),
    email: EmailStr = Body(...),
    full_name: str = Body(None),
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )
    user = crud.user.get_by_email(db, email=email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user_in = schemas.UserCreate(password=password, email=email, full_name=full_name)
    user = crud.user.create(db, obj_in=user_in)
    return user


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud.user.get(db, id=user_id)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.get("/doctor_manager/{doctor_id}/{manager_id}", response_model=schemas.DoctorManagerInDB)
def create_doctor_manager(
    doctor_id: int,
    manager_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Create doctor manager relationship
    Only super users can create this relationship
    """
    doctor = crud.user.get(db, id=doctor_id)
    manager = crud.user.get(db, id=manager_id)
    
    if not doctor or doctor.role != 'doctor':
        raise HTTPException(
            status_code=404, detail="No Doctor found with given doctor_id"
        )
    if not manager or manager.role != 'manager':
        raise HTTPException(
            status_code=404, detail="No Manager found with given manager_id"
        )
    obj_in = schemas.DoctorManagerCreate(doctor_id=doctor_id, manager_id=manager_id)
    doctor_manager = crud.user.create_doctor_manager(db=db, obj_in=obj_in)
    return doctor_manager

@router.get("/doctor_patient/{doctor_id}/{patient_id}", response_model=schemas.DoctorPatientInDB)
def create_doctor_patient(
    doctor_id: int,
    patient_id: int,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Create doctor patient relationship.
    Doctors and super users can create this relationship
    """

    doctor = crud.user.get(db, id=doctor_id)
    patient = crud.user.get(db, id=patient_id)
    
    if current_user.role != 'doctor' and not current_user.is_superuser:
        raise HTTPException(
            status_code=401, detail="Only doctoors and super users can create this relationship"
        )
    
    if current_user.role == 'doctor' and current_user.id != doctor_id:
        raise HTTPException(
            status_code=401, detail="You can not create relationships for other doctors"
        )
    
    if not doctor or doctor.role != 'doctor':
        raise HTTPException(
            status_code=404, detail="No Doctor found with given doctor_id"
        )
    if not patient or patient.role != 'patient':
        raise HTTPException(
            status_code=404, detail="No Patient found with given patient_id"
        )
    obj_in = schemas.DoctorPatientCreate(doctor_id=doctor_id, patient_id=patient_id)
    doctor_patient = crud.user.create_doctor_patient(db=db, obj_in=obj_in)
    return doctor_patient


@router.get("/assistant_manager/{assistant_id}/{manager_id}", response_model=schemas.AssistantManagerInDB)
def create_assistant_manager(
    assistant_id: int,
    manager_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Create doctor manager relationship
    Only super users can create this relationship
    """

    assistant = crud.user.get(db, id=assistant_id)
    manager = crud.user.get(db, id=manager_id)
    
    if not assistant or assistant.role != 'assistant':
        raise HTTPException(
            status_code=404, detail="No Doctor found with given doctor_id"
        )
    if not manager or manager.role != 'manager':
        raise HTTPException(
            status_code=404, detail="No Manager found with given manager_id"
        )
    obj_in = schemas.AssistantManagerCreate(assistant_id=assistant_id, manager_id=manager_id)
    assistant_manager = crud.user.create_assistant_manager(db=db, obj_in=obj_in)
    return assistant_manager