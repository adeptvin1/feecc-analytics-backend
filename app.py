from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.database import MongoDbWrapper
from modules.routers import employees, external_ops, passports, service, stages, users

api = FastAPI()

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api.include_router(employees.router, tags=["employees"])
api.include_router(passports.router, tags=["passports"])
api.include_router(stages.router, tags=["stages"])
api.include_router(users.router, tags=["user-management"])
api.include_router(service.router, tags=["service"])
api.include_router(external_ops.router, tags=["external-operations"])
