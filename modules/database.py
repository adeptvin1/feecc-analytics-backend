import os
import typing as tp

from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorCursor

from .singleton import SingletonMeta


class MongoDbWrapper(metaclass=SingletonMeta):
    """A database wrapper implementation for MongoDB"""

    def __init__(self) -> None:
        """connect to database using credentials"""
        logger.info("Connecting to MongoDB")
        mongo_client_url: tp.Optional[str] = os.getenv("MONGO_CONNECTION_URL") + "&ssl=true&ssl_cert_reqs=CERT_NONE"

        if mongo_client_url is None:
            message = "Cannot establish database connection: $MONGO_CONNECTION_URL environment variable is not set."
            logger.critical(message)
            raise IOError(message)

        mongo_client: AsyncIOMotorClient = AsyncIOMotorClient(mongo_client_url)

        self._database = mongo_client["Feecc-Hub"]

        self._employee_collection: AsyncIOMotorCollection = self._database["Employee-data"]
        self._unit_collection: AsyncIOMotorCollection = self._database["Unit-data"]
        self._prod_stage_collection: AsyncIOMotorCollection = self._database["Production-stages-data"]

        logger.info("Connected to MongoDB")

    @staticmethod
    async def _remove_ids(cursor: AsyncIOMotorCursor) -> tp.List[tp.Dict[str, tp.Any]]:
        """remove all MongoDB specific IDs from the resulting documents"""
        result: tp.List[tp.List[tp.Dict[str, tp.Any]]] = []
        for doc in await cursor.to_list(length=100):
            del doc["_id"]
            result.append(doc)
        return result

    async def _execute_all_from_collection(self, collection_: AsyncIOMotorCollection) -> tp.List[tp.Dict[str, tp.Any]]:
        cursor = collection_.find()
        return await self._remove_ids(cursor)

    async def _get_element_by_key(
        self, collection_: AsyncIOMotorCollection, key: str, value: str
    ) -> tp.Dict[str, tp.Any]:
        return await collection_.find_one({key: value}, {"_id": 0})

    async def get_concrete_employee(self, card_id: str) -> tp.Dict[str, tp.Any]:
        return await self._get_element_by_key(self._employee_collection, key="rfid_card_id", value=card_id)

    async def get_all_employees(self):
        return await self._execute_all_from_collection(self._employee_collection)

    async def get_all_passports(self):
        return await self._execute_all_from_collection(self._unit_collection)

    async def get_concrete_passport(self, internal_id: str):
        return await self._get_element_by_key(self._unit_collection, key="internal_id", value=internal_id)

    async def get_all_stages(self):
        return await self._execute_all_from_collection(self._prod_stage_collection)

    async def get_concrete_stage(self, stage_id: str):
        return await self._get_element_by_key(self._prod_stage_collection, key="id", value=stage_id)
