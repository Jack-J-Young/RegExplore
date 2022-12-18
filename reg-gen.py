from random import SystemRandom
from rstr import Rstr
from fileManager import saveListToFile, getFileInfoDensity
from regexParse import regexToAst
import regexTree

sampleSize = 100
regex = r"\d{2,3}-[A-Z]{1,3}-\d+"

buffer = r"\d+[a-z]{,10}"

# Tree tests

ast = regexToAst(regex)



# tree = regexTree.regexNode(ast)

parent = regexTree.regexToNode(ast)

print(regexTree.nodeToRegex(parent))
print(regexTree.nodeToRegex(parent['value'][0]))

#matchData = parent.getMatches('01-D-6542')

matchData = regexTree.getMatchData(parent, '131-D-5324')

print(matchData)

# Get density

rs = Rstr(SystemRandom())

def genRegexStrings(size, regex):  
    output = ["output"]
    for i in range(size):
        output.append(rs.xeger(regex))
    return output

saveListToFile(r'./input.txt', genRegexStrings(sampleSize, regex))

print("Compressability: " + str(getFileInfoDensity(r'./input.txt')))