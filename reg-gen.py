from RegExtra.RegexTree.toolset.toolCreator import loadConfig
from RegExtra.RegexTree.toolset.toolSolver import userCreativeTransform, userParetoSolve
from RegExtra.regexParse import regexToAst       
import RegExtra.RegexTree.regexTree as regexTree

regex = r".*"

config = loadConfig()

accepts = [
    '242-LM-1526',
    '07-OY-579154',
    '09-D-3032675',
    '141-L-07439138',
    '11-LH-4',
    '262-T-4',
    '252-KK-51',
]

rejects = [
]

parent = userParetoSolve(accepts, rejects, regex, config)

print(regexTree.nodeToRegex(parent))