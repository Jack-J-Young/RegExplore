import copy
from RegExtra.RegexTree.PatternNode.PatternEnums import CategoryType, PatternType
from RegExtra.RegexTree.PatternNode.patternHelpers import categoryToRegex, categoryToSet
from RegExtra.RegexTree.QuantNode.QuantEnums import QuantSpecials
from RegExtra.RegexTree.nodeEnums import NodeType

def replaceMinWrap(properties):
    if properties['currentNode']['type'] == NodeType.QUANT:
        acceptSet = [i['size'] for i in properties['acceptMatches']]

        newNode = copy.deepcopy(properties['currentNode'])
        newNode['value']['lower'] = min(acceptSet)
        newNode['value']['upper'] = max(acceptSet)
        return [newNode]
    else:
        acceptSet = [i['string'] for i in properties['acceptMatches']]

        # Get all characters from list of accept strings
        charSet = list(dict.fromkeys([item for sublist in [c for c in acceptSet] for item in sublist]))

        newNode = copy.deepcopy(properties['currentNode'])

        if min(charSet) == max(charSet):
            newNode['value'] = {
                'type' : PatternType.LITERAL,
                'value' : ord(min(charSet)),
                'regex' : f'{min(charSet)}'
            }
        else:
            newNode['value'] = {
                'type' : PatternType.RANGE,
                'value' : (ord(min(charSet)), ord(max(charSet))),
                'regex' : f'[{min(charSet)}-{max(charSet)}]'
            }

        return [newNode]

def inchWrapPattern(properties):
    acceptSet = [i['string'] for i in properties['acceptMatches']]

    parent = copy.deepcopy(properties['currentNode']['parent'])

    indexedSet = []
    for string in acceptSet:
        while len(indexedSet) < len(string):
            indexedSet.append([])
        
        for index in range(len(string)):
            if not string[index] in indexedSet[index]:
                indexedSet[index].append(string[index])
    
    output = []
    cumulativeSet = []
    for indexSet in indexedSet:
        cumulativeSet += indexSet
        newNode = copy.deepcopy(properties['currentNode'])

        if min(cumulativeSet) == max(cumulativeSet):
            newNode['value'] = {
                'type' : PatternType.LITERAL,
                'value' : ord(min(cumulativeSet)),
                'regex' : f'{min(cumulativeSet)}'
            }
        else:
            newNode['value'] = {
                'type' : PatternType.RANGE,
                'value' : (ord(min(cumulativeSet)), ord(max(cumulativeSet))),
                'regex' : f'[{min(cumulativeSet)}-{max(cumulativeSet)}]'
            }

        output.append(newNode)
    
    return output

def setCategoryPattern(properties):
    acceptSet = [i['string'] for i in properties['acceptMatches']]
    
    charSet = [item for sublist in [c for c in acceptSet] for item in sublist]

    validCategories = []
    for category in CategoryType:
        if category != CategoryType.UNKOWN:
            categorySet = categoryToSet(category)

            if set(charSet).issubset(categorySet):
                validCategories.append(category)
    
    output = []
    for category in validCategories:
        newNode = copy.deepcopy(properties['currentNode'])
        newNode['value'] = {
                'type' : PatternType.CATEGORY,
                'value' : category,
                'regex' : categoryToRegex(category)
            }
        output.append(newNode)

    return output

def bruteDelete(properties):
    return range(len(properties['currentNode']['value']))

def bruteInsert(properties):
    indices = range(len(properties['currentNode']['value']))

    quant = {
        'type' : NodeType.QUANT,
        'value' : {
            'lower' : 0,
            'upper' : QuantSpecials.MAX_REPEAT,
            'child' : None
        },
        'parent' : None,
        'path' : []
    }

    quant['value']['child'] = {
        'type' : NodeType.PATTERN,
        'value' : {
            'type' : PatternType.CATEGORY,
            'value' : CategoryType.ANY,
            'regex' : '.'
        },
        'parent' : quant,
        'path' : ['value', 'child']
    }

    return [(i, copy.deepcopy(quant)) for i in indices]

