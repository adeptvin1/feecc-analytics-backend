import typing as tp

import yaml


async def load_yaml(data: str) -> tp.Any:
    return yaml.load(data, Loader=yaml.SafeLoader)
