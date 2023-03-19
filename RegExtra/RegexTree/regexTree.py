import copy
import sre_parse
import re
from RegExtra.RegexTree.PatternNode.createPatternNode import createPatternNode
from RegExtra.RegexTree.PatternNode.PatternEnums import CategoryType, PatternType
from RegExtra.RegexTree.QuantNode.QuantEnums import QuantSpecials
from RegExtra.RegexTree.QuantNode.createQuantNode import createQuantNode
from RegExtra.RegexTree.nodeEnums import NodeType
from RegExtra.solveHelpers import getOrderedPerms
import json

# Turns ast into regex tree object
def regexToNode(rawData, parent = None, path = []): 

    node = {
        'type' : NodeType.UNKOWN,
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
                'value' : None,
                'parent' : parent,
                'path' : path
            }
            
            node['value'] = [regexToNode(rawData.data[subDataIndex], node, ['value', subDataIndex]) for subDataIndex in range(len(rawData.data))]
            
            for childIndex in range(len(node['value'])):
                if node['value'][childIndex]['type'] == NodeType.PATTERN:
                    node['value'][childIndex] = {
                        'type': NodeType.QUANT,
                        'value' : {
                            'lower' : 1,
                            'upper' : 1,
                            'child' : node['value'][childIndex]
                        },
                        'parent' : node,
                        'path' : node['value'][childIndex]['path']
                    }
                    
                    node['value'][childIndex]['value']['child']['parent'] = node['value'][childIndex]
                    node['value'][childIndex]['value']['child']['path'] = ['value', 'child']


    elif isinstance(rawData, tuple):
        #  Quant nodes
        if rawData[0] == sre_parse.MAX_REPEAT:
            node = createQuantNode(rawData[1], parent, path)
            node['value']['child'] = regexToNode(rawData[1][2], node, ['value', 'child'])

        elif rawData[0] == sre_parse.SUBPATTERN:
            node = {
                'type' : NodeType.LIST,
                'value' : None,
                'parent' : parent,
                'path' : path
            }
            node['value'] = [regexToNode(rawData.data[subDataIndex], node, ['value', subDataIndex]) for subDataIndex in range(len(rawData.data))]
            
            for childIndex in range(len(node['value'])):
                if node['value'][childIndex]['type'] == NodeType.PATTERN:
                    node['value'][childIndex] = {
                        'type': NodeType.QUANT,
                        'value' : {
                            'lower' : 1,
                            'upper' : 1,
                            'child' : node['value'][childIndex]
                        },
                        'parent' : node,
                        'path' : node['value'][childIndex]['path']
                    }
                    
                    node['value'][childIndex]['value']['child']['parent'] = node['value'][childIndex]
                    node['value'][childIndex]['value']['child']['path'] = ['value', 'child']

        # Pattern: Literal
        elif rawData[0] == sre_parse.LITERAL:
            node['type'] = NodeType.PATTERN
            node['value'] = {
                'type' : PatternType.LITERAL,
                'value' : chr(rawData[1]),
                'regex' : chr(rawData[1]) + ""
            } 

        # Pattern: everything else
        elif rawData[0] == sre_parse.IN:
            node = createPatternNode(rawData[1], parent, path)
        
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
        return '(' + ''.join([nodeToRegex(i) for i in parentNode['value']]) + ')'
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

        firstMatch = getMatchData(parentNode['value'][0], string, pastPos, preCalc)
        if firstMatch:
            currentMatches = [[i] for i in firstMatch]
        else:
            return None
        
        for child in parentNode['value'][1:]:
            nextMatches = []
            
            for matchListIndex in reversed(range(len(currentMatches))):
                changed = False
                matchList = currentMatches[matchListIndex]
                
                match = matchList[-1]
                matchData = getMatchData(child, string, match['endPos'], preCalc)
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
        
        for i in reversed(range(len(currentMatches))):
            if currentMatches[i][-1]['endPos'] != len(string):
                del currentMatches[i]
        
        output = [{
            'type' : NodeType.LIST,
            'value' : i,
            'node' : parentNode
        } for i in currentMatches]
        
        preCalc.append((string[pastPos:], preCalcName, output))
        
        return output
            
        # output = getMatchData(parentNode['value'][0], string, pastPos, preCalc)
        
        # for child in parentNode['value'][1:]:
        #     if not output:
        #         return None
        #     if len(output) == 0:
        #         return None
            
        #     positions = dict()
        #     for data in output:
        #         pos = []
        #         if data['range'][0] == data['range'][1]:
        #             pos.append(data['range'][0])
        #         pos += range(data['range'][0], data['range'][1] + 1)
                
        #         for p in pos:
        #             if p in positions:
        #                 positions[p].append(data)
        #             else:
        #                 positions[p] = [data]

        #     nextOutput = []
            
        #     t = []
        #     for i in positions:
        #         md = getMatchData(child, string, i, preCalc)
        #         if md:
        #             for d in md:
        #                 d['previous'] = positions[i]
        #             t.append(md)
            
        #     #for matches in [getMatchData(child, string, i) for i in positions]:
        #     for matches in t:
        #         nextOutput += matches
            
        #     output = nextOutput
        
        # if output == None or len(output) == 0:
        #     return None
        # else:
        #     temp = [[i] for i in output]
        #     while 'previous' in temp[0][0]:
        #         new = []
                
        #         for obj in temp:
        #             for node in obj[0]['previous']:
        #                 new.append([node] + obj)
                
        #         temp = new
            
        #     for set in temp:
        #         for index in range(len(set)):
        #             node = set[index]
                    
        #             if index >= len(set):
        #                 if node['child']['type'] == NodeType.PATTERN:
        #                     node['child']['strings'] = list(filter(lambda x : len(x) == set[index + 1]['startPos'] - set[index]['startPos'], node['child']['strings']))
        #             else:
        #                 if node['child']['type'] == NodeType.PATTERN:
        #                     node['child']['strings'] = list(filter(lambda x : len(x) == len(string) - 1 - set[index]['startPos'], node['child']['strings']))
            
        #     solutions = [{
        #         'type' : NodeType.LIST,
        #         'value' : i,
        #         'node' : parentNode
        #     } for i in temp]
            
        #     preCalc.append((string[pastPos:], preCalcName, solutions))
            
        #     return solutions

    # Match Quant nodes IF the match has the right length, also gets all possible matches
    elif parentNode['type'] == NodeType.QUANT:
        # Get all child matches
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
                            'child' : unfiltered,
                            'node' : parentNode
                        })
                    else:
                        output.append({
                        'type' : NodeType.QUANT,
                        'startPos' : pastPos,
                        'range' : (parentNode['value']['lower'] + pastPos, min(parentNode['value']['upper'] + pastPos, len(string) - 1)),
                        'endPos' : pastPos + len(unfiltered['string']),
                        'child' : unfiltered,
                        'node' : parentNode
                    })
            
            preCalc.append((string[pastPos:], preCalcName, output))
            
            return output
        return None

    # Get all matches for current node
    elif parentNode['type'] == NodeType.PATTERN:
        cutString = string[pastPos:]
        rangeRegex = '{' + str(parentNode['parent']['value']['lower']) + ',' + ('' if parentNode['parent']['value']['upper'] == QuantSpecials.MAX_REPEAT else str(parentNode['parent']['value']['upper'])) + '}'
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
            
            for index in reversed(range(len(regexTree['value']))):
                if index + 1 < len(regexTree['value']):
                    if ((regexTree['value'][index]['type'] == NodeType.QUANT and regexTree['value'][index + 1]['type'] == NodeType.QUANT) and (regexTree['value'][index]['value']['child']['type'] == NodeType.PATTERN and regexTree['value'][index + 1]['value']['child']['type'] == NodeType.PATTERN)) and nodeEqual(regexTree['value'][index]['value']['child'], regexTree['value'][index + 1]['value']['child']):
                        addRange = (regexTree['value'][index + 1]['value']['lower'], regexTree['value'][index + 1]['value']['upper'])
                        regexTree['value'][index]['value']['lower'] += addRange[0]
                        if addRange[1] == QuantSpecials.MAX_REPEAT or regexTree['value'][index]['value']['upper'] == QuantSpecials.MAX_REPEAT:
                            regexTree['value'][index]['value']['upper'] = QuantSpecials.MAX_REPEAT
                        else:
                            regexTree['value'][index]['value']['upper'] += addRange[1]
                        
                        del regexTree['value'][index + 1]
                        changed = True
                    
                simplifyRegexTree(regexTree['value'][index])
            
            if changed:
                for index in range(len(regexTree['value'])):
                    regexTree['value'][index]['path'][-1] = index
                
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