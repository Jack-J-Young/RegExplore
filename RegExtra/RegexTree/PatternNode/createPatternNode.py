import sre_parse
from RegExtra.RegexTree.PatternNode.enums import CategoryType, PatternType
from RegExtra.RegexTree.regexTree import NodeType


def createPatternNode(rawData):
    node = {'type' : NodeType.PATTERN}
    
    charData = rawData[0]
    if len(rawData) > 1:
        print('ERROR CHECK THIS IN CODE')
    if charData[0] == sre_parse.CATEGORY:
        regex = ''
        value = CategoryType.UNKOWN
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
            'value' : (chr(charData[1][0]), chr(charData[1][1])),
            'regex' : f'[{chr(charData[1][0])}-{chr(charData[1][1])}]'
        }
    else:
        node['type'] = NodeType.UNKOWN
        node['value'] = None
        return node
    
    return node