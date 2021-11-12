import typing as tp

from fastapi import APIRouter, Depends

from ..database import MongoDbWrapper
from ..exceptions import DatabaseException
from ..models import GenericResponse, ProductionStage, ProductionStageOut, ProductionStagesOut
from ..security import check_user_permissions, get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/api/v1/stages", response_model=tp.Union[ProductionStagesOut, GenericResponse])  # type:ignore
async def get_production_stages(page: int = 1, items: int = 20, decode_employees: bool = False) -> ProductionStagesOut:
    """
    Endpoint to get list of all production stages from :start: to :limit:. By default, from 0 to 20.
    """
    stages = await MongoDbWrapper().get_all_stages()
    documents_count = await MongoDbWrapper().count_stages()
    try:
        if decode_employees:
            for stage in stages:
                if not isinstance(stage.employee_name, str):
                    continue
                stage.employee_name = await MongoDbWrapper().decode_employee(stage.employee_name)
        return ProductionStagesOut(count=documents_count, data=stages[(page - 1) * items : page * items])
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)


@router.post("/api/v1/stages", dependencies=[Depends(check_user_permissions)], response_model=GenericResponse)
async def create_new_stage(stage: ProductionStage) -> GenericResponse:
    try:
        await MongoDbWrapper().add_stage(stage)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Created new production stage")


@router.delete(
    "/api/v1/stages/{stage_id}", dependencies=[Depends(check_user_permissions)], response_model=GenericResponse
)
async def remove_stage(stage_id: str) -> GenericResponse:
    try:
        await MongoDbWrapper().remove_stage(stage_id)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail=f"Deleted stage with id {stage_id}")


@router.get("/api/v1/stages/{stage_id}", response_model=tp.Union[ProductionStageOut, GenericResponse])  # type:ignore
async def get_stage_by_id(stage_id: str) -> ProductionStageOut:
    """Endpoint to get information about concrete production stage"""
    try:
        stage = await MongoDbWrapper().get_concrete_stage(stage_id)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return ProductionStageOut(stage=stage)
