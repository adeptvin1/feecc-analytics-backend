import typing as tp
from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from modules.database import MongoDbWrapper
from modules.models import Token, User
from modules.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    get_current_user,
    oauth2_scheme,
)

api = FastAPI()


@api.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}


@api.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@api.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@api.get("/api/v1/status")
async def get_server_status() -> tp.Dict[str, str]:
    return {"status": "ok"}


@api.get("/api/v1/employees")
async def get_all_employees(token: str = Depends(oauth2_scheme)):
    return await MongoDbWrapper().get_all_employees()


@api.get("/api/v1/employees/{rfid_card_id}")
async def get_employee_by_card_id(rfid_card_id: str, token: str = Depends(oauth2_scheme)):
    return await MongoDbWrapper().get_concrete_employee(rfid_card_id)


@api.get("/api/v1/passports")
async def get_all_passports(token: str = Depends(oauth2_scheme)):
    return await MongoDbWrapper().get_all_passports()


@api.get("/api/v1/passports/{internal_id}")
async def get_passport_by_internal_id(internal_id: str, token: str = Depends(oauth2_scheme)):
    return await MongoDbWrapper().get_concrete_passport(internal_id)


@api.get("/api/v1/stages")
async def get_production_stages(token: str = Depends(oauth2_scheme)):
    return await MongoDbWrapper().get_all_stages()


@api.get("/api/v1/stages/{stage_id}")
async def get_stage_by_id(stage_id: str, token: str = Depends(oauth2_scheme)):
    return await MongoDbWrapper().get_concrete_stage(stage_id)


@api.post("/api/v1/employees/decode")
async def decode_employee():
    pass
