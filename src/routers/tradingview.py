import json
from typing import List, Annotated

from ccxt import bybit
from fastapi import APIRouter, Depends, HTTPException, status

from src.dependencies.basic import get_exchanges
from src.dependencies.tradingview import request_from_tradingview
from src.schemas.tradingview import TradingViewRequest

router = APIRouter(
    tags=['TradingView'],
    dependencies=[Depends(request_from_tradingview)]
)


@router.post('/oneway')
async def oneway_action(
        payload: TradingViewRequest,
        exs: Annotated[List[bybit], Depends(get_exchanges)]
):
    print("Received payload:", json.loads(payload.model_dump_json(indent=2)))

    if payload.symbol not in exs[0].markets:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Symbol {payload.symbol} not found"
        )

    order_size = payload.size / exs[0].markets[payload.symbol]['contractSize']
    account_idx = payload.action.split('_')[-1]
    account_idx = int(account_idx) - 1

    current_position = exs[account_idx].fetch_position(payload.symbol)
    p_side = current_position['side'] if current_position else None
    p_size = current_position['contracts'] if current_position else 0

    params = {'positionIdx': 0}

    try:

        if 'close_position' in payload.action:
            params['reduceOnly'] = True
            if p_size > 0:
                if payload.side == 'buy':
                    assert p_side == 'short', f"Wrong side to close position: {p_side} >> {payload.side}"
                else:
                    assert p_side == 'long', f"Wrong side to close position: {p_side} >> {payload.side}"

            order_size = p_size

        if 'open_position' in payload.action:
            if p_size > 0:
                if (payload.side == 'buy' and p_side == 'short') or \
                        (payload.side == 'sell' and p_side == 'long'):
                    # close position first
                    _params = {'positionIdx': 0, 'reduceOnly': True}
                    exs[account_idx].create_order(
                        symbol=payload.symbol,
                        type='market',
                        side='buy' if p_side == 'short' else 'sell',
                        amount=p_size,
                        price=None,
                        params=_params
                    )

        return exs[account_idx].create_order(
            symbol=payload.symbol,
            type='market',
            side=payload.side,
            amount=order_size,
            price=None,
            params=params
        )

    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
