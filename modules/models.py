from __future__ import annotations
import enum

import hashlib
import typing as tp
from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class GenericResponse(BaseModel):
    status_code: int = 200
    detail: tp.Optional[str] = "Successful"


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


class User(BaseModel):
    username: str
    rule_set: tp.List[str] = ["read"]
    associated_employee: tp.Optional[str]


class UserOut(GenericResponse):
    user: tp.Optional[User]
    associated_employee: tp.Optional[Employee]


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
    stage_id: str


class ProductionSchema(BaseModel):
    schema_id: str = Field(default_factory=lambda: uuid4().hex)
    unit_name: str
    production_stages: tp.Optional[tp.List[ProductionSchemaStage]] = None
    required_components_schema_ids: tp.Optional[tp.List[str]] = None
    parent_schema_id: tp.Optional[str] = None
    schema_type: str


class ProductionSchemasOut(GenericResponse):
    count: int
    data: tp.List[ProductionSchema]


class ProductionSchemaOut(GenericResponse):
    schema_: tp.Annotated[tp.Optional[ProductionSchema], Field(alias="schema")]


class ProductionStage(BaseModel):
    name: str
    employee_name: tp.Optional[str]
    parent_unit_uuid: str
    session_start_time: tp.Optional[str]
    session_end_time: tp.Optional[str]
    ended_prematurely: bool
    video_hashes: tp.Optional[tp.List[str]]
    additional_info: tp.Optional[tp.Dict[tp.Any, tp.Any]]
    id: str = Field(default_factory=lambda: uuid4().hex)
    is_in_db: bool
    creation_time: datetime
    schema_stage_id: tp.Optional[str]

    completed: tp.Optional[bool]
    number: tp.Optional[int]

    async def clear(self, number: int) -> ProductionStage:
        return ProductionStage(
            name=self.name,
            parent_unit_uuid=self.parent_unit_uuid,
            ended_prematurely=False,
            is_in_db=True,
            creation_time=datetime.now(),
            session_start_time=None,
            session_end_time=None,
            completed=False,
            number=number,
            additional_info={},
            schema_stage_id=self.schema_stage_id,
        )


class ProductionStageData(ProductionStage):
    unit_name: tp.Optional[str]
    parent_unit_internal_id: tp.Optional[str]


class UnitStatus(str, enum.Enum):
    production = "production"
    built = "built"
    revision = "revision"
    approved = "approved"
    finalized = "finalized"


class Passport(BaseModel):
    schema_id: tp.Optional[str] = None
    uuid: str = Field(default_factory=lambda: uuid4().hex)
    internal_id: str
    passport_short_url: tp.Optional[str]
    passport_ipfs_cid: tp.Optional[str] = None
    is_in_db: bool
    featured_in_int_id: tp.Optional[str]
    biography: tp.Optional[tp.List[ProductionStageData]]
    components_internal_ids: tp.Optional[tp.List[str]]
    model: tp.Optional[str] = None
    date: datetime = Field(alias="creation_time")
    type: tp.Optional[str] = None
    parential_unit: tp.Optional[str] = None
    serial_number: tp.Optional[str] = None
    status: tp.Optional[UnitStatus] = None


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


class TypesOut(GenericResponse):
    data: tp.List[str]


class OrderBy(str, enum.Enum):
    descending = "asc"
    ascending = "desc"


class ProtocolStatus(str, enum.Enum):
    approved = "approved"
    finalized = "finalized"


class ProtocolRow(BaseModel):
    name: str
    value: str
    deviation: tp.Optional[str] = None
    test1: tp.Optional[str]
    test2: tp.Optional[str]
    checked: bool = False


class Protocol(BaseModel):
    protocol_name: str
    protocol_schema_id: str
    associated_with_schema_id: str
    rows: tp.List[ProtocolRow]


class ProtocolData(Protocol):
    protocol_id: str = Field(default_factory=lambda: uuid4().hex)
    associated_unit_id: str


class ProtocolOut(BaseModel):
    serial_number: str
    internal_id: str
    stage: int
    employee: Employee
