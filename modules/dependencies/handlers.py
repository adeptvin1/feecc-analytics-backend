import typing as tp

from fastapi import Depends
from ..models import Protocol, ProtocolData, User
from .security import get_current_user
from ..exceptions import DatabaseException, ForbiddenActionException
from ..database import MongoDbWrapper


async def handle_protocol(internal_id: str, protocol: Protocol, user: User = Depends(get_current_user)) -> ProtocolData:
    if "approve" not in user.rule_set:
        raise ForbiddenActionException(
            details=f"You don't have access to process protocols. Your ruleset: {user.rule_set}"
        )
    passport = await MongoDbWrapper().get_concrete_passport(internal_id=internal_id)
    if not passport:
        raise DatabaseException(details=f"Unit with id {internal_id} not found. Can't create protocol")
    return ProtocolData(**protocol.dict(), associated_unit_id=internal_id)
