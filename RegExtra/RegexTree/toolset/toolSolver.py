import oapackage
from RegExtra.Match.matchTransform import transformPatternPermutations, transformQuantifierPermutations, transformSplitPermutations
from RegExtra.RegexTree.nodeEnums import NodeType
from RegExtra.RegexTree.regexTree import nodeToRegex, pushPath
from RegExtra.RegexTree.toolset.toolCreator import ToolType
import re

from fileManager import getDensityScoreFromReference, getListDensity, getRegexDensity

def getToolMatches(acceptSet, rejectSet, regex, toolset, toolTypeBlackList=[]):
    if regex['type'] != NodeType.LIST:
        pushPath(regex, ['value', 0])
        regex = {
            'type' : NodeType.LIST,
            'value' : [regex],
            'path' : []
        }

    solutions = []

    for tool in toolset:
        if tool['type'] == ToolType.QUANT and (not set([ToolType.QUANT]) <= set(toolTypeBlackList)):
            solutions += transformQuantifierPermutations(acceptSet, rejectSet, regex, tool['function'])
        if tool['type'] == ToolType.PATTERN and (not set([ToolType.PATTERN]) <= set(toolTypeBlackList)):
            solutions += transformPatternPermutations(acceptSet, rejectSet, regex, tool['function'])
        if tool['type'] == ToolType.SPLIT and (not set([ToolType.SPLIT]) <= set(toolTypeBlackList)):
            preSolutions = getToolMatches(acceptSet, rejectSet, regex, toolset, [ToolType.SPLIT, ToolType.PATTERN])

            midSolution = []
            for solution in preSolutions:
                midSolution += transformSplitPermutations(acceptSet, rejectSet, solution, tool['function'])

            postSolution = []
            for transformedRegex in midSolution:
                postSolution += getToolMatches(acceptSet, rejectSet, transformedRegex, toolset, [ToolType.SPLIT, ToolType.QUANT])

            solutions += postSolution
    
    # for sol in solutions:
    #     print(nodeToRegex(sol))
    solutionStrings = list(map(nodeToRegex, solutions))
    for index in reversed(range(len(solutionStrings))):
        if solutionStrings[index] in solutionStrings[(index + 1):]:
            del solutions[index]

    return solutions

def getOptimalSolutions(acceptStrings, rejectStrings, matches):
    acceptDensity = getListDensity(acceptStrings)
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
        density = getRegexDensity(regex)
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

def firstParetoSolve(acceptStrings, rejectStrings, regex, toolset):
    currentRegex = regex
    previousRegex = None

    while nodeToRegex(currentRegex) != nodeToRegex(previousRegex):
        matches = getToolMatches(acceptStrings, rejectStrings, currentRegex, toolset)

        paretoSolutions = getOptimalSolutions(acceptStrings, rejectStrings, matches)

        previousRegex = currentRegex
        currentRegex = paretoSolutions[-1]
        for sol in paretoSolutions:
            print(nodeToRegex(sol))
        print()
    
    print(nodeToRegex(currentRegex))
    return currentRegex