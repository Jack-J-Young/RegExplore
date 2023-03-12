from enum import Enum

class PatternType(Enum):
    UNKOWN = -1
    LITERAL = 0
    RANGE = 1
    CATEGORY = 2

class CategoryType(Enum):
    UNKOWN = -1,
    ANY = 0,
    DIGIT = 1,
    WORD = 2