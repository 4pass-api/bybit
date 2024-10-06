from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.dependencies.basic import get_exchanges, get_redis_client
from src.dependencies.credentials import get_api_key
from src.schemas.basic import Credentials

router = APIRouter(
    tags=['Exchange Account'],
    dependencies=[Depends(get_api_key)]
)


@router.get('/balance')
async def balance(
        exs=Depends(get_exchanges)
):
    try:
        return {idx: ex.fetch_balance() for idx, ex in enumerate(exs, 1)}
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get('/positions')
async def positions(
        symbol: Annotated[
            str, Query(..., title="Symbol to get positions for", description="Symbol to get positions for")],
        exs=Depends(get_exchanges)
):
    try:
        return {idx: ex.fetch_position(symbol) for idx, ex in enumerate(exs, 1)}
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post('/leverage')
async def set_leverage(
        symbol: Annotated[
            str, Query(..., title="Symbol to set leverage for", description="Symbol to set leverage for")],
        leverage: Annotated[
            int, Query(..., title="Leverage to set", description="Leverage to set", ge=1, le=100)],
        exs=Depends(get_exchanges)
):
    try:
        return {idx: ex.set_leverage(leverage, symbol) for idx, ex in enumerate(exs, 1) if ex.apiKey is not None}
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post('/setup')
async def setup_account(
        symbol: Annotated[
            str, Query(..., title="Symbol to setup account for", description="Symbol to setup account for")
        ],
        exs=Depends(get_exchanges)
):
    try:
        return {idx: ex.set_position_mode(False, symbol) for idx, ex in enumerate(exs, 1)}
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get('/apiKey')
async def get_api_key(
        exs=Depends(get_exchanges)
):
    return {idx: ex.apiKey for idx, ex in enumerate(exs, 1)}


@router.post('/apiKey')
async def set_api_key(
        credentials: Credentials,
        _idx: Annotated[
            int, Query(..., title="Exchange index", description="Exchange index", ge=1, le=2)
        ] = 1,
        exs=Depends(get_exchanges)
):
    idx = _idx - 1

    redis_client = get_redis_client()

    old_apiKey = exs[idx].apiKey
    old_secret = exs[idx].secret

    result = None
    try:
        exs[idx].apiKey = credentials.apiKey
        exs[idx].secret = credentials.secretKey
        result = exs[idx].fetch_balance()
        redis_client.set(f'BYBIT_APIKEY_{idx}', credentials.apiKey)
        redis_client.set(f'BYBIT_SECRET_{idx}', credentials.secretKey)
    except Exception as e:
        exs[idx].apiKey = old_apiKey
        exs[idx].secret = old_secret
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    return result
