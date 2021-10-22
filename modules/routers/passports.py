import typing as tp

from fastapi import APIRouter, Depends

from ..database import MongoDbWrapper
from ..models import Passport, User
from ..security import get_current_user

router = APIRouter()


@router.post("/api/v1/passports")
async def get_all_passports(
    page: int = 0, items: int = 20, user: User = Depends(get_current_user)
) -> tp.Dict[str, tp.Any]:
    """
    Endpoint to get list of all issued passports from :start: to :limit:. By default, from 0 to 20.
    """
    passports = await MongoDbWrapper().get_all_passports()
    documents_count = await MongoDbWrapper().count_passports()
    return {"count": documents_count, "data": passports[(page - 1) * items : page * items]}


@router.get("/api/v1/passports/{internal_id}")
async def get_passport_by_internal_id(
    internal_id: str, user: User = Depends(get_current_user)
) -> tp.Optional[Passport]:
    """Endpoint to get information about concrete issued passport"""
    return await MongoDbWrapper().get_concrete_passport(internal_id)
