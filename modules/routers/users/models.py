import typing as tp

from pydantic import BaseModel

from ...models import User
from ..employees.models import Employee


class GenericResponse(BaseModel):
    status: int = 200
    detail: str = "Success"


class UserOut(GenericResponse):
    user: tp.Optional[User]
    associated_employee: tp.Optional[Employee]


class UserWithPassword(User):
    hashed_password: str


class NewUser(User):
    password: str
