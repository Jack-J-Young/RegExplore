from enum import Enum

class PatternType(Enum):
    UNKNOWN = -1
    LITERAL = 0
    RANGE = 1
    CATEGORY = 2
    OR = 3

class CategoryType(Enum):
    UNKNOWN = -1,
    ANY = 0,
    DIGIT = 1,
    WORD = 2