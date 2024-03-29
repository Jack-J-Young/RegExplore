import oapackage
from RegExtra.Match.matchTransform import deleteStep, getNodeCollections, insertStep, replaceStep
from RegExtra.RegexTree.nodeEnums import ListType, NodeType
from RegExtra.RegexTree.regexTree import matchArray, nodeToRegex, regexToNode, simplifyRegexTree
from RegExtra.RegexTree.toolset.toolCreator import StepType
import re

from RegExtra.fileManager import genRegexStrings, getDensityScoreFromReference, getListCompressibility, getRegexCompressibility
from RegExtra.regexParse import regexToAst

# Removes modified tags on regex tree
def removeModified(node):
    output = []
    currentNodes = [node]
    nextNodes = []

    while len(currentNodes) > 0:
        for node in currentNodes:
            match node['type']:
                case NodeType.LIST:
                    nextNodes += node['value']['children']
                case NodeType.QUANT:
                    nextNodes.append(node['value']['child'])
            node.pop("modified", None)
        currentNodes = nextNodes
        nextNodes = []
            
    return output

# Checks parent and path nodes of regex trees
def checkValidity(node):
    currentNodes = [node]
    nextNodes = []

    while len(currentNodes) > 0:
        for node in currentNodes:
            match node['type']:
                case NodeType.LIST:
                    nextNodes += node['value']['children']
                case NodeType.QUANT:
                    nextNodes.append(node['value']['child'])
            if node['parent'] != None:
                pathed = node['parent']
                for p in node['path']:
                    pathed = pathed[p]
                if not node == pathed:
                    print('INVALID TREE')
        currentNodes = nextNodes
        nextNodes = []

# Returns all transformations of a given regex and config
def getToolMatches(acceptSet, rejectSet, regexList, config):
    preCalc = []
    
    for regex in regexList:
        checkValidity(regex)
        if regex['type'] != NodeType.LIST:
            regex = {
                'type' : NodeType.LIST,
                'value' : {
                    'type' : ListType.NORMAL,
                    'children' : [regex]
                },
                'parent' : None,
                'path' : []
            }
            regex['value']['children'][0]['parent'] = regex
            regex['value']['children'][0]['path'] = ['value', 0]

    solutions = []

    for operationKey in config['operations']:
        operationData = config['operations'][operationKey]
        operationRegex = regexList
        nextRegex = []

        for stepName in operationData['steps']:
            
            step = config['steps'][stepName]
            inputSet = set(step['inputTypes'])
            
            operationCollection = []
            
            for opRegex in operationRegex:
                a = matchArray(acceptSet, opRegex, preCalc)
                b = matchArray(rejectSet, opRegex, preCalc)
                c = getNodeCollections(a, b)
                operationCollection.append(c)
            first = True
            
            
            for collectionIndex in reversed(range(len(operationCollection))):
                stepCollection = operationCollection[collectionIndex]
                if len(stepCollection) > 0:
                    root = stepCollection[0][0]
                    while root['parent'] != None:
                        root = root['parent']
                    print(stepName + ': ' + nodeToRegex(root))
                    
                    if first:
                        filteredCollections = list(filter(lambda collection : set([collection[0]['type']]).issubset(inputSet), stepCollection))
                    else:
                        filteredCollections = list(filter(lambda collection : set([collection[0]['type']]).issubset(inputSet) and ('modified' in collection[0]), stepCollection))

                    for collection in filteredCollections:
                        removeModified(collection[0])
                    first = False

                    match step['type']:
                        case StepType.REPLACE:
                            nextRegex += replaceStep(filteredCollections, step['function'])
                        case StepType.INSERT:
                            nextRegex += insertStep(filteredCollections, step['function'])
                        case StepType.DELETE:
                            nextRegex += deleteStep(filteredCollections, step['function'])
                    
                    del operationCollection[collectionIndex]
                
            nextRegexStrings = list(map(nodeToRegex, nextRegex))
            for index in reversed(range(len(nextRegexStrings))):
                if nextRegexStrings[index] in nextRegexStrings[(index + 1):]:
                    del nextRegex[index]
                
            operationRegex = nextRegex
            nextRegex = []
        
        for i in operationRegex:
            simplifyRegexTree(i)
        solutions += operationRegex

    solutionStrings = list(map(nodeToRegex, solutions))
    for index in reversed(range(len(solutionStrings))):
        if solutionStrings[index] in solutionStrings[(index + 1):]:
            del solutions[index]

    return solutions

