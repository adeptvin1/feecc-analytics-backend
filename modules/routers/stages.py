import typing as tp

from fastapi import APIRouter, Depends

from ..database import MongoDbWrapper
from ..models import ProductionStage
from ..security import check_user_permissions, get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/api/v1/stages")
async def get_production_stages(page: int = 1, items: int = 20, decode_employees: bool = False) -> tp.Dict[str, tp.Any]:
    """
    Endpoint to get list of all production stages from :start: to :limit:. By default, from 0 to 20.
    """
    stages = await MongoDbWrapper().get_all_stages()
    documents_count = await MongoDbWrapper().count_stages()
    if decode_employees:
        for stage in stages:
            if not isinstance(stage.employee_name, str):
                continue
            stage.employee_name = await MongoDbWrapper().decode_employee(stage.employee_name)
    return {"count": documents_count, "data": stages[(page - 1) * items : page * items]}


@router.post("/api/v1/stages", dependencies=[Depends(check_user_permissions)])
async def create_new_stage(stage: ProductionStage) -> None:
    await MongoDbWrapper().add_stage(stage)


@router.delete("/api/v1/stages/{stage_id}", dependencies=[Depends(check_user_permissions)])
async def remove_stage(stage_id: str) -> None:
    await MongoDbWrapper().remove_stage(stage_id)


@router.get("/api/v1/stages/{stage_id}")
async def get_stage_by_id(stage_id: str) -> tp.Optional[ProductionStage]:
    """Endpoint to get information about concrete production stage"""
    return await MongoDbWrapper().get_concrete_stage(stage_id)
