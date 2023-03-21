import copy
import random
from RegExtra.RegexTree.PatternNode.PatternEnums import CategoryType, PatternType
from RegExtra.RegexTree.PatternNode.createPatternNode import escapeChars
from RegExtra.RegexTree.PatternNode.patternHelpers import categoryToRegex, categoryToSet
from RegExtra.RegexTree.QuantNode.QuantEnums import QuantSpecials
from RegExtra.RegexTree.nodeEnums import ListType, NodeType
from RegExtra.RegexTree.regexTree import nodeEqual

def replaceMinWrap(properties):
    if properties['currentNode']['type'] == NodeType.QUANT:
        childrenSets = [i['children'] for i in properties['acceptMatches']]
        acceptSet = [len(''.join(node['string'] for node in cSet)) for cSet in childrenSets]

        newNode = copy.deepcopy(properties['currentNode'])
        if len(acceptSet) > 0:
            newNode['value']['lower'] = min(acceptSet)
            newNode['value']['upper'] = max(acceptSet)
            
        if not newNode['value']['upper'] == 0:
            return [newNode]
        return []
    else:
        if properties['currentNode']['parent']['value']['lower'] == 1 and properties['currentNode']['parent']['value']['upper'] == 1:
            print(0)
        
        acceptSet = [i['string'] for i in properties['acceptMatches']]

        # Get all characters from list of accept strings
        charSet = list(dict.fromkeys([item for sublist in [c for c in acceptSet] for item in sublist]))

        newNode = copy.deepcopy(properties['currentNode'])

        if len(charSet) > 0:
            if min(charSet) == max(charSet):
                newNode['value'] = {
                    'type' : PatternType.LITERAL,
                    'value' : ord(min(charSet)),
                    'regex' : escapeChars(ord(min(charSet)))
                }
            else:
                newNode['value'] = {
                    'type' : PatternType.RANGE,
                    'value' : (ord(min(charSet)), ord(max(charSet))),
                    'regex' : f'[{min(charSet)}-{max(charSet)}]'
                }
        if newNode['value']['regex'] != '':
            return [newNode]
        return []

def randomQuantChangeI(properties):
    output = []
    
    newNode = copy.deepcopy(properties['currentNode'])
    newNode['value']['lower'] = max(0, newNode['value']['lower'] - 1)
    output.append(newNode)
    
    newNode = copy.deepcopy(properties['currentNode'])
    if newNode['value']['upper'] == QuantSpecials.MAX_REPEAT:
        newNode['value']['lower'] = newNode['value']['lower'] + 1
    else:
        newNode['value']['lower'] = min(newNode['value']['lower'] + 1, newNode['value']['upper'])
    output.append(newNode)
    
    if newNode['value']['upper'] != QuantSpecials.MAX_REPEAT:
        newNode = copy.deepcopy(properties['currentNode'])
        newNode['value']['upper'] = max(newNode['value']['upper'] - 1, newNode['value']['lower'], 1)
        output.append(newNode)
        
        newNode = copy.deepcopy(properties['currentNode'])
        newNode['value']['upper'] = newNode['value']['upper'] + 1
        output.append(newNode)
    
    return output
    

def randomQuantChangeP(properties):
    output = []
    
    randomPercent = random.random()
    
    newNode = copy.deepcopy(properties['currentNode'])
    newNode['value']['lower'] = max(0, int(newNode['value']['lower']*randomPercent))
    output.append(newNode)
    
    newNode = copy.deepcopy(properties['currentNode'])
    if newNode['value']['upper'] == QuantSpecials.MAX_REPEAT:
        newNode['value']['lower'] = newNode['value']['lower'] + int(newNode['value']['lower']*randomPercent)
    else:
        newNode['value']['lower'] = min(newNode['value']['lower'] + int(newNode['value']['lower']*randomPercent), newNode['value']['upper'])
    output.append(newNode)
    
    if newNode['value']['upper'] != QuantSpecials.MAX_REPEAT:
        newNode = copy.deepcopy(properties['currentNode'])
        newNode['value']['upper'] = max(int(newNode['value']['upper']*randomPercent), newNode['value']['lower'], 1)
        output.append(newNode)
        
        newNode = copy.deepcopy(properties['currentNode'])
        newNode['value']['upper'] = newNode['value']['upper'] + int(newNode['value']['upper']*randomPercent)
        output.append(newNode)
    
    return output

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
            
        if newNode['value']['regex'] != '':
            output.append(newNode)
    
    return output

def inchCategoryPattern(properties):
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

        validCategories = []
        for category in CategoryType:
            if category != CategoryType.UNKNOWN:
                categorySet = categoryToSet(category)

                if set(cumulativeSet).issubset(categorySet):
                    validCategories.append(category)
        
        for category in validCategories:
            if category != CategoryType.ANY:
                newNode = copy.deepcopy(properties['currentNode'])
                newNode['value'] = {
                        'type' : PatternType.CATEGORY,
                        'value' : category,
                        'regex' : categoryToRegex(category)
                    }
                output.append(newNode)
    
    return output

