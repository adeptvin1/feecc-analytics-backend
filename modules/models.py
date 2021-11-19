from __future__ import annotations

import hashlib
import typing as tp
from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class GenericResponse(BaseModel):
    status_code: int = 200
    detail: tp.Optional[str] = "Successful"


class User(BaseModel):
    username: str
    is_admin: bool = False


class UserOut(GenericResponse):
    user: tp.Optional[User]


class UserWithPassword(User):
    hashed_password: str


class NewUser(User):
    password: str


class TokenData(BaseModel):
    username: tp.Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class ProductionSchemaStage(BaseModel):
    name: str
    type: tp.Optional[str] = None
    description: tp.Optional[str] = None
    equipment: tp.Optional[tp.List[str]] = None
    workplace: tp.Optional[str] = None
    duration_seconds: tp.Optional[int] = None


class ProductionSchema(BaseModel):
    schema_id: str = Field(default_factory=lambda: uuid4().hex)
    unit_name: str
    production_stages: tp.Optional[tp.List[ProductionSchemaStage]] = None
    required_components_schema_ids: tp.Optional[tp.List[str]] = None
    parent_schema_id: tp.Optional[str] = None


class ProductionSchemasOut(GenericResponse):
    count: int
    data: tp.List[ProductionSchema]


class ProductionSchemaOut(GenericResponse):
    schema_: tp.Annotated[tp.Optional[ProductionSchema], Field(alias="schema")]


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


class Barcode(BaseModel):
    unit_code: tp.Optional[str]
    barcode: tp.Optional[str]
    basename: tp.Optional[str]
    filename: tp.Optional[str]


class Passport(BaseModel):
    uuid: str
    internal_id: str
    passport_short_url: tp.Optional[str]
    is_in_db: bool
    _schema: tp.Annotated[tp.Optional[ProductionSchema], Field(alias="schema")]
    biography: tp.Optional[tp.List[ProductionStage]]
    components_units: tp.Optional[tp.Dict[str, tp.Any]] = None
    featured_in_int_id: tp.Optional[str]
    barcode: tp.Optional[Barcode]
    model: tp.Optional[str] = None


class PassportsOut(GenericResponse):
    count: int
    data: tp.List[Passport]


class PassportOut(GenericResponse):
    passport: tp.Optional[Passport]


class EncodedEmployee(BaseModel):
    encoded_name: str


class EmployeesOut(GenericResponse):
    count: int
    data: tp.Optional[tp.List[Employee]]


class EmployeeOut(GenericResponse):
    employee: tp.Optional[Employee]


class ProductionStagesOut(GenericResponse):
    count: int
    data: tp.List[ProductionStage]


class ProductionStageOut(GenericResponse):
    stage: tp.Optional[ProductionStage]


class IPFSData(BaseModel):
    id: str
    model: str
    stages: tp.List[tp.Dict[str, tp.Union[tp.List[str], str]]]


class DatabaseEntryFields(BaseModel):
    fields: tp.List[str]
