from random import SystemRandom
from rstr import Rstr
from RegExtra.RegexTree.PatternNode.enums import PatternType
from fileManager import saveListToFile, getFileInfoDensity
from regexParse import regexToAst       
import RegExtra.RegexTree.regexTree as regexTree
import RegExtra.Match.matchTransform as matchTransform

sampleSize = 100
regex = r"\d{1,9}-[A-Z]{1,3}-\d+"
#regex = r"\d{1,9}-\w{1,3}ⳤ-\d+"

buffer = r"\d+[a-z]{,10}"

# Tree tests

ast = regexToAst(regex)

# tree = regexTree.regexNode(ast)

parent = regexTree.regexToNode(ast)

print(regexTree.nodeToRegex(parent))
print(regexTree.nodeToRegex(parent['value'][0]))

#matchData = parent.getMatches('01-D-6542')

matchTransform.transformQuantifiers([
    '131-F-1',
    '13-D-3',
    '131-G-1',
    '1323-D-3',
    '1313-E-1',
    '13-D-3',
], [
    '01-D-12534',
    '98-D-32244'
], parent, lambda properties : (min(properties['acceptSet']), max(properties['acceptSet'])))

def basicPatTrans(properties):
    set = [item for sublist in [c for c in properties['acceptSet']] for item in sublist]
    return {
            'type' : PatternType.RANGE,
            'value' : (min(set), max(set)),
            'regex' : f'[{min(set)}-{max(set)}]'
        }

matchTransform.transformPatterns([
    '131-F-1',
    '13-D-3',
    '131-G-1',
    '1323-D-3',
    '1313-E-1',
    '13-D-3',
], [
    '01-D-12534',
    '98-D-32244'
], parent, basicPatTrans)

print(regexTree.nodeToRegex(parent))

# matchData = regexTree.getMatchData(parent, '131-D-5324')

# print(matchData)

# Get density

rs = Rstr(SystemRandom())

def genRegexStrings(size, regex):  
    output = ["output"]
    for i in range(size):
        output.append(rs.xeger(regex))
    return output

saveListToFile(r'./input.txt', genRegexStrings(sampleSize, regex))

print("Compressability: " + str(getFileInfoDensity(r'./input.txt')))