import copy
import sre_parse
import re
from RegExtra.RegexTree.PatternNode.createPatternNode import createPatternNode, escapeChars
from RegExtra.RegexTree.PatternNode.PatternEnums import CategoryType, PatternType
from RegExtra.RegexTree.QuantNode.QuantEnums import QuantSpecials
from RegExtra.RegexTree.QuantNode.createQuantNode import createQuantNode
from RegExtra.RegexTree.nodeEnums import ListType, NodeType
from RegExtra.solveHelpers import getOrderedPerms
import json

# Turns ast into regex tree object
def regexToNode(rawData, parent = None, path = []): 

    node = {
        'type' : NodeType.UNKNOWN,
        'value' : None,
        'parent' : parent,
        'path' : path
    }

    # List element
    if isinstance(rawData, sre_parse.SubPattern):
        if len(rawData.data) == 1:
            # Dont create list if only 1 element
            node = regexToNode(rawData.data[0], parent, path)
        else:
            # Recursively call for all elements in list
            node = {
                'type' : NodeType.LIST,
                'value' : {
                    'type' : ListType.NORMAL,
                    'children' : None
                },
                'parent' : parent,
                'path' : path
            }
            
            node['value']['children'] = [regexToNode(rawData.data[subDataIndex], node, ['value', 'children', subDataIndex]) for subDataIndex in range(len(rawData.data))]
            
            if len(node['value']['children']) == 1:
                node = node['value']['children'][0]
                node['parent'] = parent
                node['path'] = path
            else:
                for childIndex in range(len(node['value']['children'])):
                    if node['value']['children'][childIndex]['type'] != NodeType.QUANT:
                        node['value']['children'][childIndex] = {
                            'type': NodeType.QUANT,
                            'value' : {
                                'lower' : 1,
                                'upper' : 1,
                                'child' : node['value']['children'][childIndex]
                            },
                            'parent' : node,
                            'path' : node['value']['children'][childIndex]['path']
                        }
                        
                        node['value']['children'][childIndex]['value']['child']['parent'] = node['value']['children'][childIndex]
                        node['value']['children'][childIndex]['value']['child']['path'] = ['value', 'child']


    elif isinstance(rawData, tuple):
        #  Quant nodes
        if rawData[0] == sre_parse.MAX_REPEAT:
            node = createQuantNode(rawData[1], parent, path)
            node['value']['child'] = regexToNode(rawData[1][2], node, ['value', 'child'])

        elif rawData[0] == sre_parse.SUBPATTERN:
            node = regexToNode(rawData[1][3], parent, path)
        
        elif rawData[0] == sre_parse.BRANCH:
            node = {
                'type' : NodeType.LIST,
                'value' : {
                    'type' : ListType.OR,
                    'children' : None
                },
                'parent' : parent,
                'path' : path
            }
            
            node['value']['children'] = [regexToNode(rawData[1][1][subDataIndex], node, ['value', 'children', subDataIndex]) for subDataIndex in range(len(rawData[1][1]))]
        
            if len(node['value']['children']) == 1:
                node = node['value']['children'][0]
                node['parent'] = parent
                node['path'] = path
            else:
                for childIndex in range(len(node['value']['children'])):
                    if node['value']['children'][childIndex]['type'] != NodeType.QUANT:
                        node['value']['children'][childIndex] = {
                            'type': NodeType.QUANT,
                            'value' : {
                                'lower' : 1,
                                'upper' : 1,
                                'child' : node['value']['children'][childIndex]
                            },
                            'parent' : node,
                            'path' : node['value']['children'][childIndex]['path']
                        }
                        
                        node['value']['children'][childIndex]['value']['child']['parent'] = node['value']['children'][childIndex]
                        node['value']['children'][childIndex]['value']['child']['path'] = ['value', 'child']

        # Pattern: Literal
        elif rawData[0] == sre_parse.LITERAL:
            node['type'] = NodeType.PATTERN
            node['value'] = {
                'type' : PatternType.LITERAL,
                'value' : escapeChars(rawData[1]),
                'regex' : f'{escapeChars(rawData[1])}'
            } 

        # Pattern: everything else
        elif rawData[0] == sre_parse.IN:
            node = {
                'type' : NodeType.LIST,
                'value' : {
                    'type' : ListType.OR,
                    'children' : None
                },
                'parent' : parent,
                'path' : path
            }
            
            node['value']['children'] = [regexToNode(rawData[1][subDataIndex], node, ['value', 'children', subDataIndex]) for subDataIndex in range(len(rawData[1]))]

            if len(node['value']['children']) == 1:
                node = node['value']['children'][0]
                node['parent'] = parent
                node['path'] = path
            else:
                for childIndex in range(len(node['value']['children'])):
                    if node['value']['children'][childIndex]['type'] != NodeType.QUANT:
                        node['value']['children'][childIndex] = {
                            'type': NodeType.QUANT,
                            'value' : {
                                'lower' : 1,
                                'upper' : 1,
                                'child' : node['value']['children'][childIndex]
                            },
                            'parent' : node,
                            'path' : node['value']['children'][childIndex]['path']
                        }
                        
                        node['value']['children'][childIndex]['value']['child']['parent'] = node['value']['children'][childIndex]
                        node['value']['children'][childIndex]['value']['child']['path'] = ['value', 'child']
            # if len(rawData[1]) > 1:
            #     node = {
            #         'type' : NodeType.LIST,
            #         'value' : {
            #             'type' : ListType.OR,
            #             'children' : None
            #         },
            #         'parent' : parent,
            #         'path' : path
            #     }
                
            #     node['value']['children'] = [regexToNode(rawData[1][subDataIndex], node, ['value', 'children', subDataIndex]) for subDataIndex in range(len(rawData[1]))]
            
            #     for childIndex in range(len(node['value']['children'])):
            #         if node['value']['children'][childIndex]['type'] != NodeType.QUANT:
            #             node['value']['children'][childIndex] = {
            #                 'type': NodeType.QUANT,
            #                 'value' : {
            #                     'lower' : 1,
            #                     'upper' : 1,
            #                     'child' : node['value']['children'][childIndex]
            #                 },
            #                 'parent' : node,
            #                 'path' : node['value']['children'][childIndex]['path']
            #             }
                        
            #             node['value']['children'][childIndex]['value']['child']['parent'] = node['value']['children'][childIndex]
            #             node['value']['children'][childIndex]['value']['child']['path'] = ['value', 'child']
            # else:
            #     node = regexToNode(rawData[1][0], parent, path)
        if rawData[0] == sre_parse.CATEGORY:
            node['type'] = NodeType.PATTERN
            
            regex = ''
            value = CategoryType.UNKNOWN
            if rawData[1] == sre_parse.CATEGORY_DIGIT:
                regex = r'\d'
                value = CategoryType.DIGIT
            elif rawData[1] == sre_parse.CATEGORY_WORD:
                regex = r'\w'
                value = CategoryType.WORD
            value = CategoryType.DIGIT
            node['value'] = {
                    'type' : PatternType.CATEGORY,
                    'value' : value,
                    'regex' : regex
                }
        elif rawData[0] == sre_parse.RANGE:
            node['type'] = NodeType.PATTERN
            node['value'] = {
                'type' : PatternType.RANGE,
                'value' : (rawData[1][0], rawData[1][1]),
                'regex' : f'[{escapeChars(rawData[1][0])}-{escapeChars(rawData[1][1])}]'
        }
        elif rawData[0] == sre_parse.ANY:
            node['type'] = NodeType.PATTERN
            node['value'] = {
                'type' : PatternType.CATEGORY,
                'value' : CategoryType.ANY,
                'regex' : '.'
            }

    return node

