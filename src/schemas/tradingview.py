from enum import Enum, EnumMeta
from typing import Literal

from pydantic import BaseModel, Field


class MetaEnum(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class CustomStringEnum(str, Enum, metaclass=MetaEnum):
    def __str__(self):
        return self.value


class ActionEnum(CustomStringEnum):
    OPEN_POSITION_1 = "open_position_1"
    CLOSE_POSITION_1 = "close_position_1"
    OPEN_POSITION_2 = "open_position_2"
    CLOSE_POSITION_2 = "close_position_2"


class TradingViewRequest(BaseModel):
    side: Literal['buy', 'sell'] = Field(..., title="Side of the trade")
    action: ActionEnum = Field(..., title="Action to take")
    size: float = Field(..., title="Size of the trade")
    symbol: str = Field(..., title="Symbol to trade")
