import typing as tp
from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger

from modules.database import MongoDbWrapper
from modules.exceptions import AuthException
from modules.models import Token, User
from modules.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    get_current_user,
    oauth2_scheme,
)

api = FastAPI()


@api.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> tp.Dict[str, str]:
    """
    Endpoint for user-auth

    Returns bearer jwt token
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed to login user {form_data.username}")
        raise AuthException
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@api.get("/api/v1/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)) -> User:
    """Returns various information about current user by token"""
    public_data = dict(current_user).copy()
    del public_data["hashed_password"]
    return public_data


@api.get("/api/v1/status")
async def get_server_status() -> tp.Dict[str, str]:
    """Endpoint to get server status"""
    return {"status": "ok"}


@api.get("/api/v1/employees")
async def get_all_employees(start: int = 0, limit: int = 20, token: str = Depends(oauth2_scheme)):
    """
    Endpoint to get list of all employees from :start: to :limit:. By default, from 0 to 20.
    """
    employees = await MongoDbWrapper().get_all_employees()
    if limit:
        return employees[start:limit]
    return employees[start:]


@api.get("/api/v1/employees/{rfid_card_id}")
async def get_employee_by_card_id(rfid_card_id: str, token: str = Depends(oauth2_scheme)):
    """Endpoint to get information about concrete employee by his rfid card id"""
    return await MongoDbWrapper().get_concrete_employee(rfid_card_id)


@api.get("/api/v1/passports")
async def get_all_passports(start: int = 0, limit: int = 20, token: str = Depends(oauth2_scheme)):
    """
    Endpoint to get list of all issued passports from :start: to :limit:. By default, from 0 to 20.
    """
    passports = await MongoDbWrapper().get_all_passports()
    if limit:
        return passports[start:limit]
    return passports[start:]


@api.get("/api/v1/passports/{internal_id}")
async def get_passport_by_internal_id(internal_id: str, token: str = Depends(oauth2_scheme)):
    """Endpoint to get information about concrete issued passport"""
    return await MongoDbWrapper().get_concrete_passport(internal_id)


@api.get("/api/v1/stages")
async def get_production_stages(start: int = 0, limit: int = 20, token: str = Depends(oauth2_scheme)):
    """
    Endpoint to get list of all production stages from :start: to :limit:. By default, from 0 to 20.
    """
    stages = await MongoDbWrapper().get_all_stages()
    if limit:
        return stages[start:limit]
    return stages[start:]


@api.get("/api/v1/stages/{stage_id}")
async def get_stage_by_id(stage_id: str, token: str = Depends(oauth2_scheme)):
    """Endpoint to get information about concrete production stage"""
    return await MongoDbWrapper().get_concrete_stage(stage_id)


@api.post("/api/v1/employees/decode")
async def decode_employee():
    pass
