from RegExtra.RegexTree.PatternNode.patternHelpers import patternToSet
from RegExtra.RegexTree.regexTree import getMatchData, NodeType, nodeToRegex, matchArray

# Search accept and reject trees with a method and create a list of 3 tuples (original node, accept node, reject node)
def getNodeTypes(acceptArray, rejectArray, getMethod):
    # Get all nodes 
    acceptNodes = []
    for i in acceptArray:
        for j in i:
            acceptNodes += getMethod(j)

    rejectNodes = []
    for i in rejectArray:
        for j in i:
            rejectNodes += getMethod(j)
    
    outputPairs = []

    # Go through filtered nodes and create tuples
    for node in acceptNodes:
        new = True

        for item in outputPairs:
            if item[0] == node['node']:
                item[1].append(node)
                new = False
        
        if new:
            outputPairs.append([node['node'], [node], []])
    
    for node in rejectNodes:
        new = True

        for item in outputPairs:
            if item[0] == node['node']:
                item[2].append(node)
                new = False
        
        if new:
            outputPairs.append([node['node'], [],  [node]])
    
    return outputPairs

# Get all Quantifiers from a set of accept and reject string matches, then modify them based on the process function
def transformQuantifiers(acceptStrings, rejectStrings, regexTree, processFunction):
    acceptArray = matchArray(acceptStrings, regexTree)
    rejectArray = matchArray(rejectStrings, regexTree)

    quants = getNodeTypes(acceptArray, rejectArray, getQuants)
    
    for quant in quants:
        acceptSet = [i['size'] for i in quant[1]]
        rejectSet = [i['size'] for i in quant[2]]
        newTuple = processFunction({
            'acceptSet' : acceptSet,
            'rejectSet' : rejectSet,
            'currentRange' : (quant[0]['value']['lower'], quant[0]['value']['upper'])
            })
        quant[0]['value']['lower'] = newTuple[0]
        quant[0]['value']['upper'] = newTuple[1]

# Get all Patterns from a set of accept and reject string matches, then modify them based on the process function
def transformPatterns(acceptStrings, rejectStrings, regexTree, processFunction):
    acceptArray = matchArray(acceptStrings, regexTree)
    rejectArray = matchArray(rejectStrings, regexTree)

    patterns = getNodeTypes(acceptArray, rejectArray, getPatterns)
    
    for pattern in patterns:
        acceptSet = [i['string'] for i in pattern[1]]
        rejectSet = [i['string'] for i in pattern[2]]
        newValue = processFunction({
            'acceptSet' : acceptSet,
            'rejectSet' : rejectSet,
            'currentSet' : patternToSet(pattern[0])
            })
        pattern[0]['value'] = newValue

# TODO: Get all pairings of nodes in lists, use a process function on them and add the result instead, allowing you to create conditions to merge them
def transformMerge(acceptStrings, rejectStrings, regexTree, processFunction):
    acceptArray = matchArray(acceptStrings, regexTree)
    rejectArray = matchArray(rejectStrings, regexTree)

    patterns = getNodeTypes(acceptArray, rejectArray, getPatterns)
    
    for pattern in patterns:
        acceptSet = [i['string'] for i in pattern[1]]
        rejectSet = [i['string'] for i in pattern[2]]
        newValue = processFunction({
            'acceptSet' : acceptSet,
            'rejectSet' : rejectSet,
            'currentSet' : patternToSet(pattern[0])
            })
        pattern[0]['value'] = newValue

# Gets all nodes in lists, run a process function on it that allows it to split the nodes
def transformSplit(acceptStrings, rejectStrings, regexTree, processFunction):
    acceptArray = matchArray(acceptStrings, regexTree)
    rejectArray = matchArray(rejectStrings, regexTree)

    lists = getNodeTypes(acceptArray, rejectArray, getLists)
    
    for list in lists:
        for index, item in reversed(list(enumerate(list[0]['children']))):
            if item['type'] == NodeType.QUANT:
                newQuants = processFunction({
                    'acceptValue' : list[1]['children'][index],
                    'rejectValue' : list[2]['children'][index],
                    'currentValue' : list[0]['children'][index],
                })
                list['children'][index] = newQuants
                list['children'].insert(index, newQuants)

def getLists(matchData):
    output = []
    if matchData['type'] == NodeType.LIST:
        output.append(matchData)
        for child in matchData['children']:
            output += getLists(child)
    elif matchData['type'] == NodeType.QUANT:
        output += getLists(matchData['child'])
    return output

def getQuants(matchData):
    output = []
    if matchData['type'] == NodeType.LIST:
        for child in matchData['children']:
            output += getQuants(child)
    elif matchData['type'] == NodeType.QUANT:
        output.append(matchData)
        output += getQuants(matchData['child'])
    return output

def getPatterns(matchData):
    output = []
    if matchData['type'] == NodeType.LIST:
        for child in matchData['children']:
            output += getPatterns(child)
    elif matchData['type'] == NodeType.QUANT:
        output += getPatterns(matchData['child'])
    elif matchData['type'] == NodeType.PATTERN:
        output.append(matchData)
    return output