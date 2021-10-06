import os
import typing as tp

from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorCursor

from modules.models import BaseFilter, Employee, Passport, ProductionStage, User

from .singleton import SingletonMeta

DBModel = tp.Union[Employee, Passport, ProductionStage, User]


class MongoDbWrapper(metaclass=SingletonMeta):
    """A database wrapper implementation for MongoDB"""

    def __init__(self) -> None:
        """connect to database using credentials"""
        logger.info("Connecting to MongoDB")
        mongo_client_url: str = str(os.getenv("MONGO_CONNECTION_URL")) + "&ssl=true&ssl_cert_reqs=CERT_NONE"

        if mongo_client_url is None:
            message = "Cannot establish database connection: $MONGO_CONNECTION_URL environment variable is not set."
            logger.critical(message)
            raise IOError(message)

        mongo_client: AsyncIOMotorClient = AsyncIOMotorClient(mongo_client_url)

        self._database = mongo_client["Feecc-Hub"]

        self._employee_collection: AsyncIOMotorCollection = self._database["Employee-data"]
        self._unit_collection: AsyncIOMotorCollection = self._database["Unit-data"]
        self._prod_stage_collection: AsyncIOMotorCollection = self._database["Production-stages-data"]
        self._credentials_collection: AsyncIOMotorCollection = self._database["Analytics-credentials"]

        logger.info("Connected to MongoDB")

    @staticmethod
    async def _remove_ids(cursor: AsyncIOMotorCursor) -> tp.List[tp.Dict[str, tp.Any]]:
        """remove all MongoDB specific IDs from the resulting documents"""
        result: tp.List[tp.Dict[str, tp.Any]] = []
        for doc in await cursor.to_list(length=100):
            del doc["_id"]
            result.append(doc)
        return result

    @staticmethod
    async def normalize_filter(filter: tp.Optional[BaseFilter]) -> tp.Dict[str, tp.Any]:
        if not filter:
            return {}
        new_filter: tp.Dict[str, tp.Any] = {}
        for key, value in dict(filter).items():
            if value is None:
                continue
            if isinstance(value, list):
                new_filter[key] = {"$in": value}
                continue
            new_filter[key] = value
        return new_filter

    async def _get_all_from_collection(
        self, collection_: AsyncIOMotorCollection, model_: DBModel, filter_: tp.Optional[BaseFilter] = None
    ) -> tp.List[DBModel]:
        """retrieves all documents from the specified collection"""
        normalized_filter = await self.normalize_filter(filter_)
        return [model_(**_) for _ in await collection_.find(normalized_filter, {"_id": 0}).to_list(length=None)]

    async def _get_element_by_key(
        self, collection_: AsyncIOMotorCollection, key: str, value: str
    ) -> tp.Dict[str, tp.Any]:
        """retrieves all documents from given collection by given {key: value}"""
        result: tp.Dict[str, tp.Any] = await collection_.find_one({key: value}, {"_id": 0})
        return result

    async def _count_documents_in_collection(
        self, collection_: AsyncIOMotorCollection, filter_: tp.Optional[BaseFilter]
    ) -> int:
        normalized_filter = await self.normalize_filter(filter_)
        return await collection_.count_documents(normalized_filter)

    async def get_concrete_employee(self, card_id: str) -> tp.Optional[Employee]:
        """retrieves an employee by card_id"""
        employee = await self._get_element_by_key(self._employee_collection, key="rfid_card_id", value=card_id)
        if not employee:
            return None
        return Employee(**employee)

    async def get_concrete_passport(self, internal_id: str) -> tp.Optional[Passport]:
        """retrieves passport by its internal id"""
        passport = await self._get_element_by_key(self._unit_collection, key="internal_id", value=internal_id)
        if not passport:
            return None
        return Passport(**passport)

    async def get_concrete_stage(self, stage_id: str) -> tp.Optional[ProductionStage]:
        """retrieves production stage by its id"""
        production_stage = await self._get_element_by_key(self._prod_stage_collection, key="id", value=stage_id)
        if not production_stage:
            return None
        return ProductionStage(**production_stage)

    async def get_concrete_user(self, username: tp.Optional[str]) -> tp.Optional[User]:
        """retrieves information about analytics user"""
        if not username:
            raise ValueError("No username provided")
        user = await self._get_element_by_key(self._credentials_collection, key="username", value=username)
        if not user:
            return None
        return User(**user)

    async def get_all_employees(self) -> tp.List[Employee]:
        """retrieves all employees"""
        return await self._get_all_from_collection(self._employee_collection, model_=Employee)

    async def get_all_passports(self, filter_: tp.Optional[BaseFilter] = None) -> tp.List[Passport]:
        """retrieves all passports"""
        return await self._get_all_from_collection(self._unit_collection, model_=Passport, filter_=filter_)

    async def get_all_stages(self) -> tp.List[ProductionStage]:
        """retrieves all production stages"""
        return await self._get_all_from_collection(self._prod_stage_collection, model_=ProductionStage)

    async def count_employees(self, filter_: tp.Optional[BaseFilter] = None) -> int:
        """count documents in employee collection"""
        return await self._count_documents_in_collection(
            self._employee_collection, await self.normalize_filter(filter_)
        )

    async def count_passports(self, filter_: tp.Optional[BaseFilter] = None) -> int:
        """count documents in employee collection"""
        return await self._count_documents_in_collection(self._unit_collection, await self.normalize_filter(filter_))

    async def count_stages(self, filter_: tp.Optional[BaseFilter] = None) -> int:
        """count documents in employee collection"""
        return await self._count_documents_in_collection(self._unit_collection, await self.normalize_filter(filter_))
