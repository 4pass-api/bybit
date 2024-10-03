import json
import os
from contextlib import asynccontextmanager
from typing import Annotated

import ccxt
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException, status, Security, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import APIKeyHeader
from starlette.requests import Request

from src.schemas.basic import TextOnly
from src.schemas.tradingview import TradingViewRequest

load_dotenv()

api_key_header = APIKeyHeader(name='x-api-key', auto_error=False)


def get_api_key(api_key: str = Security(api_key_header)) -> str:
    if api_key != os.getenv('API_KEY', 'zxcvbnm1234'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )
    return api_key


def get_ip(request: Request):
    forwarded_for = request.headers.get("x-forwarded-for")
    try:
        client_ip = forwarded_for.split(",")[0]
    except:
        client_ip = request.client.host
    return client_ip


def request_from_tradingview(ip: str = Depends(get_ip)):
    if ip not in ["52.89.214.238", "34.212.75.30", "54.218.53.128", "52.32.178.7"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid IP: {ip}"
        )


def get_exchanges(request: Request):
    return request.app.state.exs


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.exs = [ccxt.bybit({
        'apiKey': os.getenv('BYBIT_APIKEY_1'),
        'secret': os.getenv('BYBIT_SECRET_1')
    }), ccxt.bybit({
        'apiKey': os.getenv('BYBIT_APIKEY_2'),
        'secret': os.getenv('BYBIT_SECRET_2')
    })]

    # Load the ML model
    for ex in app.state.exs:
        ex.load_markets()
    yield


app = FastAPI(
    title="Template FastAPI Backend Server",
    description="Template Description",
    version="0.0.1",
    contact={
        "name": "Author Name",
        "email": "example@exmaple.com",
    },
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=TextOnly)
async def root():
    return TextOnly(text="Hello World")


@app.get('/ip')
async def get_client_ip(ip: str = Depends(get_ip)):
    return {"ip": ip}


@app.get("/elements", include_in_schema=False)
async def api_documentation(request: Request):
    return HTMLResponse("""
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Elements in HTML</title>

    <script src="https://unpkg.com/@stoplight/elements/web-components.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/@stoplight/elements/styles.min.css">
  </head>
  <body>

    <elements-api
      apiDescriptionUrl="openapi.json"
      router="hash"
    />

  </body>
</html>""")


@app.get('/balance', dependencies=[Depends(get_api_key)])
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


@app.get('/positions', dependencies=[Depends(get_api_key)])
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


@app.post('/leverage', dependencies=[Depends(get_api_key)])
async def set_leverage(
        symbol: Annotated[
            str, Query(..., title="Symbol to set leverage for", description="Symbol to set leverage for")],
        leverage: Annotated[
            int, Query(..., title="Leverage to set", description="Leverage to set", ge=1, le=100)],
        exs=Depends(get_exchanges)
):
    try:
        return {idx: ex.set_leverage(leverage, symbol) for idx, ex in enumerate(exs, 1)}
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post('/setup', dependencies=[Depends(get_api_key)])
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


@app.get('/symbols')
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


@app.post('/oneway', dependencies=[Depends(request_from_tradingview)])
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
