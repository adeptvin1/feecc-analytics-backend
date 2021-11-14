import typing as tp

from fastapi import APIRouter, Depends


from ..exceptions import DatabaseException
from ..security import check_user_permissions, get_current_user
from ..database import MongoDbWrapper
from ..models import ProductionSchema, ProductionSchemaOut, ProductionSchemasOut, GenericResponse, ProductionStage


router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/", response_model=tp.Union[ProductionSchemasOut, GenericResponse])  # type:ignore
async def get_all_production_schemas(page: int = 1, items: int = 20) -> ProductionSchemasOut:
    """Endpoint to get all production schemas"""
    try:
        schemas_count = await MongoDbWrapper().count_schemas()
        schemas = await MongoDbWrapper().get_all_schemas()
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return ProductionSchemasOut(count=schemas_count, data=schemas[(page - 1) * items : page * items])


@router.get("/{schema_id}", response_model=tp.Union[ProductionSchemaOut, GenericResponse])  # type:ignore
async def get_concrete_production_schema(schema_id: str) -> ProductionSchemaOut:
    try:
        schema = await MongoDbWrapper().get_concrete_schema(schema_id)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return ProductionSchemaOut(schema=schema)


@router.post("/", response_model=GenericResponse, dependencies=[Depends(check_user_permissions)])
async def create_new_production_schema(schema: ProductionSchema) -> GenericResponse:
    try:
        await MongoDbWrapper().add_schema(schema)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail=f"Created new schema with id {schema.schema_id}")


@router.delete("/{schema_id}", response_model=GenericResponse, dependencies=[Depends(check_user_permissions)])
async def delete_production_schema(schema_id: str) -> GenericResponse:
    try:
        await MongoDbWrapper().remove_schema(schema_id)
    except Exception as exception_message:
        raise DatabaseException(error=exception_message)
    return GenericResponse(detail="Deleted schema")
