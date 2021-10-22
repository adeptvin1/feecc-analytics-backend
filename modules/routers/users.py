import typing as tp

from fastapi import APIRouter, Depends

from ..models import User
from ..security import get_current_user

router = APIRouter()


@router.get("/api/v1/users/me")
async def read_users_me(user: User = Depends(get_current_user)) -> tp.Dict[str, tp.Any]:
    """Returns various information about current user by token"""
    public_data = dict(user).copy()
    del public_data["hashed_password"]
    return public_data
