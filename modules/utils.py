import typing as tp

import yaml


async def load_yaml(data: str) -> str:
    return yaml.load(data, Loader=yaml.SafeLoader)
