import sre_parse
from anytree import Node, RenderTree

def regexToAst(regex):
    return sre_parse.parse(regex)

def tutpleToNode(tuple):
    print("test")

def AstToNode(ast, parent):
    nodeType = type(ast)

    if nodeType == list:
        print('list')
        for i in ast:
            node = Node(i, parent=parent)
            # parent.children.append(node)

            AstToNode(i, node)
    elif nodeType == tuple:
        print('tuple')

        # for i in ast:
        #     AstToNode(i, parent)
    else:
        print('idk')

def regexToTree(regex):
    parent = Node(regex)

    ast = regexToAst(regex)

    print(type(ast.data))

    AstToNode(ast.data, parent)

    print(parent)