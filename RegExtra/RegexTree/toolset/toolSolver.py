import oapackage
from RegExtra.Match.matchTransform import deleteStep, getNodeCollections, insertStep, replaceStep
from RegExtra.RegexTree.nodeEnums import NodeType
from RegExtra.RegexTree.regexTree import matchArray, nodeToRegex
from RegExtra.RegexTree.toolset.toolCreator import StepType
import re

from fileManager import getDensityScoreFromReference, getListCompressability, getRegexCompressability

def getToolMatches(acceptSet, rejectSet, regex, config):
    if regex['type'] != NodeType.LIST:
        regex = {
            'type' : NodeType.LIST,
            'value' : [regex],
            'path' : []
        }
        regex['value'][0]['parent'] = regex
        regex['value'][0]['path'] = ['value', 0]

    solutions = []

    for operationKey in config['operations']:
        operationData = config['operations'][operationKey]
        operationRegex = [regex]
        nextRegex = []

        for stepName in operationData['steps']:
            step = config['steps'][stepName]
            inputSet = set(step['inputTypes'])
            operationCollection = [getNodeCollections(matchArray(acceptSet, opRegex), matchArray(rejectSet, opRegex)) for opRegex in operationRegex]
                
            for stepCollection in operationCollection:
                filteredCollections = list(filter(lambda collection : set([collection[0]['type']]).issubset(inputSet), stepCollection))

                match step['type']:
                    case StepType.REPLACE:
                        nextRegex += replaceStep(filteredCollections, step['function'])
                    case StepType.INSERT:
                        nextRegex += insertStep(filteredCollections, step['function'])
                    case StepType.DELETE:
                        nextRegex += deleteStep(filteredCollections, step['function'])
            operationRegex = nextRegex
            nextRegex = []
        
        solutions += operationRegex

    solutionStrings = list(map(nodeToRegex, solutions))
    for index in reversed(range(len(solutionStrings))):
        if solutionStrings[index] in solutionStrings[(index + 1):]:
            del solutions[index]

    return solutions

def getOptimalSolutions(acceptStrings, rejectStrings, matches):
    acceptDensity = getListCompressability(acceptStrings)
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
        rejectScore = 1 - rejectCount / len(rejectStrings)
        density = getRegexCompressability(regex)
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

def firstParetoSolve(acceptStrings, rejectStrings, regex, config):
    currentRegex = regex
    previousRegex = None

    while nodeToRegex(currentRegex) != nodeToRegex(previousRegex):
        matches = getToolMatches(acceptStrings, rejectStrings, currentRegex, config)

        paretoSolutions = getOptimalSolutions(acceptStrings, rejectStrings, matches)

        temp = currentRegex
        currentRegex = paretoSolutions[0]
        if nodeToRegex(previousRegex) == nodeToRegex(currentRegex):
            currentRegex = paretoSolutions[-1]
        
        previousRegex = temp

        for sol in paretoSolutions:
            print(nodeToRegex(sol))
        print()
    
    print(nodeToRegex(currentRegex))
    return currentRegex