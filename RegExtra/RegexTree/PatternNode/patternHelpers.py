from RegExtra.RegexTree.PatternNode.enums import CategoryType, PatternType

import sys
import unicodedata
from collections import defaultdict

# unicode category lists from https://stackoverflow.com/questions/14245893/efficiently-list-all-characters-in-a-given-unicode-category
unicode_category = defaultdict(list)
for c in map(chr, range(sys.maxunicode + 1)):
    unicode_category[unicodedata.category(c)].append(c)

def getSetFromCategories(categoryList):
    return [item for sublist in [unicode_category[category] for category in categoryList] for item in sublist]

def patternToSet(node):
    match node['value']['type']:
        case PatternType.RANGE:
            return [chr(x + node['value']['value'][0]) for x in range(node['value']['value'][1] - node['value']['value'][0])]
        case PatternType.CATEGORY:
            match node['value']['value']:
                case CategoryType.DIGIT:
                    return getSetFromCategories(['Nd'])
                case CategoryType.WORD:
                    return getSetFromCategories(['Ll', 'Lu', 'Lt', 'Lo', 'Lm', 'Nd', 'Pc'])
        case _:
            return []