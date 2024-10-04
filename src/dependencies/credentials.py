from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from src.dependencies.basic import get_redis_client

api_key_header = APIKeyHeader(name='x-api-key', auto_error=False)


def get_api_key(api_key: str = Security(api_key_header)) -> str:
    redis_client = get_redis_client()
    admin_token = redis_client.get('ADMIN_TOKEN')
    redis_client.close()

    if admin_token is None:
        admin_token = 'zxcvbnm1234'

    if api_key != admin_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )
    return api_key
