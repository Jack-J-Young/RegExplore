import sre_parse
from RegExtra.RegexTree.PatternNode.PatternEnums import CategoryType, PatternType
from RegExtra.RegexTree.nodeEnums import NodeType

def createPatternNode(rawData, parent, path):
    node = {'type' : NodeType.PATTERN, 'parent' : parent, 'path' : path}
    
    charData = rawData[0]
    if charData[0] == sre_parse.CATEGORY:
        regex = ''
        value = CategoryType.UNKNOWN
        if charData[1] == sre_parse.CATEGORY_DIGIT:
            regex = r'\d'
            value = CategoryType.DIGIT
        elif charData[1] == sre_parse.CATEGORY_WORD:
            regex = r'\w'
            value = CategoryType.WORD
        value = CategoryType.DIGIT
        node['value'] = {
                'type' : PatternType.CATEGORY,
                'value' : value,
                'regex' : regex
            }
    elif charData[0] == sre_parse.RANGE:
        node['value'] = {
            'type' : PatternType.RANGE,
            'value' : (charData[1][0], charData[1][1]),
            'regex' : f'[{escapeChars(charData[1][0])}-{escapeChars(charData[1][1])}]'
        }
    else:
        node['type'] = NodeType.UNKNOWN
        node['value'] = None
        return node

    return node

def escapeChars(char):
    if set([chr(char)]) <= set('.^$*+?()[{\-]|'):
        return f'\{chr(char)}'
    return chr(char)

# def parsePatternValue(rawData):    
#     match rawData[0]:
#         case sre_parse.CATEGORY:
#             match rawData[1]:
#                 case sre_parse.CATEGORY_DIGIT:
#                     return (CategoryType.DIGIT, r'\d')
#                 case sre_parse.CATEGORY_WORD:
#                     return (CategoryType.WORD, r'\w')
#         case sre_parse.LITERAL:
#             return (rawData[1], chr(rawData[1]))
#         case sre_parse.RANGE:
#             return ()