# Create regex string to regex tree
def nodeToRegex(parentNode):
    if parentNode == None:
        return ''

    if parentNode['type'] == NodeType.LIST:
        if parentNode['value']['type'] == ListType.NORMAL:
            return '(' + ''.join([nodeToRegex(i) for i in parentNode['value']['children']]) + ')'
        elif parentNode['value']['type'] == ListType.OR:
            if len(list(filter(lambda x : not (x['value']['lower'] == 1 and x['value']['upper'] == 1), parentNode['value']['children']))) == 0:
                aggregate = ''
                for i in parentNode['value']['children']:
                    r = nodeToRegex(i)
                    if r[0] == '[' and r[-1] == ']':
                        aggregate += r[1:-1]
                    else:
                        aggregate += r
                return f"[{aggregate}]"
            else:
                return f"({'|'.join([nodeToRegex(i) for i in parentNode['value']['children']])})"
    elif parentNode['type'] == NodeType.QUANT:
        if parentNode['value']['lower'] == 0 and parentNode['value']['upper'] == QuantSpecials.MAX_REPEAT:
            return nodeToRegex(parentNode['value']['child']) + '*'
        elif parentNode['value']['lower'] == 1 and parentNode['value']['upper'] == QuantSpecials.MAX_REPEAT:
            return nodeToRegex(parentNode['value']['child']) + '+'
        elif parentNode['value']['lower'] == 0 and parentNode['value']['upper'] == 1:
            return nodeToRegex(parentNode['value']['child']) + '?'
        elif parentNode['value']['lower'] == 1 and parentNode['value']['upper'] == 1:
            return nodeToRegex(parentNode['value']['child'])
        elif parentNode['value']['lower'] == parentNode['value']['upper']:
            return nodeToRegex(parentNode['value']['child']) + '{' + str(parentNode['value']['lower']) + '}'
        elif parentNode['value']['lower'] == 0:
            return nodeToRegex(parentNode['value']['child']) + '{,' + str(parentNode['value']['upper']) + '}'
        elif parentNode['value']['upper'] == QuantSpecials.MAX_REPEAT:
            return nodeToRegex(parentNode['value']['child']) + '{' + str(parentNode['value']['lower']) + ',}'
        else:
            return nodeToRegex(parentNode['value']['child']) + '{' + str(parentNode['value']['lower']) + ',' + str(parentNode['value']['upper']) + '}'
    elif parentNode['type'] == NodeType.PATTERN:
        return parentNode['value']['regex']
    return ''

