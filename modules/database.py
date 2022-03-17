import datetime
import os
import typing as tp

from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorCursor
from pydantic import BaseModel

from modules.cacher import RedisCacher

from .models import (
    Employee,
    Passport,
    ProductionSchema,
    ProductionStage,
    ProductionStageData,
    Protocol,
    ProtocolData,
    UserWithPassword,
)
from .singleton import SingletonMeta
from .types import Filter


class MongoDbWrapper(metaclass=SingletonMeta):
    """A database wrapper implementation for MongoDB"""

    def __init__(self) -> None:
        """connect to database using credentials"""
        logger.info("Connecting to MongoDB")
        mongo_client_url: tp.Optional[str] = os.getenv("MONGO_CONNECTION_URL")

        if mongo_client_url is None:
            message = "Cannot establish database connection: $MONGO_CONNECTION_URL environment variable is not set."
            logger.critical(message)
            raise IOError(message)

        mongo_client_url = str(mongo_client_url) + "&ssl=true&tlsAllowInvalidCertificates=true"
        mongo_client: AsyncIOMotorClient = AsyncIOMotorClient(mongo_client_url)

        logger.debug(f"Connected to MongoDB at {mongo_client_url}")

        self._database = mongo_client[os.environ.get("MONGO_DATABASE_NAME")]

        self._employee_collection: AsyncIOMotorCollection = self._database["Employee-data"]
        self._unit_collection: AsyncIOMotorCollection = self._database["Unit-data"]
        self._prod_stage_collection: AsyncIOMotorCollection = self._database["Production-stages-data"]
        self._credentials_collection: AsyncIOMotorCollection = self._database["Analytics-credentials"]
        self._schemas_collection: AsyncIOMotorCollection = self._database["Production-schemas"]
        self._schemas_types_collection: AsyncIOMotorClient = self._database["Production-schemas-types"]
        self._protocols_collection: AsyncIOMotorClient = self._database["Protocols"]
        self._protocols_data_collection: AsyncIOMotorClient = self._database["Protocols-data"]

        logger.info("Connected to MongoDB")

        self._cacher: RedisCacher = RedisCacher()

    @staticmethod
    async def _remove_ids(cursor: AsyncIOMotorCursor) -> tp.List[tp.Dict[str, tp.Any]]:
        """remove all MongoDB specific IDs from the resulting documents"""
        result: tp.List[tp.Dict[str, tp.Any]] = []
        for doc in await cursor.to_list(length=100):
            del doc["_id"]
            result.append(doc)
        return result

    @staticmethod
    async def _get_all_from_collection(
        collection_: AsyncIOMotorCollection,
        model_: tp.Type[BaseModel],
        filter: Filter = {},
        include_only: tp.Optional[str] = None,
    ) -> tp.List[tp.Any]:
        """retrieves all documents from the specified collection"""
        logger.debug(f"Filter: {filter}")
        if include_only:
            return [
                _[include_only]
                for _ in await collection_.find(filter, {"_id": 0, include_only: 1}).to_list(length=None)
            ]
        return tp.cast(
            tp.List[BaseModel],
            [model_(**_) for _ in await collection_.find(filter, {"_id": 0}).to_list(length=None)],
        )

    @staticmethod
    async def _get_element_by_key(collection_: AsyncIOMotorCollection, key: str, value: str) -> tp.Dict[str, tp.Any]:
        """retrieves all documents from given collection by given {key: value}"""
        result: tp.Dict[str, tp.Any] = await collection_.find_one({key: value}, {"_id": 0})
        return result

    @staticmethod
    async def _count_documents_in_collection(collection_: AsyncIOMotorCollection, filter: Filter = {}) -> int:
        """Count documents in given collection"""
        count: int = await collection_.count_documents(filter)
        return count

    @staticmethod
    async def _add_document_to_collection(collection_: AsyncIOMotorCollection, item_: BaseModel) -> None:
        """Push document to given MongoDB collection"""
        await collection_.insert_one(item_.dict())

    @staticmethod
    async def _remove_document_from_collection(collection_: AsyncIOMotorCollection, key: str, value: str) -> None:
        """Remove document from collection by {key:value}"""
        await collection_.find_one_and_delete({key: value})

    @staticmethod
    async def _update_document_in_collection(
        collection_: AsyncIOMotorCollection,
        key: str,
        value: str,
        new_data: BaseModel,
        exclude: tp.Optional[tp.Set[str]] = None,
    ) -> None:
        logger.warning("Using deprecated method _update_document_in_collection() use _update_document() instead")
        if exclude:
            await collection_.find_one_and_update({key: value}, {"$set": new_data.dict(exclude=exclude)})
        else:
            await collection_.find_one_and_update({key: value}, {"$set": new_data.dict()})

    @staticmethod
    async def _update_document(
        collection: AsyncIOMotorCollection, filter: tp.Dict[str, str], new_data: tp.Dict[str, str]
    ) -> None:
        if not filter or not new_data:
            raise ValueError(f"Expected filter and new_data, got {filter}:{new_data}")
        await collection.find_one_and_update(filter, {"$set": new_data})

    async def decode_employee(self, hashed_employee: str) -> tp.Optional[Employee]:
        """Find an employee by hashed data"""
        employee = self._cacher.get_employee(hashed_employee)
        if employee is not None:
            return employee

        employees = await self.get_all_employees()
        self._cacher.cache_employees(employees)
        
        employee = self._cacher.get_employee(hashed_employee)
        if employee is not None:
            return employee

        return None

    async def get_internal_id_by_uuid(self, uuid: str) -> str:
        """Get internal id by given uuid"""
        passport = await self.get_concrete_passport(uuid=uuid)
        if passport is None:
            raise ValueError(f"Can't find passport with uuid {uuid}")
        logger.debug(f"{passport.internal_id} internal_id for passport with uuid {uuid}")
        return passport.internal_id

    async def get_components_internal_id(self, uuids: tp.Optional[tp.List[str]]) -> tp.List[str]:
        if not uuids:
            return []
        int_ids: tp.List[str] = []
        for uuid in uuids:
            passport = await self.get_concrete_passport(uuid=uuid)
            if passport is None:
                continue
            int_ids.append(passport.internal_id)
        return int_ids

    async def get_concrete_employee(self, card_id: str) -> tp.Optional[Employee]:
        """retrieves an employee by card_id"""
        employee = await self._get_element_by_key(self._employee_collection, key="rfid_card_id", value=card_id)
        if not employee:
            return None
        return Employee(**employee)

    async def get_concrete_passport(
        self, internal_id: tp.Optional[str] = None, uuid: tp.Optional[str] = None
    ) -> tp.Optional[Passport]:
        """retrieves unit by its internal id or uuid"""
        if internal_id and uuid:
            raise ValueError("Unit search only available by uuid or internal_id")
        if internal_id:
            passport = await self._get_element_by_key(self._unit_collection, key="internal_id", value=internal_id)
        if uuid:
            passport = await self._get_element_by_key(self._unit_collection, key="uuid", value=uuid)
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

    async def get_concrete_schema(self, schema_id: str) -> ProductionSchema:
        """retrieves information about production schema"""
        schema = await self._get_element_by_key(self._schemas_collection, key="schema_id", value=schema_id)
        return ProductionSchema(**schema)

    async def get_concrete_protocol_prototype(self, associated_with_schema_id: str) -> tp.Optional[Protocol]:
        """retrieves information about protocol prototype"""
        protocol = await self._get_element_by_key(
            self._protocols_collection, key="associated_with_schema_id", value=associated_with_schema_id
        )
        if not protocol:
            return None
        return Protocol(**protocol)

    async def get_concrete_protocol(self, internal_id: str) -> tp.Optional[ProtocolData]:
        """retrieves information about protocol by int_id"""
        protocol = await self._get_element_by_key(
            self._protocols_data_collection, key="associated_unit_id", value=internal_id
        )
        if not protocol:
            return None
        return ProtocolData(**protocol)

    async def get_passport_creation_date(self, uuid: str) -> tp.Optional[datetime.datetime]:
        try:
            return (
                await self._get_element_by_key(self._prod_stage_collection, key="parent_unit_uuid", value=uuid)
            ).get("creation_time", None)
        except Exception:
            return None

    async def get_passport_type(self, schema_id: str) -> tp.Optional[str]:
        logger.debug("Using deprecated method get_passport_type, now Unit have field type. Use it instead.")
        try:
            return (
                await self._get_element_by_key(self._schemas_types_collection, key="schema_id", value=schema_id)
            ).get("schema_type", None)
        except Exception:
            return None

    async def get_passport_serial_number(self, internal_id: str) -> tp.Optional[str]:
        passport = await self.get_concrete_passport(internal_id=internal_id)
        if not passport:
            return None
        return passport.serial_number

    async def get_passport_name(self, internal_id: str) -> tp.Optional[str]:
        passport = await self.get_concrete_passport(internal_id=internal_id)
        if not passport:
            return None
        if not passport.schema_id:
            return None
        return (await self.get_concrete_schema(schema_id=passport.schema_id)).unit_name

    async def get_passport_status(self, internal_id: str) -> tp.Optional[str]:
        """retrieves concrete passport status"""
        passport = await MongoDbWrapper().get_concrete_passport(internal_id=internal_id)
        if passport is None:
            return None
        if passport.status is None:
            return None
        return passport.status

    async def get_all_types(self) -> tp.Set[str]:
        """retrieves all types"""
        schemas: tp.List[ProductionSchema] = await self._get_all_from_collection(
            self._schemas_collection, model_=ProductionSchema
        )
        types = set(schema.schema_type for schema in schemas)
        # XXX: Field for testing purposes
        types.remove("Testing")
        return types

    async def get_all_protocol_prototypes(self) -> tp.List[Protocol]:
        """retrieves all protocol prototypes"""
        return await self._get_all_from_collection(self._protocols_collection, model_=Protocol)

    async def get_all_protocols(self, filter: Filter = {}) -> tp.List[Protocol]:
        """retrieves all protocols"""
        return await self._get_all_from_collection(self._protocols_data_collection, model_=ProtocolData, filter=filter)

    async def get_all_employees(self) -> tp.List[Employee]:
        """retrieves all employees"""
        return tp.cast(
            tp.List[Employee], await self._get_all_from_collection(self._employee_collection, model_=Employee)
        )

    async def get_passports(self, filter: Filter = {}) -> tp.List[Passport]:
        """retrieves all units"""
        if "types" in filter:
            matching_schemas_uuids = await self._get_all_from_collection(
                self._schemas_types_collection,
                model_=BaseModel,
                filter={"schema_type": filter["types"]},
                include_only="schema_id",
            )
            del filter["types"]
            filter["schema_id"] = {"$in": matching_schemas_uuids}

        if "name" in filter:
            matching_schemas_uuids = await self._get_all_from_collection(
                self._schemas_collection,
                model_=BaseModel,
                filter={"unit_name": filter["name"]},
                include_only="schema_id",
            )
            del filter["name"]
            if "schema_id" in filter:
                filter["schema_id"]["$in"] = list(set(filter["schema_id"]["$in"]).intersection(set(matching_schemas_uuids)))  # type: ignore
            else:
                filter["schema_id"] = {"$in": matching_schemas_uuids}

        return tp.cast(
            tp.List[Passport],
            await self._get_all_from_collection(self._unit_collection, model_=Passport, filter=filter),
        )

    async def get_stages(
        self, internal_id: tp.Optional[str] = None, uuid: tp.Optional[str] = None, is_subcomponent: bool = False
    ) -> tp.List[ProductionStageData]:
        """retrieves all production stages"""
        stages: tp.List[ProductionStageData]

        if internal_id and uuid:
            raise ValueError("Stages search only available by uuid or internal_id")
        if uuid:
            stages = await self._get_all_from_collection(
                self._prod_stage_collection, model_=ProductionStageData, filter={"parent_unit_uuid": uuid}
            )
            for stage in stages:
                if not stage.parent_unit_uuid:
                    continue
                if is_subcomponent:
                    stage.parent_unit_internal_id = await self.get_internal_id_by_uuid(uuid=stage.parent_unit_uuid)
                    stage.unit_name = await self.get_passport_name(
                        await self.get_internal_id_by_uuid(uuid=stage.parent_unit_uuid)
                    )

            return stages
        if internal_id:
            passport = await self.get_concrete_passport(internal_id=internal_id)
            if not passport:
                return []
            stages = await self._get_all_from_collection(
                self._prod_stage_collection, model_=ProductionStageData, filter={"parent_unit_uuid": passport.uuid}
            )
            for stage in stages:
                if not stage.parent_unit_uuid:
                    continue
                if is_subcomponent:
                    stage.parent_unit_internal_id = await self.get_internal_id_by_uuid(uuid=stage.parent_unit_uuid)
                    stage.unit_name = await self.get_passport_name(
                        await self.get_internal_id_by_uuid(uuid=stage.parent_unit_uuid)
                    )

            return stages

        return []

    async def get_all_schemas(self) -> tp.List[ProductionSchema]:
        """retrieves all production schemas"""
        return tp.cast(
            tp.List[ProductionSchema],
            await self._get_all_from_collection(self._schemas_collection, model_=ProductionSchema),
        )

    async def count_employees(self) -> int:
        """count documents in employee collection"""
        return await self._count_documents_in_collection(self._employee_collection)

    async def count_passports(self, filter: Filter = {}) -> int:
        """count documents in unit collection"""
        return await self._count_documents_in_collection(self._unit_collection, filter=filter)

    async def count_stages(self) -> int:
        """count documents in stages collection"""
        return await self._count_documents_in_collection(self._unit_collection)

    async def count_schemas(self) -> int:
        """count documents in schemas collection"""
        return await self._count_documents_in_collection(self._schemas_collection)

    async def add_employee(self, employee: Employee) -> None:
        """add employee to database"""
        await self._add_document_to_collection(self._employee_collection, employee)

    async def add_passport(self, passport: Passport) -> None:
        """add unit to database"""
        await self._add_document_to_collection(self._unit_collection, passport)

    async def add_stage(self, stage: ProductionStage) -> None:
        """add stage to database"""
        logger.debug(
            f'Added stage {stage.dict(exclude={"completed", "number", "unit_name", "parent_unit_internal_id", "video_hashes", "additional_info"})}'
        )
        await self._add_document_to_collection(self._prod_stage_collection, stage)

    async def add_user(self, user: UserWithPassword) -> None:
        """add user to database"""
        await self._add_document_to_collection(self._credentials_collection, user)

    async def add_schema(self, schema: ProductionSchema) -> None:
        """add production schema to database"""
        await self._add_document_to_collection(self._schemas_collection, schema)

    async def add_protocol(self, protocol: ProtocolData) -> None:
        """add protocol to database"""
        await self._add_document_to_collection(self._protocols_data_collection, protocol)

    async def remove_employee(self, rfid_card_id: str) -> None:
        """remove employee from database"""
        await self._remove_document_from_collection(self._employee_collection, key="rfid_card_id", value=rfid_card_id)

    async def remove_passport(self, internal_id: str) -> None:
        """remove unit from database"""
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

    async def edit_schema(self, schema_id: str, new_schema_data: ProductionSchema) -> None:
        """edit single production stage schema by its schema_id"""
        await self._update_document_in_collection(
            self._schemas_collection,
            key="schema_id",
            value=schema_id,
            new_data=new_schema_data,
            exclude={"schema_id", "parent_schema_id", "required_components_schema_ids"},
        )

    async def edit_user(self, username: str, new_user_data: UserWithPassword) -> None:
        """edit concrete user's data"""
        await self._update_document_in_collection(
            self._credentials_collection, key="username", value=username, new_data=new_user_data, exclude={"is_admin"}
        )

    async def edit_passport(self, internal_id: str, new_passport_data: Passport) -> None:
        """edit concrete unit's data"""
        await self._update_document_in_collection(
            self._unit_collection,
            key="internal_id",
            value=internal_id,
            new_data=new_passport_data,
            exclude={"uuid", "internal_id", "is_in_db", "featured_in_int_id"},
        )

    async def edit_employee(self, rfid_card_id: str, new_employee_data: Employee) -> None:
        """edit concrete employee's data"""
        await self._update_document_in_collection(
            self._employee_collection, key="rfid_card_id", value=rfid_card_id, new_data=new_employee_data, exclude=None
        )

    async def edit_stage(self, stage_id: str, new_stage_data: ProductionStage) -> None:
        """edit concrete production stage data"""
        await self._update_document_in_collection(
            self._prod_stage_collection,
            key="id",
            value=stage_id,
            new_data=new_stage_data,
            exclude={
                "parent_unit_uuid",
                "session_start_time",
                "session_end_time",
                "id",
                "is_in_db",
                "creation_time",
            },
        )

    async def update_serial_number(self, internal_id: str, serial_number: str) -> None:
        """update concrete passport serial_number by internal_id"""
        await self._update_document(
            self._unit_collection, filter={"internal_id": internal_id}, new_data={"serial_number": serial_number}
        )

    async def update_passport_status(self, internal_id: str, status: str) -> None:
        """update concrete passport status"""
        current_status = await self.get_passport_status(internal_id=internal_id)
        logger.warning(f"Trying to change status from {current_status} to {status}")
        if status == current_status:
            return None
        await self._update_document(self._unit_collection, {"internal_id": internal_id}, {"status": status})

    async def update_protocol(self, protocol_data: ProtocolData) -> None:
        logger.debug(
            f"Updating protocol {protocol_data.protocol_id} for unit {protocol_data.associated_unit_id}. Data: {protocol_data.dict()}"
        )
        await self._update_document(
            self._protocols_data_collection,
            filter={"associated_unit_id": protocol_data.associated_unit_id},
            new_data=protocol_data.dict(),
        )

    async def send_unit_for_revision(self, internal_id: str, stage_ids: tp.List[str]) -> None:
        passport = await self.get_concrete_passport(internal_id=internal_id)
        if not passport:
            raise ValueError(f"Can't send unit for revision. Passport {internal_id} not found")

        current_status = passport.status
        if current_status != "built":
            raise ValueError(f"Can't send unit for revision. Current status {current_status}")
        if not len(stage_ids):
            raise ValueError(f"Can't send unit for revision. No stage_ids provided")

        for stage_id in stage_ids:
            stage = await self.get_concrete_stage(stage_id=stage_id)

            if not stage:
                raise ValueError(f"Can't send unit for revision. Stage with id {stage_id} not found")

            if stage.parent_unit_uuid != passport.uuid:
                raise ValueError(
                    f"Can't send unit for revision. Stage {stage.id} not associated with passport {internal_id}"
                )

            stages = await self.get_stages(internal_id=internal_id)
            if not stages:
                raise ValueError(f"Can't send unit for revision. Passport {internal_id} have 0 stages")

            await self.add_stage(await stage.clear(number=len(stages)))

    async def approve_protocol(self, internal_id: str, data: ProtocolData) -> None:
        protocol = await self.get_concrete_protocol(internal_id=internal_id)

        if not protocol:
            await self.add_protocol(data)
            return

        if protocol.status == "Протокол утверждён":
            logger.warning(f"Protocol was already finalized. Unit {internal_id}, protocol {data.protocol_id}")

        protocol.rows = data.rows
        protocol.status = await protocol.status.switch()

        await self.update_protocol(protocol)

        if protocol.status == "Вторая стадия испытаний пройдена":
            await self.update_passport_status(internal_id=internal_id, status="approved")
