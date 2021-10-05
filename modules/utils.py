import typing as tp


async def decode_employee(hashed_employee: str) -> str:
    pass


async def normalize_filter(filter: tp.Dict[str, str]) -> tp.Dict[str, tp.Any]:
    new_filter: tp.Dict[str, tp.Any] = {}
    for key, value in dict(filter).items():
        if value is None:
            continue
        if value is list:
            new_filter[key] = {"$in": value}
            continue
        new_filter[key] = value
    return new_filter
