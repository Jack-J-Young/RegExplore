from RegExtra.RegexTree.PatternNode.patternHelpers import patternToSet
from RegExtra.RegexTree.regexTree import changePathIndex, getMatchData, NodeType, nodeToRegex, matchArray
import copy

# Search accept and reject trees with a method and create a list of 3 tuples (original node, accept node, reject node)
def getNodeTypes(acceptArray, rejectArray, getMethod):
    # Get all nodes 
    acceptNodes = []
    for i in acceptArray:
        if i:
            for j in i:
                acceptNodes += getMethod(j)

    rejectNodes = []
    for i in rejectArray:
        if i:
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

# Get all Quantifiers from a set of accept and reject string matches, then get all possible permutations of quantifier changes based on the method processFunction
def transformQuantifierPermutations(acceptStrings, rejectStrings, regexTree, processFunction):

    # tranform all nodes
    acceptArray = matchArray(acceptStrings, regexTree)
    rejectArray = matchArray(rejectStrings, regexTree)

    quants = getNodeTypes(acceptArray, rejectArray, getQuants)
    
    modifiedLeaves = []
    for quant in quants:
        newQuant = processFunction({
            'acceptMatches' : quant[1],
            'rejectMatches' : quant[2],
            'currentNode' : quant[0]
        })
        
        modifiedLeaves.append(newQuant)

    # Copy tree and repleace correct node on each permutation
    output = []

    for leafSet in modifiedLeaves:
        for leaf in leafSet:
            if len(leaf['path']) > 0:
                currentRegexTree = copy.deepcopy(regexTree)

                currentNode = currentRegexTree

                for path in leaf['path'][:-1]:
                    currentNode = currentNode[path]
                    
                currentNode[leaf['path'][-1]] = leaf
            else:
                currentRegexTree = leaf

            output.append(currentRegexTree)

    return output

# Get all Patterns from a set of accept and reject string matches, then modify them based on the process function
def transformPatterns(acceptStrings, rejectStrings, regexTree, processFunction):
    acceptArray = matchArray(acceptStrings, regexTree)
    rejectArray = matchArray(rejectStrings, regexTree)

    patterns = getNodeTypes(acceptArray, rejectArray, getPatterns)
    
    for pattern in patterns:
        acceptSet = [i['string'] for i in pattern[1]]
        rejectSet = [i['string'] for i in pattern[2]]
        newValue = processFunction({
            'acceptMatches' : acceptSet,
            'rejectMatches' : rejectSet,
            'currentSet' : patternToSet(pattern[0])
        })
        pattern[0]['value'] = newValue

def transformPatternPermutations(acceptStrings, rejectStrings, regexTree, processFunction):

    acceptArray = matchArray(acceptStrings, regexTree)
    rejectArray = matchArray(rejectStrings, regexTree)

    patterns = getNodeTypes(acceptArray, rejectArray, getPatterns)
    
    modifiedLeaves = []
    for pattern in patterns:

        newPattern = processFunction({
            'acceptMatches' : pattern[1],
            'rejectMatches' : pattern[2],
            'currentNode' : pattern[0]
        })
        
        modifiedLeaves.append(newPattern)
    
    # Copy tree and repleace correct node on each permutation
    output = []

    for leafSet in modifiedLeaves:
        for leaf in leafSet:
            if len(leaf['path']) > 0:
                currentRegexTree = copy.deepcopy(regexTree)

                currentNode = currentRegexTree

                for path in leaf['path'][:-1]:
                    currentNode = currentNode[path]
                    
                currentNode[leaf['path'][-1]] = leaf
            else:
                currentRegexTree = leaf

            output.append(currentRegexTree)

    return output

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

# Gets all nodes in lists, run a process function on it that allows it to split the nodes
def transformSplitPermutations(acceptStrings, rejectStrings, regexTree, processFunction):
    acceptArray = matchArray(acceptStrings, regexTree)
    rejectArray = matchArray(rejectStrings, regexTree)

    lists = getNodeTypes(acceptArray, rejectArray, getLists)
    
    modifiedLeaves = []
    for list in lists:
        # for index, item in reversed(list(enumerate(list[0]['children']))):
        for index in reversed(range(len(list[0]['value']))):
            if list[0]['value'][index]['type'] == NodeType.QUANT:
                newNodes = processFunction({
                    # 'acceptMatches' : list[1][forall]['children'][index],
                    'acceptMatches' : [match['children'][index] for match in list[1]],
                    'rejectMatches' : [match['children'][index] for match in list[2]],
                    'currentNode' : list[0]['value'][index],
                })

                modifiedLeaves.append((list[0]['value'][index]['path'], newNodes))

    # Copy tree and repleace correct node on each permutation
    output = []

    for leafSet in modifiedLeaves:
        for leaf in leafSet[1]:
            if len(leafSet[0]) > 0:
                currentRegexTree = copy.deepcopy(regexTree)

                currentNode = currentRegexTree
                for path in leafSet[0][:-2]:
                    currentNode = currentNode[path]
                
                currentNode['value'][leafSet[0][-1]] = leaf[-1]
                for node in leaf[:-1]:
                    currentNode['value'].insert(leafSet[0][-1], node)
                
                for index in range(len(currentNode['value'])):
                    changePathIndex(currentNode['value'][index], len(currentNode['path']) + 1, index)

                output.append(currentRegexTree)
            else:
                newParent = {
                    'type' : NodeType.LIST,
                    'value' : leaf,
                    'path' : []
                }

                for index in range(len(newParent['value'])):
                    newParent['value'][index]['path'] = ['value', index]
                
                output.append(newParent)

    return output

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