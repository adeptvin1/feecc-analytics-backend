import yaml
import typing as tp

from modules.models import Employee


async def decode_employee(employees: tp.List[Employee], hashed_employee: str) -> tp.Optional[Employee]:
    """Find an employee by hashed data"""
    for employee in employees:
        encoded_employee = await employee.encode_sha256()
        print(encoded_employee)
        if encoded_employee == hashed_employee:
            return employee
    return None


async def load_yaml(data: str) -> str:
    return yaml.load(data, Loader=yaml.SafeLoader)
