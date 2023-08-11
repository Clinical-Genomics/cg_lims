from enum import Enum


class StrEnum(str, Enum):
    def __str__(self) -> str:
        return str.__str__(self)


class IntEnum(int, Enum):
    def __int__(self) -> int:
        return int.__int__(self)


class FloatEnum(float, Enum):
    def __int__(self) -> float:
        return float.__int__(self)
