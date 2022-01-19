import datetime
import typing as tp


def parse_passports_filter(
    name: tp.Optional[str], date: tp.Optional[datetime.datetime], overtime: tp.Optional[bool], rework: tp.Optional[bool]
) -> tp.Dict[str, str]:
    clear_filter = {}

    if name.startswith("http"):
        clear_filter["short_url"] = name
    elif len(name) == 13 and name.isnumeric():
        clear_filter["internal_id"] = name
    else:
        clear_filter["uuid"] = name

    if date:
        clear_filter["date"] = str(date)

    if overtime:
        clear_filter["overtime"] = overtime

    if rework:
        clear_filter["rework"] = rework

    return clear_filter
