import typing as tp
import datetime

from .models import ProtocolStatus

Filter = tp.Dict[
    str,
    tp.Union[
        bool,
        str,
        datetime.datetime,
        ProtocolStatus,
        tp.Dict[str, tp.Union[datetime.datetime, None, str, tp.Set[str], tp.List[str]]],
    ],
]
