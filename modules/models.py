import hashlib
import typing as tp
from datetime import datetime

from pydantic import BaseModel


class GenericResponse(BaseModel):
    status_code: int = 200
    detail: tp.Optional[str] = "Successful"


class User(BaseModel):
    username: str
    is_admin: bool


class UserWithPassword(User):
    hashed_password: str


class NewUser(User):
    password: str


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


class Employee(BaseModel):
    rfid_card_id: str
    name: str
    position: str

    async def compose(self) -> str:
        return " ".join([self.rfid_card_id, self.name, self.position])

    async def encode_sha256(self) -> str:
        employee_passport_string: str = await self.compose()
        employee_passport_string_encoded: bytes = employee_passport_string.encode()
        employee_passport_code: str = hashlib.sha256(employee_passport_string_encoded).hexdigest()
        return employee_passport_code


class EncodedEmployee(BaseModel):
    encoded_name: str


class EmployeesOut(GenericResponse):
    count: int
    data: tp.Optional[tp.List[Employee]]


class EmployeeOut(GenericResponse):
    employee: tp.Optional[Employee]


class ProductionStage(BaseModel):
    name: str
    employee_name: tp.Optional[tp.Union[str, Employee]]
    parent_unit_uuid: str
    session_start_time: str
    session_end_time: tp.Optional[str]
    video_hashes: tp.Optional[tp.List[str]]
    additional_info: tp.Dict[tp.Any, tp.Any]
    id: str
    is_in_db: bool
    creation_time: tp.Optional[datetime]


class IPFSData(BaseModel):
    id: str
    model: str
    stages: tp.List[tp.Dict[str, tp.Union[tp.List[str], str]]]


class DatabaseEntryFields(BaseModel):
    fields: tp.List[str]
