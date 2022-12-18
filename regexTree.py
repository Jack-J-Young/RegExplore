import sre_parse
import re
from solveHelpers import getOrderedPerms
import json
from enum import Enum

class NodeType(Enum):
    UNKOWN = -1
    LIST = 0
    QUANT = 1
    PATTERN = 2

# MATCH DATA JSON
# {
#     startPos: int,
#     endPos: int,
#     regex: string,
#     string: string,
#     previousData: [
#         {
#             another match data
#         }
#     ]
# }

# DEFAULT_ANCHOR = {
#     'startPos': 0,
#     'endPos':
# }

class regexNode:
    def getName(self):
        return ''

    def getMatches(self, input, pastMatchData = None):
        return pastMatchData

class listNode(regexNode):
    def __init__(self):
        self.children = []
    
    def appendChild(self, node):
        self.children.append(node)

    def getName(self):
        name = '('
        for subData in self.children:
            name += subData.getName()
        return name + ')'

    def getMatches(self, input, pastMatchData = None):
        lastMatchData = pastMatchData
        for child in self.children:
            matchData = child.getMatches(input, lastMatchData)
            if matchData:
                lastMatchData = matchData
            else:
                return None
        return lastMatchData

class quantNode(regexNode):
    # Range, a-b, i = sre_parse.MAXREPEAT

    def __init__(self, lower, upper, childNode):
        self.lower = lower
        self.upper = upper
        self.childNode = childNode

    def getName(self):
        if self.lower == 0 and self.upper == sre_parse.MAXREPEAT:
            return f'{self.childNode.getName()}*'
        elif self.lower == 1 and self.upper == sre_parse.MAXREPEAT:
            return f'{self.childNode.getName()}+'
        elif self.lower == 0 and self.upper == 1:
            return f'{self.childNode.getName()}?'
        elif self.upper == sre_parse.MAXREPEAT:
            return f'{self.childNode.getName()}{{{self.lower},}}'
        else:
            return f'{self.childNode.getName()}{{{self.lower},{self.upper}}}'

    def getMatches(self, input, pastMatchData = None):
        outputMatchData = []
        # Get matches form child
        matchData = self.childNode.getMatches(input, pastMatchData)
        if matchData:
            for i in range(len(matchData)):
                currentData = matchData[i]
                # Get size of match
                matchSize = currentData["endPos"] - currentData["startPos"] + 1
                if matchSize >= self.lower and ((self.upper == sre_parse.MAXREPEAT) or (matchSize <= self.upper)):
                    # Valid match size
                    outputMatchData.append(currentData)
            return None if len(outputMatchData) == 0 else outputMatchData
        else:
            return None