# Check if string matches a regex
def getMatchData(parentNode, string, pastPos = 0, preCalc = []):
    
    sub = ''
    match parentNode['type']:
        case NodeType.LIST:
            sub = 'L:'
        case NodeType.QUANT:
            sub = 'Q:'
        case NodeType.PATTERN:
            sub = 'P:'
    
    preCalcName = sub + nodeToRegex(parentNode)
    
    preCalcFiltered = list(filter(lambda x : x[0] == string[pastPos:] and x[1] == preCalcName, preCalc))
    
    if len(preCalcFiltered) > 0:
        return preCalcFiltered[0][2]
    
    # List node
    if parentNode['type'] == NodeType.LIST:
        # {
        #     'type' : NodeType.LIST,
        #     'value' : [],
        #     'node' : parentNode
        # }
        if parentNode['value']['type'] == ListType.NORMAL:
            firstMatch = getMatchData(parentNode['value']['children'][0], string, pastPos, preCalc)
            if firstMatch:
                currentMatches = [[i] for i in firstMatch]
            else:
                return None
            
            for child in parentNode['value']['children'][1:]:
                nextMatches = []
                
                if parentNode['parent'] == None:
                    print(0)
                
                for matchListIndex in reversed(range(len(currentMatches))):
                    changed = False
                    matchList = currentMatches[matchListIndex]
                    
                    match = matchList[-1]
                    matchData = getMatchData(child, string, match['endPos'], preCalc)
                    if parentNode['parent'] == None:
                        print(0)
                    if matchData:
                        for i in range(len(matchData)):
                            mdat = matchData[i]
                            if mdat:
                                changed = True
                                matchList.append(mdat)
                            else:
                                print(0)
                    
                    if not changed:
                        del currentMatches[matchListIndex]
                    # nextMatches += [[match + i] for i in getMatchData(child, string, match['endPos'], preCalc)]
                    
                # currentMatches = nextMatches
            
            if parentNode['parent'] == None:
                for i in reversed(range(len(currentMatches))):
                    if currentMatches[i][-1]['endPos'] != len(string):
                        del currentMatches[i]
            
            output = [{
                'type' : NodeType.LIST,
                'value' : i,
                'node' : parentNode,
                'endPos' : i[-1]['endPos'],
                'string' : ''.join([n['string'] for n in i])
            } for i in currentMatches]
            
            preCalc.append((string[pastPos:], preCalcName, output))
            
            return output
        else:
            output = []
            
            for node in parentNode['value']['children']:
                matchData = getMatchData(node, string, pastPos, preCalc)
                
                if matchData:
                    for match in matchData:
                        output.append({
                            'type' : NodeType.LIST,
                            'value' : [match],
                            'node' : parentNode,
                            'endPos' : match['endPos'],
                            'string' : match['string']
                        })
            
            return output

    # Match Quant nodes IF the match has the right length, also gets all possible matches
    elif parentNode['type'] == NodeType.QUANT:
        # Get all child matches
        if parentNode['value']['child']['type'] == NodeType.PATTERN:
            unfilteredList = getMatchData(parentNode['value']['child'], string, pastPos, preCalc)
            
            if unfilteredList:
                output = []
                
                for unfiltered in unfilteredList:
                    
                        if len(unfiltered['string']) >= parentNode['value']['lower'] and (parentNode['value']['upper'] == QuantSpecials.MAX_REPEAT or len(unfiltered['string']) <= parentNode['value']['upper']):
                            # Check the length of each match and add node about quant sizes
                            if parentNode['value']['upper'] == QuantSpecials.MAX_REPEAT:
                                output.append({
                                    'type' : NodeType.QUANT,
                                    'startPos' : pastPos,
                                    'range' : (parentNode['value']['lower'] + pastPos, len(string) - 1),
                                    'endPos' : pastPos + len(unfiltered['string']),
                                    'string' : unfiltered['string'],
                                    'children' : [unfiltered],
                                    'node' : parentNode
                                })
                            else:
                                output.append({
                                'type' : NodeType.QUANT,
                                'startPos' : pastPos,
                                'range' : (parentNode['value']['lower'] + pastPos, min(parentNode['value']['upper'] + pastPos, len(string) - 1)),
                                'endPos' : pastPos + len(unfiltered['string']),
                                'string' : unfiltered['string'],
                                'children' : [unfiltered],
                                'node' : parentNode
                            })
                
                preCalc.append((string[pastPos:], preCalcName, output))
                
                return output
        elif parentNode['value']['child']['type'] == NodeType.LIST:
            firstMatches = getMatchData(parentNode['value']['child'], string, pastPos, preCalc)
            matchLists = [[i] for i in firstMatches]
            
            if matchLists:
                iteration = 1
                while len(list(filter(lambda x : len(x) == iteration, matchLists))) > 0 and (parentNode['value']['upper'] == QuantSpecials.MAX_REPEAT or iteration < parentNode['value']['upper']):
                # while len(list(filter(lambda x : len(x) == iteration + 1, matchLists))) > 0:
                    nextMatchLists = []
                    for matchList in matchLists:
                        nextMatches = getMatchData(parentNode['value']['child'], string, matchList[-1]['endPos'], preCalc)
                        
                        if nextMatches:
                            for match in nextMatches:
                                nextMatchLists.append(matchList + [match])
                    
                    matchLists = nextMatchLists
                    iteration += 1
                
                nodes = [{
                    'type' : NodeType.QUANT,
                    'startPos' : pastPos,
                    'range' : (parentNode['value']['lower'] + pastPos, i[-1]['endPos']),
                    'endPos' : i[-1]['endPos'],
                    'string' : ''.join([s['string'] for s in i]),
                    'children' : i,
                    'node' : parentNode
                } for i in matchLists]
                
                preCalc.append((string[pastPos:], preCalcName, nodes))
                
                return nodes
        return None

    # Get all matches for current node
    elif parentNode['type'] == NodeType.PATTERN:
        cutString = string[pastPos:]
        rangeRegex = '{' + str(parentNode['parent']['value']['lower']) + ',' + ('' if parentNode['parent']['value']['upper'] == QuantSpecials.MAX_REPEAT else str(parentNode['parent']['value']['upper'])) + '}'
        # print(f"\A[{parentNode['value']['regex']}]{rangeRegex}")
        # if parentNode['value']['regex'][0] == '[' and parentNode['value']['regex'][-1] == ']':
        #     match = re.match(f"\A{parentNode['value']['regex']}{rangeRegex}", cutString)
        # else:
        #     match = re.match(f"\A[{parentNode['value']['regex']}]{rangeRegex}", cutString)
        match = re.match(f"\A{parentNode['value']['regex']}{rangeRegex}", cutString)
        
        if match:
            span = match.span()
            
            strings = []
            
            for index in range(parentNode['parent']['value']['lower'], span[1] + 1):
                strings.append(string[pastPos : index + pastPos])
            
            solutions = [{
                    'type' : NodeType.PATTERN,
                    'string' : string,
                    'node' : parentNode
                } for string in strings]
            
            preCalc.append((string[pastPos:], preCalcName, solutions))
            
            return solutions
        else:
            return None

