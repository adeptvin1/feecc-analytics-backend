from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.routers import employees, external_ops, passports, service, stages, users, schemas

api = FastAPI()

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api.include_router(employees.router, prefix="/api/v1/employees", tags=["Employees Management"])
api.include_router(passports.router, prefix="/api/v1/passports", tags=["Passports (Units) Management"])
api.include_router(schemas.router, prefix="/api/v1/schemas", tags=["Production Schemas Management"])
api.include_router(stages.router, prefix="/api/v1/stages", tags=["Production Stages Management"])
api.include_router(users.router, prefix="/api/v1/users", tags=["Analytics Users Management"])
api.include_router(service.router, tags=["Service Endpoints"])
api.include_router(external_ops.router, tags=["External Operations"])
