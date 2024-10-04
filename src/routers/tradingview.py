import json

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
        exs=Depends(get_exchanges)
):
    print("Received payload:", json.loads(payload.model_dump_json(indent=2)))

    if payload.symbol not in exs[0].markets:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Symbol {payload.symbol} not found"
        )

    order_size = payload.size / exs[0].markets[payload.symbol]['contractSize']

    try:
        if '1' in payload.action:
            params = {'positionIdx': 0}
            if 'close_position' in payload.action:
                params['reduceOnly'] = True
                current_position = exs[0].fetch_position(payload.symbol)

                if current_position['side'] == 'long':
                    assert payload.side == 'sell', f"Wrong side to close position: {current_position['side']} >> {payload.side}"
                else:
                    assert payload.side == 'buy', f"Wrong side to close position: {current_position['side']} >> {payload.side}"

                order_size = current_position['contracts']

            return exs[0].create_order(
                payload.symbol,
                'market',
                str(payload.side),
                order_size,
                None,
                params
            )

        else:
            params = {'positionIdx': 0}
            if 'close_position' in payload.action:
                params['reduceOnly'] = True
                current_position = exs[1].fetch_position(payload.symbol)

                if current_position['side'] == 'long':
                    assert payload.side == 'sell', f"Wrong side to close position: {current_position['side']} >> {payload.side}"
                else:
                    assert payload.side == 'buy', f"Wrong side to close position: {current_position['side']} >> {payload.side}"

                order_size = current_position['contracts']

            return exs[1].create_order(
                payload.symbol,
                'market',
                str(payload.side),
                order_size,
                None,
                params
            )

    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
