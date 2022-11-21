import json
from random import SystemRandom
from rstr import Rstr
from sly import Lexer, Parser
from fileManager import saveListToFile, getFileInfoDensity
from regexParse import regexToTree, regexToAst
import regexTree

sampleSize = 100
regex = r"(\d+--e*)-(-?e-)\d{2,3}--[A-Z]{1,3}-\d+"

# Tree tests

ast = regexToAst(regex)



# tree = regexTree.regexNode(ast)

parent = regexTree.toNode(ast)

print(parent.getName())
print(parent.children[0].getName())

# Get density

rs = Rstr(SystemRandom())

def genRegexStrings(size, regex):
    output = ["output"]
    for i in range(size):
        output.append(rs.xeger(regex))
    return output

saveListToFile(r'./input.txt', genRegexStrings(sampleSize, regex))

print(getFileInfoDensity(r'./input.txt'))