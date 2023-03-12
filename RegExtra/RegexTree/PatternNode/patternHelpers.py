from RegExtra.RegexTree.PatternNode.PatternEnums import CategoryType, PatternType

import sys
import unicodedata
from collections import defaultdict

# unicode category lists from https://stackoverflow.com/questions/14245893/efficiently-list-all-characters-in-a-given-unicode-category
unicode_category = defaultdict(list)
unicode_any = []
for c in map(chr, range(sys.maxunicode + 1)):
    unicode_category[unicodedata.category(c)].append(c)
    unicode_any.append(c)

def getSetFromCategories(categoryList):
    return [item for sublist in [unicode_category[category] for category in categoryList] for item in sublist]

def categoryToSet(category):
    match category:
        case CategoryType.ANY:
            return unicode_any
        case CategoryType.DIGIT:
            return getSetFromCategories(['Nd'])
        case CategoryType.WORD:
            return getSetFromCategories(['Ll', 'Lu', 'Lt', 'Lo', 'Lm', 'Nd', 'Pc'])

def categoryToRegex(category):
    match category:
        case CategoryType.ANY:
            return '.'
        case CategoryType.DIGIT:
            return '\d'
        case CategoryType.WORD:
            return '\w'
        case _:
            return ''

def patternToSet(node):
    match node['value']['type']:
        case PatternType.RANGE:
            return [chr(x + node['value']['value'][0]) for x in range(node['value']['value'][1] - node['value']['value'][0])]
        case PatternType.CATEGORY:
            return categoryToSet(node['value']['value'])
        case _:
            return []