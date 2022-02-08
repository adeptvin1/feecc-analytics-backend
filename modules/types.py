import typing as tp
import datetime

Filter = tp.Dict[str, tp.Union[bool, str, datetime.datetime, tp.Dict[str, tp.Union[tp.Set[str], tp.List[str]]]]]
