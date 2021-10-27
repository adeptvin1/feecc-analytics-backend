import typing as tp

from fastapi import APIRouter, Depends

from ..database import MongoDbWrapper
from ..models import ProductionStage, User
from ..security import get_current_user
from ..utils import decode_employee

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/api/v1/stages")
async def get_production_stages(page: int = 1, items: int = 20, decode_employees: bool = False) -> tp.Dict[str, tp.Any]:
    """
    Endpoint to get list of all production stages from :start: to :limit:. By default, from 0 to 20.
    """
    stages = await MongoDbWrapper().get_all_stages()
    documents_count = await MongoDbWrapper().count_stages()
    if decode_employees:
        employees = await MongoDbWrapper().get_all_employees()
        for stage in stages:
            stage.employee_name = await decode_employee(employees, stage.employee_name)
    return {"count": documents_count, "data": stages[(page - 1) * items : page * items]}


@router.get("/api/v1/stages/{stage_id}")
async def get_stage_by_id(stage_id: str) -> tp.Optional[ProductionStage]:
    """Endpoint to get information about concrete production stage"""
    return await MongoDbWrapper().get_concrete_stage(stage_id)
