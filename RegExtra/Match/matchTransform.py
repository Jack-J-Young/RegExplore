from RegExtra.RegexTree.regexTree import NodeType, matchArray
import copy

# Search accept and reject trees and create a list of 4 tuples (original node, accept node, reject node, node path)
def getNodeCollections(acceptArray, rejectArray):
    # Get all nodes

    acceptNodes = []
    for i in acceptArray:
        if i:
            for j in i:
                acceptNodes += getAll(j)

    rejectNodes = []
    for i in rejectArray:
        if i:
            for j in i:
                rejectNodes += getAll(j)
    
    # outputPairs = []
    outputDict = dict()

    # Go through filtered nodes and create tuples
    for node in acceptNodes:
        key = str(id(node['node']))
        
        if key in outputDict:
            outputDict[key][1].append(node)
        else:
            outputDict[key] = [node['node'], [node], []]
    
    for node in rejectNodes:
        key = str(id(node['node']))
        
        if key in outputDict:
            outputDict[key][2].append(node)
        else:
            outputDict[key] = [node['node'], [], [node]]
    
    return [outputDict[key] for key in outputDict]

# def getCollectionPaths(collections):
#     for collection in collections:
#         collection.append(getPath(collection[0]))

def replaceStep(nodeCollections, replaceFunction):
    output = []
    for nodeCollection in nodeCollections:
        newNodes = replaceFunction({
            'acceptMatches' : nodeCollection[1],
            'rejectMatches' : nodeCollection[2],
            'currentNode' : nodeCollection[0],
        })

        for newNode in newNodes:
            root = newNode
            while root['parent'] != None:
                root = root['parent']

            output.append(root)
    
    return output

def insertStep(nodeCollections, insertFunction):
    output = []
    for nodeCollection in nodeCollections:
        newNodeTuples = insertFunction({
            'acceptMatches' : nodeCollection[1],
            'rejectMatches' : nodeCollection[2],
            'currentNode' : nodeCollection[0],
        })

        for newNodeTuple in newNodeTuples:
            newNode = copy.deepcopy(nodeCollection[0])
            newNode['value'].insert(newNodeTuple[0], newNodeTuple[1])

            newNodeTuple['parent'] = newNode
            newNodeTuple['path'] = ['value', 0]

            for index in range(len(newNode['value'])):
                newNode['value'][index]['path'][-1] = index

            root = newNode
            while root['parent'] != None:
                root = root['parent']

            output.append(root)
    
    return output

def deleteStep(nodeCollections, replaceFunction):
    output = []
    for nodeCollection in nodeCollections:
        removeIndices = replaceFunction({
            'acceptMatches' : nodeCollection[1],
            'rejectMatches' : nodeCollection[2],
            'currentNode' : nodeCollection[0],
        })

        for removeIndex in removeIndices:
            newNode = copy.deepcopy(nodeCollection[0])
            
            del newNode['value'][removeIndex]

            for index in range(len(newNode['value'])):
                newNode['value'][index]['path'][-1] = index

            root = newNode
            while root['parent'] != None:
                root = root['parent']

            output.append(root)
    
    return output

# Replaces one pattern in tree with result of processFunction, does this for all patterns and creates tree copy
def replacePatternPermutations(nodeCollections, regexTree, processFunction):
    nodeCollections = filter(lambda t: t[0]['type'] == NodeType.PATTERN, nodeCollections)
    
    output = []
    for nodeData in nodeCollections:
        newNodes = processFunction({
            'acceptMatches' : nodeData[1],
            'rejectMatches' : nodeData[2],
            'currentNode' : nodeData[0],
        })

        for newNode in newNodes:
            permRegex = copy.deepcopy(regexTree)

            # path = nodeData[3]
            path = getPath(nodeData[0])
            preNode = permRegex
            while len(path) > 1:
                preNode = preNode[path[0]]
                del path[0]
            
            preNode[path[0]] = newNode
            output.append(permRegex)
    
    return output

# Replaces one quantfier in tree with result of processFunction, does this for all patterns and creates tree copy
def replaceQuantifierPermutations(nodeCollections, regexTree, processFunction):
    nodeCollections = filter(lambda t: t[0]['type'] == NodeType.QUANT, nodeCollections)
    
    output = []
    for nodeData in nodeCollections:
        newNodes = processFunction({
            'acceptMatches' : nodeData[1],
            'rejectMatches' : nodeData[2],
            'currentNode' : nodeData[0],
        })

        for newNode in newNodes:
            permRegex = copy.deepcopy(regexTree)

            # path = nodeData[3]
            path = getPath(nodeData[0])
            preNode = permRegex
            while len(path) > 1:
                preNode = preNode[path[0]]
                del path[0]
            
            preNode[path[0]] = newNode
            output.append(permRegex)
    
    return output

def insertListPermutations(acceptStrings, rejectStrings, regexTree, generateFunction):
    return 0

# Gets all nodes in lists, run a process function on it that allows it to split the nodes
# def transformSplitPermutations(acceptStrings, rejectStrings, regexTree, processFunction):
#     acceptArray = matchArray(acceptStrings, regexTree)
#     rejectArray = matchArray(rejectStrings, regexTree)

#     lists = getNodeTypes(acceptArray, rejectArray)
    
#     modifiedLeaves = []
#     for list in lists:
#         # for index, item in reversed(list(enumerate(list[0]['children']))):
#         for index in reversed(range(len(list[0]['value']))):
#             if list[0]['value'][index]['type'] == NodeType.QUANT:
#                 newNodes = processFunction({
#                     # 'acceptMatches' : list[1][forall]['children'][index],
#                     'acceptMatches' : [match['children'][index] for match in list[1]],
#                     'rejectMatches' : [match['children'][index] for match in list[2]],
#                     'currentNode' : list[0]['value'][index],
#                 })

#                 modifiedLeaves.append((list[0]['value'][index]['path'], newNodes))

#     # Copy tree and repleace correct node on each permutation
#     output = []

#     for leafSet in modifiedLeaves:
#         for leaf in leafSet[1]:
#             if len(leafSet[0]) > 0:
#                 currentRegexTree = copy.deepcopy(regexTree)

#                 currentNode = currentRegexTree
#                 for path in leafSet[0][:-2]:
#                     currentNode = currentNode[path]
                
#                 currentNode['value'][leafSet[0][-1]] = leaf[-1]
#                 for node in leaf[:-1]:
#                     currentNode['value'].insert(leafSet[0][-1], node)
                
#                 for index in range(len(currentNode['value'])):
#                     changePathIndex(currentNode['value'][index], len(currentNode['path']) + 1, index)

#                 output.append(currentRegexTree)
#             else:
#                 newParent = {
#                     'type' : NodeType.LIST,
#                     'value' : leaf,
#                     'path' : []
#                 }

#                 for index in range(len(newParent['value'])):
#                     newParent['value'][index]['path'] = ['value', index]
                
#                 output.append(newParent)

#     return output
    # tranform all nodes
    acceptArray = matchArray(acceptStrings, regexTree)
    rejectArray = matchArray(rejectStrings, regexTree)

    nodesData = getNodePaths(acceptArray, rejectArray, getQuants)


# Serch functions:

def getAll(matchData):
    output = []
    currentNodes = [matchData]
    nextNodes = []

    while len(currentNodes) > 0:
        for node in currentNodes:
            match node['type']:
                case NodeType.LIST:
                    nextNodes += node['children']
                case NodeType.QUANT:
                    nextNodes.append(node['child'])
            output.append(node)
        currentNodes = nextNodes
        nextNodes = []
            
    return output