# Returns pareto optimal regex given a list of regex
def getOptimalSolutions(acceptStrings, rejectStrings, matches):
    acceptDensity = getListCompressibility(acceptStrings)
    print("accDens: " + str(acceptDensity))

    scores = []
    for tree in matches:
        regex = nodeToRegex(tree)

        # Accept %
        acceptCount = 0
        for string in acceptStrings:
            if re.match(f'\A{regex}\Z', string):
                acceptCount += 1
        
        # Reject %
        rejectCount = 0
        for string in rejectStrings:
            if re.match(f'\A{regex}\Z', string):
                rejectCount += 1

        acceptScore = acceptCount / len(acceptStrings)
        rejectScore = 1 - rejectCount / len(rejectStrings) if len(rejectStrings) > 0 else 1.0
        density = getRegexCompressibility(regex)
        print(regex + " Dens: " + str(density))
        densityScore = getDensityScoreFromReference(acceptDensity, density)
        scores.append((acceptScore, rejectScore, densityScore))
        
    # From https://oapackage.readthedocs.io/en/latest/examples/example_pareto.html
    pareto = oapackage.ParetoDoubleLong()

    for i in range(len(scores)):
        w = oapackage.doubleVector(scores[i])
        print(str(w[0]) + ", " + str(w[1]) + ", " + str(w[2]) + ": " + nodeToRegex(matches[i]))
        pareto.addvalue(w, i)
    
    output = []
    for index in pareto.allindices():
        output.append(matches[index])

    return output

# Returns pareto optimal solutions given a list of regex
def getDenseSolutions(acceptStrings, rejectStrings, matches):
    scores = []
    for tree in matches:
        regex = nodeToRegex(tree)

        # Accept %
        acceptCount = 0
        for string in acceptStrings:
                acceptCount += 1
        
        # Reject %
        rejectCount = 0
        for string in rejectStrings:
            if re.match(f'\A{regex}\Z', string):
                rejectCount += 1

        acceptScore = acceptCount / len(acceptStrings) if len(rejectStrings) > 0 else 1.0
        rejectScore = 1 - rejectCount / len(rejectStrings) if len(rejectStrings) > 0 else 1.0
        density = getRegexCompressibility(regex)
        scores.append((acceptScore, rejectScore, density))
        
    # From https://oapackage.readthedocs.io/en/latest/examples/example_pareto.html
    pareto = oapackage.ParetoDoubleLong()

    for i in range(len(scores)):
        w = oapackage.doubleVector(scores[i])
        print(str(w[0]) + ", " + str(w[1]) + ", " + str(w[2]) + ": " + nodeToRegex(matches[i]))
        pareto.addvalue(w, i)
    
    output = []
    for index in pareto.allindices():
        output.append(matches[index])

    return output

# Returns a transformed regex given regex
def firstParetoSolve(acceptStrings, rejectStrings, regex, config):
    currentRegex = regex
    previousRegex = None

    while nodeToRegex(currentRegex) != nodeToRegex(previousRegex):
        matches = getToolMatches(acceptStrings, rejectStrings, [currentRegex], config)

        paretoSolutions = getOptimalSolutions(acceptStrings, rejectStrings, matches)

        temp = currentRegex
        currentRegex = paretoSolutions[0]
        if nodeToRegex(previousRegex) == nodeToRegex(currentRegex):
            currentRegex = paretoSolutions[-1]
        
        previousRegex = temp
    
    return currentRegex

