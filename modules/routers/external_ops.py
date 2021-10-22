import typing as tp

import httpx
from fastapi import APIRouter
from yaml import YAMLError

from ..exceptions import ConnectionTimeoutException, IncorrectAddressException, ParserException, UnhandledException
from ..models import IPFSData
from ..utils import load_yaml

router = APIRouter()


@router.get("/api/v1/ipfs_decode")
async def parse_ipfs_link(link: str) -> IPFSData:
    """ Extracts saved passport from IPFS/Pinata """
    if not link.startswith(("http://", "https://")):
        raise IncorrectAddressException

    try:
        async with httpx.AsyncClient() as client:
            request = await client.get(link)
            return await load_yaml(request.text)
    except httpx.ReadTimeout:
        raise ConnectionTimeoutException
    except YAMLError:
        raise ParserException
    except Exception as exception:
        raise UnhandledException(error=exception)


@router.get("/api/v1/validate")
async def validate_stages() -> tp.List[bool]:
    pass
