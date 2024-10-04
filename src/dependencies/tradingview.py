from fastapi import HTTPException, Depends, status

from src.dependencies.basic import get_ip


def request_from_tradingview(ip: str = Depends(get_ip)):
    if ip not in ["52.89.214.238", "34.212.75.30", "54.218.53.128", "52.32.178.7"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid IP: {ip}"
        )
