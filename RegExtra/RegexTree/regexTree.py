import sre_parse
import re
from RegExtra.RegexTree.PatternNode.createPatternNode import createPatternNode
from RegExtra.RegexTree.PatternNode.PatternEnums import CategoryType, PatternType
from RegExtra.RegexTree.QuantNode.QuantEnums import QuantSpecials
from RegExtra.RegexTree.QuantNode.createQuantNode import createQuantNode
from RegExtra.RegexTree.nodeEnums import NodeType
from solveHelpers import getOrderedPerms
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
        elif parentNode['value']['lower'] == 0 and parentNode['value']['upper'] == 0:
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
def getMatchData(parentNode, string, pastPos = 0):

    # List node
    if parentNode['type'] == NodeType.LIST:
        output = [{
            'type' : NodeType.LIST,
            'startPos' : -1,
            'endPos' : -1,
            'size' : 0,
            'string' : '',
            'children' : [],
            'node' : parentNode
        }]

        for child in parentNode['value']:
            if len(output) == 0:
                return None

            nextOutput = []
            for data in output:
                # Get match for child nodes and move the stored positions
                matchData = getMatchData(child, string, data['endPos'] + 1)
                if matchData:
                    nextOutput += [{
                        'type' : NodeType.LIST,
                        'startPos' : i['startPos'],
                        'endPos' : i['endPos'],
                        'size' : i['endPos'] - data['startPos'] + 1,
                        'string' : '',
                        'children' : data['children'] + [i],
                        'node' : parentNode
                    } for i in matchData]
            
            output = nextOutput
        
        # Create current matched string
        for data in output:
            for child in data['children']:
                data['string'] += child['string']
    
        return output

    # Match Quant nodes IF the match has the right length, also gets all possible matches
    elif parentNode['type'] == NodeType.QUANT:
        # Get all child matches
        unfiltered = getMatchData(parentNode['value']['child'], string, pastPos)

        # Check the length of each match and add node about quant sizes
        if unfiltered:
            output = []

            for matchData in unfiltered:
                size = matchData['endPos'] - matchData['startPos'] + 1
                if (size >= parentNode['value']['lower']) and ((parentNode['value']['upper'] == QuantSpecials.MAX_REPEAT) or (size <= parentNode['value']['upper'])):
                    output.append(matchData)
            
            return [{
                'type' : NodeType.QUANT,
                'startPos' : i['startPos'],
                'endPos' : i['endPos'],
                'size' : i['size'],
                'string' : i['string'],
                'child' : i,
                'node' : parentNode
            } for i in output]

    # Get all matches for current node
    elif parentNode['type'] == NodeType.PATTERN:
        output = []
        matches = getUnitMatches(parentNode['value']['regex'], string, pastPos)
        if matches:
            for i in matches:
                i.update({'node' : parentNode})
                output.append(i)
            return output
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
        #  Get all posible permutations given max length
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

def matchArray(stringArray, regexTree):
    dataArray = [getMatchData(regexTree, i) for i in stringArray]
    return dataArray

def getTotalPath(node):
    path = []
    while node['parent'] != None:
        path = node['path'] + path
        node = node['parent']

    return path