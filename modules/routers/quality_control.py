import typing as tp

from fastapi import APIRouter, Depends
from loguru import logger

from ..database import MongoDbWrapper
from ..exceptions import DatabaseException
from ..models import GenericResponse
from ..dependencies.security import check_user_permissions, get_current_user


router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/")
async def testing() -> None:
    pass
