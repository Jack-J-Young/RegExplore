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
def getMatchData(parentNode, string, pastPos = 0):
    # List node
    if parentNode['type'] == NodeType.LIST:
        # {
        #     'type' : NodeType.LIST,
        #     'value' : [],
        #     'node' : parentNode
        # }
        output = getMatchData(parentNode['value'][0], string, pastPos)

        for child in parentNode['value'][1:]:
            if len(output) == 0:
                return None
            
            positions = []
            for data in output:
                if data['range'][0] == data['range'][1]:
                    positions.append(data['range'][0])
                positions += range(data['range'][0], data['range'][1])
                
            positions = list(dict.fromkeys(positions))

            nextOutput = []
            for matches in [getMatchData(child, string, i) for i in positions]:
                if matches:
                    nextOutput += matches
            
            output = nextOutput
    
        return output

    # Match Quant nodes IF the match has the right length, also gets all possible matches
    elif parentNode['type'] == NodeType.QUANT:
        # Get all child matches
        unfilteredList = getMatchData(parentNode['value']['child'], string, pastPos)
        
        if unfilteredList:
            output = []
            
            for unfiltered in unfilteredList:  
                # Check the length of each match and add node about quant sizes
                if parentNode['value']['upper'] == QuantSpecials.MAX_REPEAT:
                    output.append({
                        'type' : NodeType.QUANT,
                        'range' : (parentNode['value']['lower'] + pastPos, len(string) - 1),
                        'child' : unfiltered,
                        'node' : parentNode
                    })
                else:
                    output.append({
                    'type' : NodeType.QUANT,
                    'range' : (parentNode['value']['lower'] + pastPos, min(parentNode['value']['upper'] + pastPos, len(string) - 1)),
                    'child' : unfiltered,
                    'node' : parentNode
                })
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
            
            if parentNode['parent']['value']['lower'] == 0:
                strings = ['']
            for index in range(span[1] - span[0]):
                strings.append(string[span[0] + pastPos : index + span[0] + pastPos + 1])
            
            return [{
                    'type' : NodeType.PATTERN,
                    'strings' : strings,
                    'node' : parentNode
                }]
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

def matchArray(stringArray, regexTree):
    return [getMatchData(regexTree, i) for i in stringArray]

def getTotalPath(node):
    path = []
    while node['parent'] != None:
        path = node['path'] + path
        node = node['parent']

    return path