import typing as tp

from fastapi import APIRouter, Depends

from modules.database import MongoDbWrapper

from ..models import User, UserWithPassword
from ..security import create_new_user, get_current_user, get_password_hash

router = APIRouter()


@router.get("/api/v1/users/me")
async def read_users_me(user: User = Depends(get_current_user)) -> User:
    """Returns various information about current user by token"""
    return user


@router.post("/api/v1/users")
async def register_new_user(user: UserWithPassword = Depends(create_new_user)) -> None:
    """Endpoint to create new user"""
    await MongoDbWrapper().add_user(user)
