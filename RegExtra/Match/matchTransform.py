from RegExtra.RegexTree.regexTree import NodeType, simplifyRegexTree
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

def replaceStep(nodeCollections, replaceFunction):
    output = []
    for nodeCollection in nodeCollections:
        newNodes = replaceFunction({
            'acceptMatches' : nodeCollection[1],
            'rejectMatches' : nodeCollection[2],
            'currentNode' : nodeCollection[0],
        })
        
        for newNode in newNodes:
            newNode['modified'] = True
            match newNode['type']:
                case NodeType.QUANT:
                    newNode['value']['child']['modified'] = True
                case NodeType.PATTERN:
                    newNode['parent']['modified'] = True
            root = newNode
            while root['parent'] != None:
                root = root['parent']

            output.append(root)
    
    for i in output:
        simplifyRegexTree(i)
    return output

def insertStep(nodeCollections, insertFunction):
    output = []
    for nodeCollection in nodeCollections:
        newNodeTupleLists = insertFunction({
            'acceptMatches' : nodeCollection[1],
            'rejectMatches' : nodeCollection[2],
            'currentNode' : nodeCollection[0],
        })

        if newNodeTupleLists:
            for newNodeTupleList in newNodeTupleLists:
                newNode = copy.deepcopy(nodeCollection[0])
                
                for newNodeTuple in newNodeTupleList:
                    newNode['value']['children'].insert(newNodeTuple[0], newNodeTuple[1])

                    # newNode['modified'] = True
                    newNode['value']['children'][newNodeTuple[0]]['modified'] = True
                    newNode['value']['children'][newNodeTuple[0]]['value']['child']['modified'] = True

                    newNodeTuple[1]['parent'] = newNode
                    newNodeTuple[1]['path'] = ['value', 'children', 0]

                for index in range(len(newNode['value']['children'])):
                    newNode['value']['children'][index]['path'][-1] = index

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

            newNode['modified'] = True
            
            del newNode['value']['children'][removeIndex]

            for index in range(len(newNode['value']['children'])):
                newNode['value']['children'][index]['path'][-1] = index

            root = newNode
            while root['parent'] != None:
                root = root['parent']

            output.append(root)
    
    for i in output:
        simplifyRegexTree(i)
    return output

def getAll(matchData):
    output = []
    currentNodes = [matchData]
    nextNodes = []

    while len(currentNodes) > 0:
        for node in currentNodes:
            match node['type']:
                case NodeType.LIST:
                    nextNodes += node['value']
                case NodeType.QUANT:
                    nextNodes += node['children']
            output.append(node)
        currentNodes = nextNodes
        nextNodes = []
            
    return output