import datetime
import typing as tp
from ..types import Filter


async def parse_passports_filter(
    name: tp.Optional[str] = None,
    date: tp.Optional[datetime.datetime] = None,
    overtime: tp.Optional[bool] = None,
    rework: tp.Optional[bool] = None,
    types: tp.Optional[str] = None,
    unfinished: bool = False,
) -> Filter:
    clear_filter: Filter = {}

    if name is not None:
        if "url.today" in name:
            clear_filter["passport_short_url"] = name
        elif len(name) == 32:
            clear_filter["uuid"] = name
        elif len(name) == 13 and name.isnumeric():
            clear_filter["internal_id"] = name
        else:
            clear_filter["name"] = {"$regex": name}

    if date is not None:
        start, end = date.replace(hour=0, minute=0, second=0), date.replace(hour=23, minute=59, second=59)
        clear_filter["creation_time"] = {"$lt": end, "$gte": start}

    if types is not None:
        types_array: tp.List[str] = types.split(",")
        clear_filter["types"] = {"$in": types_array}

    if overtime is not None:
        clear_filter["overtime"] = overtime

    if rework is not None:
        clear_filter["rework"] = rework

    clear_filter["passport_ipfs_cid"] = {"$ne": None} if not unfinished else None  # type: ignore

    return clear_filter
