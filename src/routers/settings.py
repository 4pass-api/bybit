from fastapi import APIRouter, Depends

from src.dependencies.basic import get_redis_client
from src.dependencies.credentials import get_api_key
from src.schemas.basic import TextOnly

router = APIRouter(
    tags=['System Settings'],
    dependencies=[Depends(get_api_key)]
)


@router.post('/adminToken')
async def set_admin_token(
        token: TextOnly
):
    redis_client = get_redis_client()
    redis_client.set('ADMIN_TOKEN', token.text)
    redis_client.close()
    return {"adminToken": token.text}
