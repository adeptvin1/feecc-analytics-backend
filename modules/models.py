from __future__ import annotations

import typing as tp

from pydantic import BaseModel


class User(BaseModel):
    username: str
    rule_set: tp.List[str] = ["read"]
    associated_employee: tp.Optional[str]
