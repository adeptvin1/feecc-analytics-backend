import datetime
import typing as tp


async def parse_passports_filter(
    name: tp.Optional[str], date: tp.Optional[datetime.datetime], overtime: tp.Optional[bool], rework: tp.Optional[bool]
) -> tp.Dict[str, tp.Union[bool, str, datetime.datetime]]:
    clear_filter: tp.Dict[str, tp.Union[bool, str, datetime.datetime]] = {}

    if name is not None:
        if name.startswith("http"):
            clear_filter["short_url"] = name
        elif len(name) == 13 and name.isnumeric():
            clear_filter["internal_id"] = name
        else:
            clear_filter["uuid"] = name

    if date is not None:
        clear_filter["date"] = str(date)

    if overtime is not None:
        clear_filter["overtime"] = overtime

    if rework is not None:
        clear_filter["rework"] = rework

    return clear_filter
