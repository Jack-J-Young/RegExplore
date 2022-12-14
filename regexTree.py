import sre_parse
import re
from solveHelpers import getOrderedPerms
import json

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

def toNode(rawData): 

    node = regexNode()

    if isinstance(rawData, sre_parse.SubPattern):
        if len(rawData.data) == 1:
            node = toNode(rawData.data[0])
        else:
            node = listNode()

            for subData in rawData.data:
                node.appendChild(toNode(subData))

    elif isinstance(rawData, tuple):
        if rawData[0] == sre_parse.MAX_REPEAT:
            repeatData = rawData[1]
            node = quantNode(repeatData[0], repeatData[1], toNode(repeatData[2]))

        elif rawData[0] == sre_parse.SUBPATTERN:
            node = listNode()

            for subData in rawData[1][3]:
                node.appendChild(toNode(subData))

        elif rawData[0] == sre_parse.LITERAL:
            node = patternNode(chr(rawData[1]) + "")

        elif rawData[0] == sre_parse.IN:
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
                    print(rawData)
            
            node = patternNode(value)

        else:
            print(rawData)

    return node