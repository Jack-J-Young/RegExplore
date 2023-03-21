from RegExtra.RegexTree.toolset.toolCreator import loadConfig
from RegExtra.RegexTree.toolset.toolSolver import userCreativeTransform
import RegExtra.RegexTree.regexTree as regexTree

config = loadConfig('./configs/creative-transform.json')

parent = userCreativeTransform(config)

print(regexTree.nodeToRegex(parent))