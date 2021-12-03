import typing as tp

from fastapi import APIRouter, Depends

from ..database import MongoDbWrapper
from ..exceptions import DatabaseException
from ..models import GenericResponse, Passport, PassportOut, PassportsOut
from ..security import check_user_permissions, get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/", response_model=tp.Union[PassportsOut, GenericResponse])  # type:ignore
async def get_all_passports(page: int = 1, items: int = 20) -> PassportsOut:
    """
    Endpoint to get list of all issued passports from :start: to :limit:. By default, from 0 to 20.
    """
    try:
        passports = await MongoDbWrapper().get_all_passports()
        documents_count = await MongoDbWrapper().count_passports()
    except Exception as exception_message:
        print(exception_message)
        raise DatabaseException(error=exception_message)

    return PassportsOut(count=documents_count, data=passports[(page - 1) * items : page * items])


@router.post("/", dependencies=[Depends(check_user_permissions)], response_model=GenericResponse)
async def create_new_passport(passport: Passport) -> GenericResponse:
    """Endpoint to create a new passport"""
    try:
        await MongoDbWrapper().add_passport(passport)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Created new passport")


@router.delete("/{internal_id}", dependencies=[Depends(check_user_permissions)], response_model=GenericResponse)
async def delete_passport(internal_id: str) -> GenericResponse:
    """Endpoint to delete an existing passport from database"""
    try:
        await MongoDbWrapper().remove_passport(internal_id)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Deleted passport")


@router.get("/{internal_id}", response_model=tp.Union[PassportOut, GenericResponse])  # type:ignore
async def get_passport_by_internal_id(internal_id: str) -> tp.Union[PassportOut, GenericResponse]:
    """Endpoint to get information about concrete issued passport"""
    try:
        passport = await MongoDbWrapper().get_concrete_passport(internal_id)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    if passport is None:
        return GenericResponse(status_code=404, detail="Not found")
    return PassportOut(passport=passport)


@router.patch("/{internal_id}", response_model=GenericResponse)
async def patch_passport(internal_id: str, new_data: Passport) -> GenericResponse:
    """
    Edit concrete user's credentials by username.
    Ignored fields: {"uuid", "internal_id", "is_in_db", "featured_in_int_id"}. Send anything, nothing will be changed
    """
    try:
        await MongoDbWrapper().edit_passport(internal_id=internal_id, new_passport_data=new_data)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Patched passport")
