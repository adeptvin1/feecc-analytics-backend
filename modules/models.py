import typing as tp

from pydantic import BaseModel
from datetime import date, datetime


class BaseFilter(BaseModel):
    pass


class User(BaseModel):
    username: str
    hashed_password: str
    is_admin: bool


class TokenData(BaseModel):
    username: tp.Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class Passport(BaseModel):
    model: str
    uuid: str
    internal_id: str
    passport_short_url: tp.Optional[str]
    is_in_db: bool


class PassportsFilter(BaseFilter):
    model: tp.Optional[tp.List[str]]
    uuid: tp.Optional[str]
    internal_id: tp.Optional[str]
    passport_short_url: tp.Optional[str]
    is_in_db: tp.Optional[str]


class Employee(BaseModel):
    rfid_card_id: str
    name: str
    position: str


class ProductionStage(BaseModel):
    name: str
    employee_name: str
    parent_unit_uuid: str
    session_start_time: str
    session_end_time: str
    video_hashes: tp.Optional[tp.List[str]]
    additional_info: tp.Dict[tp.Any, tp.Any]
    id: str
    is_in_db: bool
    creation_time: str
