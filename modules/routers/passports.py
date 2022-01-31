import typing as tp

from fastapi import APIRouter, Depends
from loguru import logger

from ..database import MongoDbWrapper
from ..exceptions import DatabaseException
from ..models import GenericResponse, Passport, PassportOut, PassportsOut, ProductionStage
from ..dependencies.security import check_user_permissions, get_current_user
from ..dependencies.filters import parse_passports_filter
from ..types import Filter


router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/", response_model=tp.Union[PassportsOut, GenericResponse])  # type:ignore
async def get_all_passports(
    page: int = 1,
    items: int = 20,
    filter: Filter = Depends(parse_passports_filter),
) -> PassportsOut:
    """
    Endpoint to get list of all issued units from :start: to :limit:. By default, from 0 to 20.
    """
    logger.debug(f"Filter: {filter}")
    try:
        passports = (await MongoDbWrapper().get_passports(filter))[(page - 1) * items : page * items]
        documents_count = await MongoDbWrapper().count_passports(filter)

        for passport in passports:
            passport.biography = await MongoDbWrapper().get_stages(uuid=passport.uuid)
            passport.date = await MongoDbWrapper().get_passport_creation_date(uuid=passport.uuid)
    except Exception as exception_message:
        logger.error(
            f"Failed to get units from page {page} (count: {items}, filter: {filter}). Exception: {exception_message}"
        )
        raise DatabaseException(error=exception_message)

    return PassportsOut(count=documents_count, data=passports)


@router.post("/", dependencies=[Depends(check_user_permissions)], response_model=GenericResponse)
async def create_new_passport(passport: Passport) -> GenericResponse:
    """Endpoint to create a new unit"""
    try:
        await MongoDbWrapper().add_passport(passport)
    except Exception as exception_message:
        logger.error(f"Failed to create new unit ({passport.dict()}). Exception: {exception_message}")
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Created new unit")


@router.delete("/{internal_id}", dependencies=[Depends(check_user_permissions)], response_model=GenericResponse)
async def delete_passport(internal_id: str) -> GenericResponse:
    """Endpoint to delete an existing unit from database"""
    try:
        await MongoDbWrapper().remove_passport(internal_id)
    except Exception as exception_message:
        logger.error(f"Failed to delete unit {internal_id}. Exception: {exception_message}")
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Deleted unit")


@router.get("/{internal_id}", response_model=tp.Union[PassportOut, GenericResponse])  # type:ignore
async def get_passport_by_internal_id(internal_id: str) -> tp.Union[PassportOut, GenericResponse]:
    """Endpoint to get information about concrete issued unit"""
    try:
        passport = await MongoDbWrapper().get_concrete_passport(internal_id)
    except Exception as exception_message:
        logger.error(f"Failed to get unit {internal_id}. Exception: {exception_message}")
        raise DatabaseException(error=exception_message)
    if passport is None:
        logger.error(f"Unknown unit {internal_id}")
        return GenericResponse(status_code=404, detail="Not found")
    return PassportOut(passport=passport)


@router.patch("/{internal_id}", dependencies=[Depends(check_user_permissions)], response_model=GenericResponse)
async def patch_passport(internal_id: str, new_data: Passport) -> GenericResponse:
    """
    Edit concrete unit data.
    Ignored fields: {"uuid", "internal_id", "is_in_db", "featured_in_int_id"}. Send null instead.
    """
    try:
        await MongoDbWrapper().edit_passport(internal_id=internal_id, new_passport_data=new_data)
    except Exception as exception_message:
        logger.error(f"Failed to patch unit {internal_id} with data {new_data.dict()}. Exception: {exception_message}")
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Successfully patched unit")


@router.post("/{internal_id}/add_stage", dependencies=[Depends(check_user_permissions)], response_model=GenericResponse)
async def add_stage_to_passport(internal_id: str, new_stage: ProductionStage) -> GenericResponse:
    try:
        await MongoDbWrapper().add_stage_to_passport(passport_id=internal_id, stage=new_stage)
    except Exception as exception_message:
        logger.error(f"Failed to add new production stage to unit {internal_id}. Exception: {exception_message}")
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Successfully added stage to unit")
