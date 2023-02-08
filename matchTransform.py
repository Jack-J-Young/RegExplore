from regexTree import getMatchData, NodeType, nodeToRegex, matchArray

def getNodeTypes(acceptArray, rejectArray, getMethod):
    acceptNodes = []
    for i in acceptArray:
        for j in i:
            acceptNodes += getMethod(j)

    rejectNodes = []
    for i in rejectArray:
        for j in i:
            rejectNodes += getMethod(j)
    
    outputPairs = []
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

def transformQuantifiers(acceptStrings, rejectStrings, regexTree, processFunction):
    acceptArray = matchArray(acceptStrings, regexTree)
    rejectArray = matchArray(rejectStrings, regexTree)

    quants = getNodeTypes(acceptArray, rejectArray, getQuants)
    
    for quant in quants:
        acceptSet = [i['size'] for i in quant[1]]
        rejectSet = [i['size'] for i in quant[2]]
        newTuple = processFunction(acceptSet, rejectSet)
        quant[0]['value']['lower'] = newTuple[0]
        quant[0]['value']['upper'] = newTuple[1]

def getQuants(matchData):
    output = []
    if matchData['type'] == NodeType.LIST:
        for child in matchData['children']:
            output += getQuants(child)
    elif matchData['type'] == NodeType.QUANT:
        output.append(matchData)
        output += getQuants(matchData['child'])
    return output