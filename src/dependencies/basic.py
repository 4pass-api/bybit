from typing import List

from ccxt import Exchange
from redis import StrictRedis as Redis
from starlette.requests import Request


def get_ip(request: Request):
    forwarded_for = request.headers.get("x-forwarded-for")
    try:
        client_ip = forwarded_for.split(",")[0]
    except:
        client_ip = request.client.host
    return client_ip


def get_exchanges(request: Request) -> List[Exchange]:
    return request.app.state.exs


def get_redis_client():
    r = Redis(host='redis', port=6379, decode_responses=True)
    return r
