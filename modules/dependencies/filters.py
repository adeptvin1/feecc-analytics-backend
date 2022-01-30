import datetime
import typing as tp


async def parse_passports_filter(
    name: tp.Optional[str] = None,
    date: tp.Optional[datetime.datetime] = None,
    overtime: tp.Optional[bool] = None,
    rework: tp.Optional[bool] = None,
) -> tp.Dict[str, tp.Union[bool, str, datetime.datetime, tp.Dict[str, str]]]:
    clear_filter: tp.Dict[str, tp.Union[bool, str, datetime.datetime, tp.Dict[str, str]]] = {}

    if name is not None:
        if name.startswith("url"):
            clear_filter["passport_short_url"] = name
        elif len(name) == 13 and name.isnumeric():
            clear_filter["internal_id"] = name
        else:
            clear_filter["model"] = {"$regex": name}

    if date is not None:
        clear_filter["date"] = str(date)

    if overtime is not None:
        clear_filter["overtime"] = overtime

    if rework is not None:
        clear_filter["rework"] = rework

    return clear_filter
