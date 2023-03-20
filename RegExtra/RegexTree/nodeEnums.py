from enum import Enum


class NodeType(Enum):
    UNKNOWN = -1
    LIST = 0
    QUANT = 1
    PATTERN = 2

class ListType(Enum):
    UNKNOWN = -1
    NORMAL = 0
    OR = 1