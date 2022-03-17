import time
import typing as tp

import os
from loguru import logger
from pydantic import BaseModel, parse_obj_as
import redis

from modules.models import Employee

from .singleton import SingletonMeta


class RedisCacher(metaclass=SingletonMeta):
    @logger.catch(reraise=True)
    async def __init__(self) -> None:
        REDIS_HOST = os.environ.get("REDIS_HOST")

        self._client = redis.Redis(host=REDIS_HOST, socket_connect_timeout=3)

    async def _is_in_cache(self, query: tp.Tuple[str, str]) -> bool:
        """Check if query is available in cache"""
        return self._client.exists(str(query))

    async def _cache_to_redis(self, query: tp.Tuple[str, str], data: BaseModel) -> None:
        """Save employee data to redis"""
        ttl = 1000 ** 2
        self._client.set(
            name=str(query),
            value=repr([entry.dict() for entry in data]),
            exat=int(time.time()) + ttl,
        )
        logger.debug(f"Cached to redis. Set to expire after {ttl // 60}m.")

    async def _unpack_from_redis(
        self, query: tp.Tuple[str, str], model: tp.Type[BaseModel]
    ) -> tp.List[tp.Type[BaseModel]]:
        """Het data to redis"""
        data = eval(self._client.get(name=str(query)))
        return [parse_obj_as(model, entry) for entry in data]

    async def cache_employees(self, employees: tp.Iterable[Employee]) -> None:
        for employee in employees:
            employee_sha = await employee.encode_sha256()
            if not await self._is_in_cache(query=("employees", employee_sha)):
                await self._cache_to_redis(query=("employees", employee_sha), data=employee)

    async def get_employee(self, hashed_employee: str) -> tp.Optional[Employee]:
        query = ("employees", hashed_employee)

        if self._is_in_cache(query=query):
            return self._unpack_from_redis(query=query)
        return None
