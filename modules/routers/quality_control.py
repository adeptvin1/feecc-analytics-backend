import typing as tp

from fastapi import APIRouter, Depends
from loguru import logger

from ..dependencies.handlers import handle_protocol


from ..database import MongoDbWrapper
from ..exceptions import DatabaseException
from ..models import (
    Employee,
    GenericResponse,
    Protocol,
    ProtocolData,
    ProtocolOut,
    ProtocolsOut,
    TypesOut,
    ProtocolStatus,
)
from ..types import Filter
from ..dependencies.filters import parse_tcd_filters
from ..dependencies.security import get_current_employee, get_current_user


router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/protocols", response_model=ProtocolsOut)
async def get_protocols(filter: Filter = Depends(parse_tcd_filters)) -> ProtocolsOut:
    try:
        protocols = await MongoDbWrapper().get_all_protocols(filter=filter)
    except Exception as exception_message:
        logger.warning(f"Can't get all protocols from DB. Filter: {filter}")
        raise DatabaseException(error=exception_message)
    return ProtocolsOut(data=protocols)


@router.get("/protocols/types")
async def get_protocols_types() -> TypesOut:
    return TypesOut(data=["Первая стадия испытаний", "Вторая стадия испытаний", "Утверждено"])


@router.get("/protocols/{internal_id}")
async def get_concrete_protocol(internal_id: str, employee: Employee = Depends(get_current_employee)) -> ProtocolOut:
    """protocol prototype or protocol data if in DB"""
    protocol: tp.Union[Protocol, ProtocolData, None]
    try:
        protocol = await MongoDbWrapper().get_concrete_protocol(internal_id=internal_id)
        unit = await MongoDbWrapper().get_concrete_passport(internal_id=internal_id)
        if not unit:
            raise DatabaseException(detail=f"Unit with {internal_id} not found. Can't generate protocol for it")
        if not protocol:
            protocol = await MongoDbWrapper().get_concrete_protocol_prototype(associated_with_schema_id=unit.schema_id)
    except Exception as exception_message:
        logger.warning(f"Can't get protocol for unit {internal_id}, exc: {exception_message}")
        raise DatabaseException(detail=exception_message)
    return ProtocolOut(serial_number=unit.serial_number, employee=employee, protocol=protocol)


@router.post("/protocols/{internal_id}")
async def process_protocol(protocol: ProtocolData = Depends(handle_protocol)) -> GenericResponse:
    try:
        await MongoDbWrapper().approve_protocol(internal_id=protocol.associated_unit_id, data=protocol)
    except Exception as exception_message:
        logger.error(f"Can't process protocol for unit {protocol.associated_unit_id}. Exception: {exception_message}")
        logger.debug(f"Protocol: {protocol}")
        raise DatabaseException(detail=exception_message)

    return GenericResponse()
