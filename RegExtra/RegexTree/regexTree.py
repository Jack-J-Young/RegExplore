import sre_parse
import re
from RegExtra.RegexTree.PatternNode.createPatternNode import createPatternNode
from RegExtra.RegexTree.PatternNode.enums import CategoryType, PatternType
from RegExtra.RegexTree.QuantNode.createQuantNode import createQuantNode
from RegExtra.RegexTree.nodeEnums import NodeType
from solveHelpers import getOrderedPerms
import json

def regexToNode(rawData): 

    node = {
        'type' : NodeType.UNKOWN,
        'value' : None
    }

    if isinstance(rawData, sre_parse.SubPattern):
        if len(rawData.data) == 1:
            node = regexToNode(rawData.data[0])
        else:
            node = {
                'type' : NodeType.LIST,
                'value' : [regexToNode(subData) for subData in rawData.data]
            }

    elif isinstance(rawData, tuple):
        if rawData[0] == sre_parse.MAX_REPEAT:
            node = createQuantNode(rawData[1], regexToNode(rawData[1][2]))

        elif rawData[0] == sre_parse.SUBPATTERN:
            node = {
                'type' : NodeType.LIST,
                'value' : [regexToNode(subData) for subData in rawData.data]
            }

        elif rawData[0] == sre_parse.LITERAL:
            node['type'] = NodeType.PATTERN
            node['value'] = {
                'type' : PatternType.LITERAL,
                'value' : chr(rawData[1]),
                'regex' : chr(rawData[1]) + ""
            }

        elif rawData[0] == sre_parse.IN:
            node = createPatternNode(rawData[1])

        else:
            node['type'] = NodeType.UNKOWN
            node['value'] = None

    return node

def nodeToRegex(parentNode):
    if parentNode['type'] == NodeType.LIST:
        return '(' + ''.join([nodeToRegex(i) for i in parentNode['value']]) + ')'
    elif parentNode['type'] == NodeType.QUANT:
        if parentNode['value']['lower'] == 0 and parentNode['value']['upper'] == sre_parse.MAXREPEAT:
            return nodeToRegex(parentNode['value']['child']) + '*'
        elif parentNode['value']['lower'] == 1 and parentNode['value']['upper'] == sre_parse.MAXREPEAT:
            return nodeToRegex(parentNode['value']['child']) + '+'
        elif parentNode['value']['lower'] == 0 and parentNode['value']['upper'] == 1:
            return nodeToRegex(parentNode['value']['child']) + '?'
        elif parentNode['value']['lower'] == 0 and parentNode['value']['upper'] == 0:
            return nodeToRegex(parentNode['value']['child'])
        elif parentNode['value']['lower'] == parentNode['value']['upper']:
            return nodeToRegex(parentNode['value']['child']) + '{' + str(parentNode['value']['lower']) + '}'
        elif parentNode['value']['lower'] == 0:
            return nodeToRegex(parentNode['value']['child']) + '{,' + str(parentNode['value']['upper']) + '}'
        elif parentNode['value']['upper'] == sre_parse.MAXREPEAT:
            return nodeToRegex(parentNode['value']['child']) + '{' + str(parentNode['value']['lower']) + ',}'
        else:
            return nodeToRegex(parentNode['value']['child']) + '{' + str(parentNode['value']['lower']) + ',' + str(parentNode['value']['upper']) + '}'
    elif parentNode['type'] == NodeType.PATTERN:
        return parentNode['value']['regex']
    return ''

def getMatchData(parentNode, string, pastPos = 0):
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
        
        for data in output:
            for child in data['children']:
                data['string'] += child['string']
    
        return output


        # for childNode in parentNode['value']:
        #     matches = getMatchData(childNode, string, pastData)
        #     output = [{
        #         'type' : NodeType.LIST,
        #         'startPos' : i['startPos'],
        #         'endPos' : i['endPos'],
        #         'size' : i['endPos'] - i['startPos'] + 1,
        #         'children' : [i]
        #     } for i in matches]
        

    elif parentNode['type'] == NodeType.QUANT:
        unfiltered = getMatchData(parentNode['value']['child'], string, pastPos)

        if unfiltered:
            output = []

            for matchData in unfiltered:
                size = matchData['endPos'] - matchData['startPos'] + 1
                if (size >= parentNode['value']['lower']) and ((parentNode['value']['upper'] == sre_parse.MAX_REPEAT) or (size <= parentNode['value']['upper'])):
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

    # print(index)
    # print(len(input))
    # print(self.char)
    # print(input[index])
    # print(True if index < len(input) else False)
    # print(True if re.match(self.char, input[index]) else False)
    # print(True if index < len(input) and re.match(self.char, input[index]) else False)

    while index < len(string) and re.match(pattern, string[index]):
        index += 1
    
    if index == startIndex:
        return None
    else:
        ranges = getOrderedPerms(startIndex, index - startIndex)
        for orderedTuple in ranges:
            chars = ''
            for c in orderedTuple:
                chars += str(string[c])
            # output.append((orderedTuple[0], orderedTuple[-1], chars))
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