def getUnitMatches(pattern, string, startIndex = 0):
    output = []

    # Get match blocks
    index = startIndex

    # From start go to final match length
    while index < len(string) and re.match(pattern, string[index]):
        index += 1
    
    if index == startIndex:
        return None
    else:
        #  Get all possible permutations given max length
        ranges = getOrderedPerms(startIndex, index - startIndex)
        for orderedTuple in ranges:
            chars = ''
            for c in orderedTuple:
                chars += str(string[c])
        
            output.append({
                'type' : NodeType.PATTERN,
                'startPos' : orderedTuple[0],
                'endPos' : orderedTuple[-1],
                'size' : orderedTuple[-1] - orderedTuple[0] + 1,
                'pattern' : pattern,
                'string' : chars
            })
        return output

def matchArray(stringArray, regexTree, preCalc = []):
    return [getMatchData(regexTree, i, preCalc=preCalc) for i in stringArray]

def simplifyRegexTree(regexTree):
    match regexTree['type']:
        case NodeType.LIST:
            old = nodeToRegex(regexTree)
            changed = False
            
            for index in reversed(range(len(regexTree['value']['children']))):
                if index + 1 < len(regexTree['value']['children']):
                    if ((regexTree['value']['children'][index]['type'] == NodeType.QUANT and regexTree['value']['children'][index + 1]['type'] == NodeType.QUANT) and (regexTree['value']['children'][index]['value']['child']['type'] == NodeType.PATTERN and regexTree['value']['children'][index + 1]['value']['child']['type'] == NodeType.PATTERN)) and nodeEqual(regexTree['value']['children'][index]['value']['child'], regexTree['value']['children'][index + 1]['value']['child']):
                        addRange = (regexTree['value']['children'][index + 1]['value']['lower'], regexTree['value']['children'][index + 1]['value']['upper'])
                        regexTree['value']['children'][index]['value']['lower'] += addRange[0]
                        if addRange[1] == QuantSpecials.MAX_REPEAT or regexTree['value']['children'][index]['value']['upper'] == QuantSpecials.MAX_REPEAT:
                            regexTree['value']['children'][index]['value']['upper'] = QuantSpecials.MAX_REPEAT
                        else:
                            regexTree['value']['children'][index]['value']['upper'] += addRange[1]
                        
                        del regexTree['value']['children'][index + 1]
                        changed = True
                    
                simplifyRegexTree(regexTree['value']['children'][index])
            
            if changed:
                for index in range(len(regexTree['value']['children'])):
                    regexTree['value']['children'][index]['path'][-1] = index
                
                print(f'old: {old}, new: {nodeToRegex(regexTree)}')
            
        case NodeType.QUANT:
            simplifyRegexTree(regexTree['value']['child'])

def nodeEqual(a, b):
    output = True
    
    if a['type'] != b['type']:
        return False
    
    match a['type']:
        case NodeType.PATTERN:
            return a['value']['type'] == b['value']['type'] and a['value']['value'] == b['value']['value']
        case _:
            print('EQUALITY ERROR')
    return a == b

def getTotalPath(node):
    path = []
    while node['parent'] != None:
        path = node['path'] + path
        node = node['parent']

    return path