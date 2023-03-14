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

# def minWrapCharSet(chars, parent):
#     newNode = {
#         'type' : NodeType.PATTERN,
#         'value' : None,
#         'parent' : parent
#     }

#     if min(chars) == max(chars):
#         newNode['value'] = {
#             'type' : PatternType.LITERAL,
#             'value' : ord(min(chars)),
#             'regex' : f'{min(chars)}'
#         }
#     else:
#         newNode['value'] = {
#             'type' : PatternType.RANGE,
#             'value' : (ord(min(chars)), ord(max(chars))),
#             'regex' : f'[{min(chars)}-{max(chars)}]'
#         }
    
#     return newNode

# def categorysFromChars(chars, parent):
#     validCategories = []
#     for category in CategoryType:
#         if category != CategoryType.UNKOWN:
#             categorySet = categoryToSet(category)

#             if set(chars).issubset(categorySet):
#                 validCategories.append(category)
    
#     output = []
#     for category in validCategories:
#         output.append({
#             'type' : NodeType.PATTERN,
#             'value' : {
#                 'type' : PatternType.CATEGORY,
#                 'value' : category,
#                 'regex' : categoryToRegex(category)
#             },
#             'parent' : parent
#         })
    
#     return output

# def minWrapQuant(properties):
#     acceptSet = [i['size'] for i in properties['acceptMatches']]
#     # rejectSet = [i['size'] for i in properties['acceptMatches']]

#     newNode = copy.deepcopy(properties['currentNode'])
#     newNode['value']['lower'] = min(acceptSet)
#     newNode['value']['upper'] = max(acceptSet)
#     return [newNode]

# def setCategoryPattern(properties):
#     acceptSet = [i['string'] for i in properties['acceptMatches']]
    
#     charSet = [item for sublist in [c for c in acceptSet] for item in sublist]

#     return categorysFromChars(charSet, copy.deepcopy(properties['currentNode']['parent']))
#     # validCategories = []
#     # for category in CategoryType:
#     #     if category != CategoryType.UNKOWN:
#     #         categorySet = categoryToSet(category)

#     #         if set(charSet).issubset(categorySet):
#     #             validCategories.append(category)
    
#     # output = []
#     # for category in validCategories:
#     #     output.append({
#     #         'type' : NodeType.PATTERN,
#     #         'value' : {
#     #             'type' : PatternType.CATEGORY,
#     #             'value' : category,
#     #             'regex' : categoryToRegex(category)
#     #         },
#     #         'path' : copy.deepcopy(properties['currentNode']['path'])
#     #     })
    
#     # return output 

# def minWrapPattern(properties):
#     acceptSet = [i['string'] for i in properties['acceptMatches']]
#     # rejectSet = [i['string'] for i in properties['rejectMatches']]

#     # Get all characters from list of accept strings
#     charSet = list(dict.fromkeys([item for sublist in [c for c in acceptSet] for item in sublist]))

#     output = [minWrapCharSet(charSet, properties['currentNode']['parent'])]

#     return output

# def inchWrapPattern(properties):
#     acceptSet = [i['string'] for i in properties['acceptMatches']]

#     parent = copy.deepcopy(properties['currentNode']['parent'])

#     indexedSet = []
#     for string in acceptSet:
#         while len(indexedSet) < len(string):
#             indexedSet.append([])
        
#         for index in range(len(string)):
#             if not string[index] in indexedSet[index]:
#                 indexedSet[index].append(string[index])
    
#     output = []
#     cumulativeSet = []
#     for indexSet in indexedSet:
#         cumulativeSet += indexSet
#         output.append(minWrapCharSet(cumulativeSet, parent))
    
#     return output

# def bruteSplit(properties):
#     # Get possible quant ranges
#     lower = properties['currentNode']['value']['lower']
#     upper = properties['currentNode']['value']['upper']

#     output = []

#     if upper == QuantSpecials.MAX_REPEAT:
#         a = 0
#         # MAYBE ADD, not sure

#         # node1 = copy.deepcopy(properties['currentNode'])
#         # node2 = copy.deepcopy(properties['currentNode'])

#         # node1['value']['lower'] = pLower1
#         # node1['value']['upper'] = QuantSpecials.MAX_REPEAT

#         # node2['value']['lower'] = pLower2
#         # node2['value']['upper'] = QuantSpecials.MAX_REPEAT

#         # output.append([node1, node2])
#     else:
#         for pLower1 in range(lower + 1):
#             pLower2 = lower - pLower1
#             for pUpper1Raw in range(upper - pLower1):
#                 pUpper1 = pUpper1Raw + pLower1

#                 pUpper2 = upper - pUpper1

#                 node1 = copy.deepcopy(properties['currentNode'])
#                 node2 = copy.deepcopy(properties['currentNode'])

#                 node1['value']['lower'] = pLower1
#                 node1['value']['upper'] = pUpper1

#                 node2['value']['lower'] = pLower2
#                 node2['value']['upper'] = pUpper2

#                 output.append([node1, node2])
    
#     return output



