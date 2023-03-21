from RegExtra.RegexTree.toolset.toolCreator import loadConfig
from RegExtra.RegexTree.toolset.toolSolver import userCreativeTransform, userParetoSolve
from RegExtra.regexParse import regexToAst       
import RegExtra.RegexTree.regexTree as regexTree

regex = r"a+(?=b)."

ast = regexToAst(regex)

parent = regexTree.regexToNode(ast)

print(regexTree.nodeToRegex(parent))

config = loadConfig('./configs/creative-transform.json')

accepts = [
    # '242-LM-1526',
    # '07-OY-579154',
    # '09-D-3032675',
    # '141-L-07439138',
    # '11-LH-453',
    # '262-T-487',
    # '252-KK-51',
    
    '+387 665 130 4293',
    '+233 30 489 2948',
    '+972 55 245 0796',
    '+377 8501 0634',
    '+1 758 568 9976',
    '+216 9683 4056',
    '+993 12 513055',
    
    # 'D01 R5P3',
    # 'F93 X2DR',
    # 'F92 RR76',
    # 'D12 CD40',
    # 'R21 RK73',
    # 'W23 H2Y6',
    
    # '187.163.193.127',
    # '197.248.167.45',
    # '202.89.167.209',
    # '126.171.54.142',
    # '220.153.139.43',
    
    # 'luciano_hahn77@yahoo.com',
    # 'vergie.bogisich4@hotmail.com',
    # 'annabel_batz@gmail.com',
    # 'german8@yahoo.com',
    # 'alisa39@yahoo.com',
    # 'myles_ankunding75@hotmail.com',
    # 'vladimir8@gmail.com',
    # 'janis90@gmail.com',
    # 'alden_ortiz53@hotmail.com',
    # 'justus3@gmail.com',
]

rejects = [
]

parent = userCreativeTransform(accepts, rejects, config)

print(regexTree.nodeToRegex(parent))