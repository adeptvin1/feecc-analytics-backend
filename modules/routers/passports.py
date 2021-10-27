import typing as tp

from fastapi import APIRouter, Depends

from ..database import MongoDbWrapper
from ..models import DatabaseEntryFields, Passport, User
from ..security import check_user_permissions, get_current_user

router = APIRouter()


@router.get("/api/v1/passports")
async def get_all_passports(
    page: int = 0, items: int = 20, user: User = Depends(get_current_user)
) -> tp.Dict[str, tp.Any]:
    """
    Endpoint to get list of all issued passports from :start: to :limit:. By default, from 0 to 20.
    """
    passports = await MongoDbWrapper().get_all_passports()
    documents_count = await MongoDbWrapper().count_passports()
    return {"count": documents_count, "data": passports[(page - 1) * items : page * items]}


@router.post("/api/v1/passports")
async def create_new_passport(passport: Passport, user=Depends(check_user_permissions)) -> None:
    """Endpoint to create a new passport"""
    await MongoDbWrapper().add_passport(passport)


@router.delete("/api/v1/passports/{internal_id}")
async def delete_passport(internal_id: str, user=Depends(check_user_permissions)) -> None:
    """Endpoint to delete an existing passport from database"""
    await MongoDbWrapper().remove_passport(internal_id)


@router.get("/api/v1/passports/fields")
async def get_passport_entry_fields() -> DatabaseEntryFields:
    # TODO
    await MongoDbWrapper()._get_fields_from_collection()


@router.get("/api/v1/passports/{internal_id}")
async def get_passport_by_internal_id(
    internal_id: str, user: User = Depends(get_current_user)
) -> tp.Optional[Passport]:
    """Endpoint to get information about concrete issued passport"""
    return await MongoDbWrapper().get_concrete_passport(internal_id)
