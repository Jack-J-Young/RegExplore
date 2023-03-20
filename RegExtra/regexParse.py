import sre_parse
from anytree import Node, RenderTree

def regexToAst(regex):
    parse = sre_parse.parse(regex)
    return parse

# def tupleToNode(tuple):
#     print("test")
#     print(type(tuple[0]))
#     if (tuple[0].name == 'LITERAL'):
#         return Node(chr(tuple[1]))
#     elif (tuple[0].name == 'MAX_REPEAT'):
#         node = Node(f'{tuple[1][2]}{{{tuple[1][0]},{tuple[1][1]}}}')
#         AstToNode(tuple[1][2], node)
#         return node
#     elif (tuple[0].name == 'SUBPATTERN'):
#         print('test2')
    
#     return Node('null')

# def AstToNode(ast, parent):
#     nodeType = type(ast)

#     if nodeType == list:
#         print('list')
#         for i in ast:
#             # This needs to be check if tuple or list...

#             node = Node(i, parent=parent)
#             # parent.children.append(node)

#             AstToNode(i, node)
#     elif nodeType == tuple:
#         print('tuple')
#         node = tupleToNode(ast)
#         node.parent = parent
#     else:
#         print('idk')

# def regexToTree(regex):
#     parent = Node(regex)

#     ast = regexToAst(regex)

#     print(type(ast.data))

#     AstToNode(ast.data, parent)

#     print(parent)