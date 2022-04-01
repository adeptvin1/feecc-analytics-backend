import typing as tp
from uuid import uuid4

from pydantic import BaseModel, Field


class GenericResponse(BaseModel):
    status: int = 200
    detail: str = "Success"


class ProductionSchemaStage(BaseModel):
    name: str
    type: tp.Optional[str] = None
    description: tp.Optional[str] = None
    equipment: tp.Optional[tp.List[str]] = None
    workplace: tp.Optional[str] = None
    duration_seconds: tp.Optional[int] = None
    stage_id: str


class ProductionSchema(BaseModel):
    schema_id: str = Field(default_factory=lambda: uuid4().hex)
    unit_name: str
    production_stages: tp.Optional[tp.List[ProductionSchemaStage]] = None
    required_components_schema_ids: tp.Optional[tp.List[str]] = None
    parent_schema_id: tp.Optional[str] = None
    schema_type: str


class ProductionSchemasOut(GenericResponse):
    count: int
    data: tp.List[ProductionSchema]


class ProductionSchemaOut(GenericResponse):
    schema_: tp.Annotated[tp.Optional[ProductionSchema], Field(alias="schema")]
