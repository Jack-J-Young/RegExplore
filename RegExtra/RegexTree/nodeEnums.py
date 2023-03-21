from enum import Enum


class NodeType(Enum):
    UNKNOWN = -1
    LIST = 0
    QUANT = 1
    PATTERN = 2
    ASSERT = 3

class ListType(Enum):
    UNKNOWN = -1
    NORMAL = 0
    OR = 1

class AssertType(Enum):
    UNKNOWN = -1
    LOOK_AHEAD = 0
    LOOK_AHEAD_NOT = 1
    LOOK_BEHIND = 2
    LOOK_BEHIND_NOT = 3