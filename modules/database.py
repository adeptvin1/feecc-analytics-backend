import os
import typing as tp

from functools import lru_cache
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorCursor
from pydantic import BaseModel

from .models import BaseFilter, Employee, Passport, ProductionStage, User, UserWithPassword
from .singleton import SingletonMeta

DBModel = tp.Union[Employee, Passport, ProductionStage, User]


class MongoDbWrapper(metaclass=SingletonMeta):
    """A database wrapper implementation for MongoDB"""

    def __init__(self) -> None:
        """connect to database using credentials"""
        logger.info("Connecting to MongoDB")
        mongo_client_url: str = str(os.getenv("MONGO_CONNECTION_URL")) + "&ssl=true&ssl_cert_reqs=CERT_NONE"

        print(mongo_client_url)

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

        self._decoded_employees: tp.Dict[str, Employee] = {}

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

    @staticmethod
    async def normalize_model(data: tp.Type[BaseModel]) -> tp.Dict[tp.Any, tp.Any]:
        data_ = {}
        for key, value in dict(data).items():
            if value is None:
                continue
            data_[key] = value
        return data_

    async def _get_all_from_collection(
        self, collection_: AsyncIOMotorCollection, model_: tp.Type[BaseModel], filter_: tp.Optional[BaseFilter] = None
    ) -> tp.List[BaseModel]:
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
        self, collection_: AsyncIOMotorCollection, filter_: tp.Optional[tp.Dict[str, tp.Any]]
    ) -> int:
        normalized_filter = await self.normalize_filter(filter_)
        count: int = await collection_.count_documents(normalized_filter)
        return count

    async def _add_document_to_collection(self, collection_: AsyncIOMotorCollection, item_: tp.Type[BaseModel]) -> None:
        await collection_.insert_one(dict(item_))

    async def _remove_document_from_collection(self, collection_: AsyncIOMotorCollection, key: str, value: str) -> None:
        await collection_.find_one_and_delete({key: value})

    async def decode_employee(self, hashed_employee: str) -> tp.Optional[Employee]:
        """Find an employee by hashed data"""
        employee = self._decoded_employees.get(hashed_employee, None)
        if employee is not None:
            return employee
        employees = await self.get_all_employees()
        for employee in employees:
            encoded_employee = await employee.encode_sha256()
            if encoded_employee == hashed_employee:
                self._decoded_employees[hashed_employee] = employee
                return employee
        return None

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

    async def get_concrete_user(self, username: tp.Optional[str]) -> tp.Optional[UserWithPassword]:
        """retrieves information about analytics user"""
        if not username:
            raise ValueError("No username provided")
        user = await self._get_element_by_key(self._credentials_collection, key="username", value=username)
        if not user:
            return None
        return UserWithPassword(**user)

    async def get_all_employees(self) -> tp.List[Employee]:
        """retrieves all employees"""
        return await self._get_all_from_collection(self._employee_collection, model_=Employee)

    async def get_all_passports(self) -> tp.List[Passport]:
        """retrieves all passports"""
        return await self._get_all_from_collection(self._unit_collection, model_=Passport)

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

    async def add_employee(self, employee: Employee) -> None:
        """add employee to database"""
        await self._add_document_to_collection(self._employee_collection, employee)

    async def add_passport(self, passport: Passport) -> None:
        await self._add_document_to_collection(self._unit_collection, passport)

    async def add_stage(self, stage: ProductionStage) -> None:
        await self._add_document_to_collection(self._prod_stage_collection, stage)

    async def add_user(self, user: UserWithPassword) -> None:
        await self._add_document_to_collection(self._credentials_collection, user)

    async def remove_employee(self, rfid_card_id: str) -> None:
        await self._remove_document_from_collection(self._employee_collection, key="rfid_card_id", value=rfid_card_id)

    async def remove_passport(self, internal_id: str) -> None:
        await self._remove_document_from_collection(self._unit_collection, key="internal_id", value=internal_id)

    async def remove_stage(self, stage_id: str) -> None:
        await self._remove_document_from_collection(self._prod_stage_collection, key="stage_id", value=stage_id)
