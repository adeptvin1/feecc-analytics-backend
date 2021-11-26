import os
import typing as tp

from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorCursor
from pydantic import BaseModel

from .models import Employee, Passport, ProductionSchema, ProductionStage, UserWithPassword
from .singleton import SingletonMeta


class MongoDbWrapper(metaclass=SingletonMeta):
    """A database wrapper implementation for MongoDB"""

    def __init__(self) -> None:
        """connect to database using credentials"""
        logger.info("Connecting to MongoDB")
        mongo_client_url: str = str(os.getenv("MONGO_CONNECTION_URL")) + "&ssl=true&tlsAllowInvalidCertificates=true"

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
        self._schemas_collection: AsyncIOMotorCollection = self._database["Production-schemas"]

        logger.info("Connected to MongoDB")

        self._decoded_employees: tp.Dict[str, tp.Optional[Employee]] = {}

    @staticmethod
    async def _remove_ids(cursor: AsyncIOMotorCursor) -> tp.List[tp.Dict[str, tp.Any]]:
        """remove all MongoDB specific IDs from the resulting documents"""
        result: tp.List[tp.Dict[str, tp.Any]] = []
        for doc in await cursor.to_list(length=100):
            del doc["_id"]
            result.append(doc)
        return result

    async def _get_all_from_collection(
        self, collection_: AsyncIOMotorCollection, model_: tp.Type[BaseModel]
    ) -> tp.List[BaseModel]:
        """retrieves all documents from the specified collection"""
        return tp.cast(
            tp.List[BaseModel],
            [model_(**_) for _ in await collection_.find({}, {"_id": 0}).to_list(length=None)],
        )

    async def _get_element_by_key(
        self, collection_: AsyncIOMotorCollection, key: str, value: str
    ) -> tp.Dict[str, tp.Any]:
        """retrieves all documents from given collection by given {key: value}"""
        result: tp.Dict[str, tp.Any] = await collection_.find_one({key: value}, {"_id": 0})
        return result

    async def _count_documents_in_collection(self, collection_: AsyncIOMotorCollection) -> int:
        """Count documents in given collection"""
        count: int = await collection_.count_documents({})
        return count

    async def _add_document_to_collection(self, collection_: AsyncIOMotorCollection, item_: BaseModel) -> None:
        """Push document to given MongoDB collection"""
        await collection_.insert_one(item_.dict())

    async def _remove_document_from_collection(self, collection_: AsyncIOMotorCollection, key: str, value: str) -> None:
        """Remove document from collection by {key:value}"""
        await collection_.find_one_and_delete({key: value})

    async def _update_document_in_collection(
        self,
        collection_: AsyncIOMotorCollection,
        key: str,
        value: str,
        new_data: BaseModel,
        exclude: tp.Optional[tp.Set[str]] = None,
    ):
        await collection_.find_one_and_update({key: value}, {"$set": new_data.dict(exclude=exclude)})

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
        """retrieves information about analytics user by username"""
        if not username:
            raise ValueError("No username provided")
        user = await self._get_element_by_key(self._credentials_collection, key="username", value=username)
        if not user:
            return None
        return UserWithPassword(**user)

    async def get_concrete_schema(self, schema_id: str) -> tp.Optional[ProductionSchema]:
        """retrieves information about production schema"""
        schema = await self._get_element_by_key(self._schemas_collection, key="schema_id", value=schema_id)
        if schema is None:
            return None
        return ProductionSchema(**schema)

    async def get_all_employees(self) -> tp.List[Employee]:
        """retrieves all employees"""
        return tp.cast(
            tp.List[Employee], await self._get_all_from_collection(self._employee_collection, model_=Employee)
        )

    async def get_all_passports(self) -> tp.List[Passport]:
        """retrieves all passports"""
        return tp.cast(tp.List[Passport], await self._get_all_from_collection(self._unit_collection, model_=Passport))

    async def get_all_stages(self) -> tp.List[ProductionStage]:
        """retrieves all production stages"""
        return tp.cast(
            tp.List[ProductionStage],
            await self._get_all_from_collection(self._prod_stage_collection, model_=ProductionStage),
        )

    async def get_all_schemas(self) -> tp.List[ProductionSchema]:
        """retrieves all production schemas"""
        return tp.cast(
            tp.List[ProductionSchema],
            await self._get_all_from_collection(self._schemas_collection, model_=ProductionSchema),
        )

    async def count_employees(self) -> int:
        """count documents in employee collection"""
        return await self._count_documents_in_collection(self._employee_collection)

    async def count_passports(self) -> int:
        """count documents in employee collection"""
        return await self._count_documents_in_collection(self._unit_collection)

    async def count_stages(self) -> int:
        """count documents in employee collection"""
        return await self._count_documents_in_collection(self._unit_collection)

    async def count_schemas(self) -> int:
        """count documents in schemas collection"""
        return await self._count_documents_in_collection(self._schemas_collection)

    async def add_employee(self, employee: Employee) -> None:
        """add employee to database"""
        await self._add_document_to_collection(self._employee_collection, employee)

    async def add_passport(self, passport: Passport) -> None:
        """add passport to database"""
        await self._add_document_to_collection(self._unit_collection, passport)

    async def add_stage(self, stage: ProductionStage) -> None:
        """add stage to database"""
        await self._add_document_to_collection(self._prod_stage_collection, stage)

    async def add_user(self, user: UserWithPassword) -> None:
        """add user to database"""
        await self._add_document_to_collection(self._credentials_collection, user)

    async def add_schema(self, schema: ProductionSchema) -> None:
        """add production schema to database"""
        await self._add_document_to_collection(self._schemas_collection, schema)

    async def remove_employee(self, rfid_card_id: str) -> None:
        """remove employee from database"""
        await self._remove_document_from_collection(self._employee_collection, key="rfid_card_id", value=rfid_card_id)

    async def remove_passport(self, internal_id: str) -> None:
        """remove passport (unit) from database"""
        await self._remove_document_from_collection(self._unit_collection, key="internal_id", value=internal_id)

    async def remove_stage(self, stage_id: str) -> None:
        """remove production stage from database"""
        await self._remove_document_from_collection(self._prod_stage_collection, key="id", value=stage_id)

    async def remove_user(self, username: str) -> None:
        """remove user by username from database"""
        await self._remove_document_from_collection(self._credentials_collection, key="username", value=username)

    async def remove_schema(self, schema_id: str) -> None:
        """remove production schema from database"""
        await self._remove_document_from_collection(self._schemas_collection, key="schema_id", value=schema_id)

    async def edit_schema(self, schema_id: str, new_schema: ProductionSchema) -> None:
        """edit single production stage schema by its schema_id"""
        await self._update_document_in_collection(
            self._schemas_collection,
            key="schema_id",
            value=schema_id,
            new_data=new_schema,
            exclude={"schema_id", "parent_schema_id", "required_components_schema_ids"},
        )