class patternNode(regexNode):
    def __init__(self, char):
        self.char = char

    def getName(self):
        return self.char

    def getMatches(self, input, pastMatchData = None):
        if pastMatchData == None:
            # If theres no anchor, start from 0
            # TODO: if starting from 0 or anywhere match, LOOK INTO STARTING CHAR ALSO
            matchData = self.getMatchesFromIndex(input, 0)

            return matchData
        else:
            outputMatchData = []

            # Starting from each anchor
            for anchor in pastMatchData:
                matchData = self.getMatchesFromIndex(input, anchor['endPos'] + 1)
                # If failed to match
                if matchData:
                    for currentData in matchData:

                        # Add previous match data and append
                        currentData['previousData'] = anchor['previousData']
                        # if len(currentData['previousData']) > 0:
                        #     currentData['previousData'] = anchor['previousData']
                        # currentData['previousData'].append(anchor)

                        outputMatchData.append(currentData)
                    return outputMatchData
                else:
                    return None

    def getMatchesFromIndex(self, input, startIndex):
        output = []

        # Get match blocks
        index = startIndex
        matchRanges = []

        print(index)
        print(len(input))
        print(self.char)
        print(input[index])
        print(True if index < len(input) else False)
        print(True if re.match(self.char, input[index]) else False)
        print(True if index < len(input) and re.match(self.char, input[index]) else False)

        while index < len(input) and re.match(self.char, input[index]):
            index += 1
        
        if index == startIndex:
            return None
        else:
            ranges = getOrderedPerms(startIndex, index - startIndex)
            for orderedTuple in ranges:
                chars = ''
                for c in orderedTuple:
                    chars += str(input[c])
                # output.append((orderedTuple[0], orderedTuple[-1], chars))
                output.append({
                    'startPos': orderedTuple[0],
                    'endPos': orderedTuple[-1],
                    'regex': self.char,
                    'string': chars,
                    'previousData': None
                })
            return output





        # for offsetI in range(len(input) - index):
        #     i = offsetI + index
        #     if re.match(self.char, input[i]):
        #         if startPos == -1:
        #             startPos = i
        #     elif startPos != -1:
        #         matchRanges.append((startPos, i))
        #         startPos = -1

        # # Get all matches from blocks
        # for matchRange in matchRanges:
        #     ranges = getOrderedPerms(matchRange[0], matchRange[1] - matchRange[0])
        #     for orderedTuple in ranges:
        #         chars = ''
        #         for c in orderedTuple:
        #             chars += str(input[c])
        #         output.append((orderedTuple[0], orderedTuple[-1], chars))
        #         output.append({
        #             'startPos': index,
        #             'endPos': ,
        #             'regex': self.char,
        #             'string': 'idkyet',
        #             'previousData': []
        #         })

        # return 

def regexToNode(rawData): 

    node = {
        'type' : NodeType.UNKOWN,
        'value' : None
    }

    if isinstance(rawData, sre_parse.SubPattern):
        if len(rawData.data) == 1:
            node = regexToNode(rawData.data[0])
        else:
            node['type'] = NodeType.LIST
            node['value'] = []

            for subData in rawData.data:
                node['value'].append(regexToNode(subData))

    elif isinstance(rawData, tuple):
        if rawData[0] == sre_parse.MAX_REPEAT:
            repeatData = rawData[1]
            node['type'] = NodeType.QUANT
            node['value'] = {
                'lower' : repeatData[0],
                'upper' : repeatData[1],
                'child' : regexToNode(repeatData[2])
            }

        elif rawData[0] == sre_parse.SUBPATTERN:
            node['type'] = NodeType.LIST
            node['value'] = []

            for subData in rawData[1][3]:
                node['value'].append(regexToNode(subData))

        elif rawData[0] == sre_parse.LITERAL:
            node['type'] = NodeType.PATTERN
            node['value'] = chr(rawData[1]) + ""

        elif rawData[0] == sre_parse.IN:
            node['type'] = NodeType.PATTERN
            value = ''

            for charData in rawData[1]:
                if charData[0] == sre_parse.CATEGORY:
                    if charData[1] == sre_parse.CATEGORY_DIGIT:
                        value += r'\d'
                    elif charData[1] == sre_parse.CATEGORY_WORD:
                        value += r'\w'
                elif charData[0] == sre_parse.RANGE:
                    value += f'[{chr(charData[1][0])}-{chr(charData[1][1])}]'
                else:
                    node['type'] = NodeType.UNKOWN
                    node['value'] = None
                    return node
            
            node['value'] = value

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
        return parentNode['value']
    return ''

def getMatchData(parentNode, string, pastPos = 0):
    if parentNode['type'] == NodeType.LIST:
        output = [{
            'type' : NodeType.LIST,
            'startPos' : -1,
            'endPos' : -1,
            'size' : 0,
            'string' : '',
            'children' : []
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
                        'children' : data['children'] + [i]
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
                'child' : i
            } for i in output]

    elif parentNode['type'] == NodeType.PATTERN:
        return getUnitMatches(parentNode['value'], string, pastPos)
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