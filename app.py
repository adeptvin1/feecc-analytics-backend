import typing as tp
from datetime import timedelta

import httpx
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger
from yaml.error import YAMLError

from modules.database import MongoDbWrapper
from modules.exceptions import (
    AuthException,
    ConnectionTimeoutException,
    IncorrectAddressException,
    ParserException,
    UnhandledException,
)
from modules.models import Employee, EncodedEmployee, IPFSData, Passport, ProductionStage, Token, User
from modules.security import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_current_user
from modules.utils import decode_employee, load_yaml

api = FastAPI()

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@api.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> tp.Dict[str, str]:
    """
    Endpoint for user-auth

    Returns bearer jwt token
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed to login user {form_data.username}")
        raise AuthException
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@api.get("/api/v1/users/me")
async def read_users_me(user: User = Depends(get_current_user)) -> tp.Dict[str, tp.Any]:
    """Returns various information about current user by token"""
    public_data = dict(user).copy()
    del public_data["hashed_password"]
    return public_data


@api.get("/api/v1/status")
async def get_server_status() -> tp.Dict[str, str]:
    """Endpoint to get server status"""
    return {"status": "ok"}


@api.get("/api/v1/employees")
async def get_all_employees(
    page: int = 0, items: int = 20, user: User = Depends(get_current_user)
) -> tp.Dict[str, tp.Any]:
    """
    Endpoint to get list of all employees from :start: to :limit:. By default, from 0 to 20.
    """
    employees = await MongoDbWrapper().get_all_employees()
    documents_count = await MongoDbWrapper().count_employees()
    return {"count": documents_count, "data": employees[(page - 1) * items : page * items]}


@api.get("/api/v1/employees/{rfid_card_id}")
async def get_employee_by_card_id(rfid_card_id: str, user: User = Depends(get_current_user)) -> tp.Optional[Employee]:
    """Endpoint to get information about concrete employee by his rfid card id"""
    return await MongoDbWrapper().get_concrete_employee(rfid_card_id)


@api.post("/api/v1/passports")
async def get_all_passports(
    page: int = 0,
    items: int = 20,
    user: User = Depends(get_current_user),
) -> tp.Dict[str, tp.Any]:
    """
    Endpoint to get list of all issued passports from :start: to :limit:. By default, from 0 to 20.
    """
    passports = await MongoDbWrapper().get_all_passports()
    documents_count = await MongoDbWrapper().count_passports()
    return {"count": documents_count, "data": passports[(page - 1) * items : page * items]}


@api.get("/api/v1/passports/{internal_id}")
async def get_passport_by_internal_id(
    internal_id: str, user: User = Depends(get_current_user)
) -> tp.Optional[Passport]:
    """Endpoint to get information about concrete issued passport"""
    return await MongoDbWrapper().get_concrete_passport(internal_id)


@api.get("/api/v1/stages")
async def get_production_stages(
    page: int = 0, items: int = 20, user: User = Depends(get_current_user)
) -> tp.Dict[str, tp.Any]:
    """
    Endpoint to get list of all production stages from :start: to :limit:. By default, from 0 to 20.
    """
    stages = await MongoDbWrapper().get_all_stages()
    documents_count = await MongoDbWrapper().count_stages()
    return {"count": documents_count, "data": stages[(page - 1) * items : page * items]}


@api.get("/api/v1/stages/{stage_id}")
async def get_stage_by_id(stage_id: str, user: User = Depends(get_current_user)) -> tp.Optional[ProductionStage]:
    """Endpoint to get information about concrete production stage"""
    return await MongoDbWrapper().get_concrete_stage(stage_id)


@api.post("/api/v1/employees/decode")
async def decode_existing_employee(encoded_employee: EncodedEmployee) -> tp.Optional[Employee]:
    return await decode_employee(await MongoDbWrapper().get_all_employees(), encoded_employee.encoded_name)


@api.get("/api/v1/ipfs_decode")
async def parse_ipfs_link(link: str) -> IPFSData:
    """ Extracts data from IPFS/Pinata """
    if not link.startswith(("http://", "https://")):
        raise IncorrectAddressException

    try:
        async with httpx.AsyncClient() as client:
            request = await client.get(link)
            return await load_yaml(request.text)
    except httpx.ReadTimeout:
        raise ConnectionTimeoutException
    except YAMLError:
        raise ParserException
    except Exception as exception:
        raise UnhandledException(error=exception)


@api.get("/api/v1/validate")
async def validate_stages() -> tp.List[bool]:
    pass
