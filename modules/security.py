from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

fake_users = {"123": {"username": "123", "hashed_password": "123321"}}


class User(BaseModel):
    username: str
    hashed_password: str


def fake_hash_password(password: str):
    return password + "321"


def get_user(username: str):
    if username in fake_users:
        user_dict = fake_users[username]
        return User(**user_dict)


def fake_decode_token(token):
    user = get_user(token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
