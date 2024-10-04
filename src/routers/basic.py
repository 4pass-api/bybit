from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.dependencies.basic import get_ip, get_exchanges

router = APIRouter(
    tags=['Basic']
)


@router.get('/ip')
async def get_client_ip(ip: str = Depends(get_ip)):
    return {"ip": ip}


@router.get('/symbols')
async def get_symbols_by_keyword(
        keyword: Annotated[
            str, Query(..., title="Keyword to search for", description="Keyword to search for")
        ],
        exs=Depends(get_exchanges)
):
    all_symbols = list(exs[0].markets.keys())
    filter_symbols = [symbol for symbol in all_symbols if keyword.lower() in symbol.lower()]
    return [symbol for symbol in filter_symbols if
            exs[0].markets[symbol]['active'] and exs[0].markets[symbol]['contract']]
