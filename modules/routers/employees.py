import typing as tp

from fastapi import APIRouter, Depends

from ..database import MongoDbWrapper
from ..models import Employee, EncodedEmployee, User
from ..security import get_current_user
from ..utils import decode_employee

router = APIRouter()


@router.get("/api/v1/employees")
async def get_all_employees(
    page: int = 0, items: int = 20, user: User = Depends(get_current_user)
) -> tp.Dict[str, tp.Any]:
    """
    Endpoint to get list of all employees from :start: to :limit:. By default, from 0 to 20.
    """
    employees = await MongoDbWrapper().get_all_employees()
    documents_count = await MongoDbWrapper().count_employees()
    return {"count": documents_count, "data": employees[(page - 1) * items : page * items]}


@router.get("/api/v1/employees/{rfid_card_id}")
async def get_employee_by_card_id(rfid_card_id: str, user: User = Depends(get_current_user)) -> tp.Optional[Employee]:
    """Endpoint to get information about concrete employee by his rfid card id"""
    return await MongoDbWrapper().get_concrete_employee(rfid_card_id)


@router.post("/api/v1/employees/decode")
async def decode_existing_employee(encoded_employee: EncodedEmployee) -> tp.Optional[Employee]:
    return await decode_employee(await MongoDbWrapper().get_all_employees(), encoded_employee.encoded_name)
