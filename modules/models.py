import hashlib
import typing as tp
from datetime import date, datetime

from pydantic import BaseModel


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

    async def compose(self) -> str:
        print(" ".join([self.rfid_card_id, self.name, self.position]))
        return " ".join([self.rfid_card_id, self.name, self.position])

    async def encode_sha256(self) -> str:
        employee_passport_string: str = await self.compose()
        employee_passport_string_encoded: bytes = employee_passport_string.encode()
        employee_passport_code: str = hashlib.sha256(employee_passport_string_encoded).hexdigest()
        return employee_passport_code


class EncodedEmployee(BaseModel):
    encoded_name: str


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
    creation_time: tp.Optional[datetime]
