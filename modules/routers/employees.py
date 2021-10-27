import typing as tp

from fastapi import APIRouter, Depends

from ..database import MongoDbWrapper
from ..exceptions import ForbiddenActionException
from ..models import Employee, EncodedEmployee, User
from ..security import get_current_user, check_user_permissions
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


@router.post("/api/v1/employees")
async def create_new_employee(employee_data: Employee, user=Depends(check_user_permissions)) -> None:
    """Endpoint to create new employee"""
    await MongoDbWrapper().add_employee(employee_data)


@router.delete("/api/v1/employees/{rfid_card_id}")
async def delete_employee(rfid_card_id: str, user=Depends(check_user_permissions)) -> None:
    """Endpoint to delete employee from database"""
    await MongoDbWrapper().remove_employee(rfid_card_id)


@router.get("/api/v1/employees/{rfid_card_id}")
async def get_employee_by_card_id(rfid_card_id: str, user: User = Depends(get_current_user)) -> tp.Optional[Employee]:
    """Endpoint to get information about concrete employee by his rfid card id"""
    return await MongoDbWrapper().get_concrete_employee(rfid_card_id)


@router.post("/api/v1/employees/decode")
async def decode_existing_employee(encoded_employee: EncodedEmployee) -> tp.Optional[Employee]:
    return await decode_employee(await MongoDbWrapper().get_all_employees(), encoded_employee.encoded_name)