# takes in config and returns transformed regex, uses user input
def userCreativeTransform(config):
    acceptStrings = config['accepts']
    rejectStrings = config['rejects']
    
    perSolution = 3
    
    # currentRegex = [regexToNode(regexToAst(i[1:-1])) for i in rexpy.results.rex]
    currentRegex = [regexToNode(regexToAst(config['startRegex']))]
    previousRegex = None
    
    while True:
        matches = getToolMatches(acceptStrings, rejectStrings, currentRegex, config)

        if matches:
            paretoSolutions = getDenseSolutions(acceptStrings, rejectStrings, matches)
        else:
            paretoSolutions = currentRegex
        
        index = 0
        totalGenerated = []
        for solutionIndex in range(len(paretoSolutions)):
            solution = paretoSolutions[solutionIndex]
            regex = nodeToRegex(solution)
            print('[' + str(solutionIndex) + ']: ' + regex)

            generatedStrings = genRegexStrings(regex, perSolution)
            totalGenerated += generatedStrings

            for genIndex in range(len(generatedStrings)):
                print(repr(generatedStrings[genIndex]))
                index += 1
        
        print("Enter 'F (index)' to finish with regex")
        newAcceptsRaw = input("Enter indices (e.g. '0 3 4'): ")
        indices = []
        if len(newAcceptsRaw) > 0:
            rawList = newAcceptsRaw.split(' ')
            
            if rawList[0] == 'F':
                return paretoSolutions[int(rawList[1])]
            
            for i in range(len(rawList)):
                if rawList[i] == '':
                    del rawList[i]

            indices = [int(i) for i in rawList]
            # Un comment for mutations
            # acceptStrings = []
            # for i in indices:
            #     acceptStrings += totalGenerated[i*perSolution:(i+1)*perSolution]
            
            indices.sort()

            for i in reversed(indices):
                del totalGenerated[i*perSolution:(i+1)*perSolution]

        rejectStrings += totalGenerated

        if len(indices) > 0:
            currentRegex = []
            for i in indices:
                currentRegex.append(paretoSolutions[i])

def userParetoSolve(acceptStrings, rejectStrings, regex, config):
    
    perSolution = 3

    # .*-.*-.*
    # currentRegex = [regexToNode(regexToAst(i[1:-1])) for i in rexpy.results.rex]
    # currentRegex = [regexToNode(regexToAst('.*-.*-.*'))]
    currentRegex = [regexToNode(regexToAst(regex))]
    previousRegex = None

    while len(currentRegex) > 0:
        matches = getToolMatches(acceptStrings, rejectStrings, currentRegex, config)

        paretoSolutions = getOptimalSolutions(acceptStrings, rejectStrings, matches)
        paretoScoring = [0 for _ in paretoSolutions]
        
        index = 0
        totalGenerated = []
        for solution in paretoSolutions:
            regex = nodeToRegex(solution)
            print(regex)

            generatedStrings = genRegexStrings(regex, perSolution)
            totalGenerated += generatedStrings

            for genIndex in range(len(generatedStrings)):
                print('[' + str(index) + ']: ' + repr(generatedStrings[genIndex]))
                index += 1
        
        newAcceptsRaw = input("Enter indices: ")
        if len(newAcceptsRaw) > 0:
            rawList = newAcceptsRaw.split(' ')
            for i in range(len(rawList)):
                if rawList[i] == '':
                    del rawList[i]

            indices = [int(i) for i in rawList]
            for i in indices:
                paretoScoring[int(i/perSolution)] += 1
                acceptStrings += totalGenerated[i]
            
            indices.sort()

            for i in reversed(indices):
                del totalGenerated[i]

        rejectStrings = totalGenerated
        
        maxScore = 0
        for scoreIndex in range(len(paretoScoring)):
            if paretoScoring[scoreIndex] > maxScore:
                maxScore = paretoScoring[scoreIndex]
        
        currentRegex = []
        for index in range(len(paretoScoring)):
            if paretoScoring[index] == maxScore:
                currentRegex.append(paretoSolutions[index])
    
    return currentRegex