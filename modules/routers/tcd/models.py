from __future__ import annotations

import enum
import typing as tp
from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field

from ..employees.models import Employee


class GenericResponse(BaseModel):
    status: int = 200
    detail: str = "Success"


class ProtocolStatus(str, enum.Enum):
    first = "Первая стадия испытаний пройдена"
    second = "Вторая стадия испытаний пройдена"
    third = "Протокол утверждён"

    @tp.no_type_check
    async def switch(self) -> ProtocolStatus:
        if self.value == self.first:
            return ProtocolStatus(self.second.value)
        elif self.value == self.second:
            return ProtocolStatus(self.third.value)
        else:
            return ProtocolStatus(self.third.value)

    @property
    async def is_approved(self) -> bool:
        return bool(self.value == self.third)


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
    default_serial_number: tp.Optional[str]
    rows: tp.List[ProtocolRow]


class ProtocolData(Protocol):
    protocol_id: str = Field(default_factory=lambda: uuid4().hex)
    associated_unit_id: str
    status: ProtocolStatus = ProtocolStatus.first
    creation_time: datetime = Field(default_factory=datetime.now)


class ProtocolOut(GenericResponse):
    serial_number: tp.Optional[str]
    employee: tp.Optional[Employee]
    protocol: tp.Union[ProtocolData, Protocol]


class ProtocolsOut(GenericResponse):
    data: tp.List[ProtocolData]


class TypesOut(GenericResponse):
    data: tp.List[str]
