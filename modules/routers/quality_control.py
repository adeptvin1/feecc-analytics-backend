import typing as tp

from fastapi import APIRouter, Depends
from loguru import logger

from ..dependencies.handlers import handle_protocol


from ..database import MongoDbWrapper
from ..exceptions import DatabaseException
from ..models import GenericResponse, ProtocolData
from ..types import Filter
from ..dependencies.filters import parse_tcd_filters
from ..dependencies.security import check_user_permissions, get_current_user


router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/protocols")
async def get_protocols(filter: Filter = Depends(parse_tcd_filters)) -> None:
    try:
        pass
    except Exception:
        pass


@router.get("/protocols/{internal_id}")
async def get_concrete_protocol(internal_id: str) -> None:
    try:
        pass
    except Exception:
        pass


@router.post("/protocols/{internal_id}")
async def process_protocol(protocol: ProtocolData = Depends(handle_protocol)) -> GenericResponse:
    try:
        pass
    except Exception:
        pass
