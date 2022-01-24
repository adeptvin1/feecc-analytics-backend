from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import os

from modules.routers import employees, external_ops, passports, service, stages, users, schemas

api = FastAPI()

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@api.on_event("startup")
def check_environment_variables() -> None:
    logger.info("Checking environment variables")
    failed: bool = False
    if os.environ.get("MONGO_CONNECTION_URL", None) is None:
        failed = True
        logger.error("variable $MONGO_CONNECTION_URL is not set")
    if os.environ.get("SECRET_KEY", None) is None:
        failed = True
        logger.error("variable $SECRET_KEY is not set")
    if failed:
        message = "Can't start analytics server because some envvars are missing"
        logger.critical(message)
        raise IOError(message)
    else:
        logger.info("All checks passed, running analytics server")


@api.on_event("shutdown")
def shutdown_event() -> None:
    logger.success("Shutting down feecc analytics backend server...")


api.include_router(employees.router, prefix="/api/v1/employees", tags=["Employees Management"])
api.include_router(passports.router, prefix="/api/v1/passports", tags=["Passports (Units) Management"])
api.include_router(schemas.router, prefix="/api/v1/schemas", tags=["Production Schemas Management"])
api.include_router(stages.router, prefix="/api/v1/stages", tags=["Production Stages Management"])
api.include_router(users.router, prefix="/api/v1/users", tags=["Analytics Users Management"])
api.include_router(service.router, tags=["Service Endpoints"])
api.include_router(external_ops.router, tags=["External Operations"])
