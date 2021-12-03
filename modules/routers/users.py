import typing as tp

from fastapi import APIRouter, Depends

from ..database import MongoDbWrapper
from ..exceptions import DatabaseException
from ..models import GenericResponse, User, UserOut, UserWithPassword, NewUser
from ..security import check_user_permissions, create_new_user, get_current_user

router = APIRouter()


@router.get("/me", response_model=tp.Union[UserOut, GenericResponse])  # type:ignore
async def read_users_me(user: User = Depends(get_current_user)) -> UserOut:
    """Returns various information about current user by token"""
    return UserOut(user=user)


@router.post("/", response_model=GenericResponse, dependencies=[Depends(check_user_permissions)])
async def register_new_user(user: UserWithPassword = Depends(create_new_user)) -> GenericResponse:
    """Endpoint to create new user"""
    try:
        await MongoDbWrapper().add_user(user)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Created new user")


@router.get(
    "/{username}",
    dependencies=[Depends(get_current_user)],
    response_model=tp.Union[UserOut, GenericResponse],  # type:ignore
)
async def get_user_data(username: str) -> tp.Union[UserOut, GenericResponse]:
    """Get information about concrete user"""
    try:
        user = await MongoDbWrapper().get_concrete_user(username)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    if user is None:
        return GenericResponse(status_code=404, detail="Not found")
    return UserOut(user=user)


@router.delete(
    "/{username}",
    dependencies=[Depends(check_user_permissions)],
    response_model=GenericResponse,
)
async def delete_user(username: str) -> GenericResponse:
    """Delete concrete user by username"""
    try:
        await MongoDbWrapper().remove_user(username)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Deleted user")


@router.patch(
    "/{username}",
    dependencies=[Depends(check_user_permissions)],
    response_model=GenericResponse,
)
async def patch_user(username: str, user_data: UserWithPassword = Depends(create_new_user)) -> GenericResponse:
    """Edit concrete user's credentials by username"""
    try:
        await MongoDbWrapper().edit_user(username=username, new_user_data=user_data)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Patched user")
