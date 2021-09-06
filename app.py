import typing as tp

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClientEncryption
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from modules.database import MongoDbWrapper
from modules.security import oauth2_scheme, fake_users, User, fake_hash_password, get_current_user

api = FastAPI()


@api.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = User(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


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
async def get_employee_by_card_id(rfid_card_id: str):
    return await MongoDbWrapper().get_concrete_employee(rfid_card_id)


@api.get("/api/v1/passports")
async def get_all_passports():
    return await MongoDbWrapper().get_all_passports()


@api.get("/api/v1/passports/{internal_id}")
async def get_passport_by_internal_id(internal_id: str):
    return await MongoDbWrapper().get_concrete_passport(internal_id)


@api.get("/api/v1/stages")
async def get_production_stages():
    return await MongoDbWrapper().get_all_stages()


@api.get("/api/v1/stages/{stage_id}")
async def get_stage_by_id(stage_id: str):
    return await MongoDbWrapper().get_concrete_stage(stage_id)


@api.post("/api/v1/employees/decode")
async def decode_employee():
    pass
