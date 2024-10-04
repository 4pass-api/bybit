from contextlib import asynccontextmanager

import ccxt
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from starlette.requests import Request

from src.dependencies.basic import get_redis_client
from src.routers.account import router as account_router
from src.routers.basic import router as basic_router
from src.routers.settings import router as settings_router
from src.routers.tradingview import router as tradingview_router
from src.schemas.basic import TextOnly

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = get_redis_client()

    app.state.exs = [ccxt.bybit({
        'apiKey': redis_client.get('BYBIT_APIKEY_1'),
        'secret': redis_client.get('BYBIT_SECRET_1')
    }), ccxt.bybit({
        'apiKey': redis_client.get('BYBIT_APIKEY_2'),
        'secret': redis_client.get('BYBIT_SECRET_2')
    })]

    redis_client.close()

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

app.include_router(settings_router)
app.include_router(basic_router)
app.include_router(account_router)
app.include_router(tradingview_router)


@app.get("/", response_model=TextOnly)
async def root():
    return TextOnly(text="Hello World")


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
