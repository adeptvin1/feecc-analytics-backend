import typing as tp

from fastapi import APIRouter, Depends

from ..database import MongoDbWrapper
from ..exceptions import DatabaseException
from ..models import GenericResponse, User, UserOut, UserWithPassword
from ..security import create_new_user, get_current_user

router = APIRouter()


@router.get("/api/v1/users/me", response_model=tp.Union[UserOut, GenericResponse])
async def read_users_me(user: User = Depends(get_current_user)) -> User:
    """Returns various information about current user by token"""
    return UserOut(user=user)


@router.post("/api/v1/users", response_model=GenericResponse)
async def register_new_user(user: UserWithPassword = Depends(create_new_user)) -> GenericResponse:
    """Endpoint to create new user"""
    try:
        await MongoDbWrapper().add_user(user)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Created new user")
