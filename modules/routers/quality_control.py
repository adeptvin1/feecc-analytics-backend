import typing as tp

from fastapi import APIRouter, Depends
from loguru import logger


from ..database import MongoDbWrapper
from ..exceptions import DatabaseException
from ..models import GenericResponse
from ..dependencies.filters import parse_tcd_filters
from ..dependencies.security import check_user_permissions, get_current_user


router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/protocols")
async def get_protocols(filter=Depends(parse_tcd_filters)) -> None:
    pass


@router.get("/protocols/{internal_id}")
async def get_concrete_protocol(internal_id: str) -> None:
    pass


@router.post("/protocols/{internal_id}")
async def process_protocol(internal_id: str, protocol: tp.List[tp.List[tp.Any]]) -> None:
    pass