def setCategoryPattern(properties):
    acceptSet = [i['string'] for i in properties['acceptMatches']]
    
    charSet = [item for sublist in [c for c in acceptSet] for item in sublist]

    validCategories = []
    for category in CategoryType:
        if category != CategoryType.UNKNOWN:
            categorySet = categoryToSet(category)

            if set(charSet).issubset(categorySet):
                validCategories.append(category)
    
    output = []
    for category in validCategories:
        if category != CategoryType.ANY:
            newNode = copy.deepcopy(properties['currentNode'])
            newNode['value'] = {
                    'type' : PatternType.CATEGORY,
                    'value' : category,
                    'regex' : categoryToRegex(category)
                }
            output.append(newNode)

    return output

def charsToOr(properties):
    if properties['currentNode']['value']['type'] == PatternType.RANGE:
        oldNode = copy.deepcopy(properties['currentNode'])
        
        acceptSet = range(oldNode['value']['value'][0], oldNode['value']['value'][1] + 1)
        # acceptSet = [i['string'] for i in properties['currentNode']]
        
        # acceptSet = list(dict.fromkeys(acceptSet))
        
        # acceptSet = sorted(acceptSet)
        
        setNodes = [{
            'type' : NodeType.QUANT,
            'value' : {
                'upper' : 1,
                'lower' : 1,
                'child' : {
                    'type' : NodeType.PATTERN,
                    'value' : {
                        'type' : PatternType.LITERAL,
                        'value' : i,
                        'regex' : chr(i)
                    },
                    'parent' : None,
                    'path' : ['value', 'child']
                }
            },
            'parent' : None,
            'path' : ['value', 'children']
        } for i in acceptSet]
        
        output = {
            'type' : NodeType.LIST,
            'value' : {
                'type' : ListType.OR,
                'children' : setNodes
            },
            'parent' : oldNode['parent'],
            'path' : oldNode['path']
        }
        
        for nodeIndex in range(len(setNodes)):
            setNodes[nodeIndex]['parent'] = output
            setNodes[nodeIndex]['path'] = setNodes[nodeIndex]['path'] + [nodeIndex]
            setNodes[nodeIndex]['value']['child']['parent'] = setNodes[nodeIndex]
        
        parent = oldNode['parent']
        for p in oldNode['path'][:-1]:
            parent = oldNode['parent'][p]
        
        parent[oldNode['path'][-1]] = output
        
        return [output]
    return []

def bruteDelete(properties):
    if len(properties['currentNode']['value']) > 1:
        return range(len(properties['currentNode']['value']))
    else:
        return []

def redundancyDelete(properties):
    output = []
    
    index = 0
    offset = 0
    while index + 1 < len(properties['currentNode']['value']):
        if nodeEqual(properties['currentNode']['value'][index]['value']['child'], properties['currentNode']['value'][index + 1]['value']['child']):
            # After is not lower 0
            if properties['currentNode']['value'][index + 1]['value']['lower'] != 0:
                output.append(index)
            
            # After is not same when upper is inf
            elif properties['currentNode']['value'][index]['value']['upper'] == QuantSpecials.MAX_REPEAT:
                output.append(index + 1)
                offset += 1
        
        index += 1
    
    return output

def repeatInsert(properties):
    output = []
    
    for index in range(len(properties['currentNode']['value']['children']) - 1):
        currentNode = properties['currentNode']['value']['children'][index]
        nextNode = properties['currentNode']['value']['children'][index + 1]
        
        output.append([(index, copy.deepcopy(nextNode)),(index, copy.deepcopy(currentNode))])
    
    return output

def bruteInsert(properties):
    indices = range(len(properties['currentNode']['value']['children']) + 1)

    quant = {
        'type' : NodeType.QUANT,
        'value' : {
            'lower' : 1,
            'upper' : 1,
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

    output = []
    for i in indices:
        currentNodeTest = False
        if i < len(properties['currentNode']['value']['children']):
            currentNodeTest = (properties['currentNode']['value']['children'][i]['value']['lower'] == 0 and properties['currentNode']['value']['children'][i]['value']['upper'] == QuantSpecials.MAX_REPEAT) and properties['currentNode']['value']['children'][i]['value']['child']['value']['value'] == CategoryType.ANY
        previousNodeTest = False
        if i - 1 >= 0:
            previousNodeTest = (properties['currentNode']['value']['children'][i - 1]['value']['lower'] == 0 and properties['currentNode']['value']['children'][i - 1]['value']['upper'] == QuantSpecials.MAX_REPEAT) and properties['currentNode']['value']['children'][i - 1]['value']['child']['value']['value'] == CategoryType.ANY
        nextNodeTest = False
        if i + 1 < len(properties['currentNode']['value']):
            previousNodeTest = (properties['currentNode']['value']['children'][i + 1]['value']['lower'] == 0 and properties['currentNode']['value']['children'][i + 1]['value']['upper'] == QuantSpecials.MAX_REPEAT) and properties['currentNode']['value']['children'][i + 1]['value']['child']['value']['value'] == CategoryType.ANY
        
        if not (currentNodeTest or previousNodeTest or nextNodeTest):
            output.append([(i, copy.deepcopy(quant))])
    return output

def quantsToKeleene(properties):
    lengthSum = len(properties['currentNode']['parent']['value'])
    
    newNode = copy.deepcopy(properties['currentNode'])
    newNode['value']['lower'] = 0
    # newNode['value']['upper'] = lengthSum
    newNode['value']['upper'] = QuantSpecials.MAX_REPEAT
    
    return [newNode]