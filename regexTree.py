import sre_parse

class regexNode:
    def getName(self):
        return ''

class listNode(regexNode):
    def __init__(self):
        self.children = []
    
    def appendChild(self, node):
        self.children.append(node)

    def getName(self):
        name = '('
        for subData in self.children:
            name += subData.getName()
        return name + ')'

class quantNode(regexNode):
    # Range, a-b, i = infinity

    def __init__(self, lower, upper, childNode):
        self.lower = lower
        self.upper = upper
        self.childNode = childNode

    def getName(self):
        return f'{self.childNode.getName()}{{{self.lower},{self.upper}}}'

class patternNode(regexNode):
    def __init__(self, char):
        self.char = char

    def getName(self):
        return self.char

# class inNode(regexNode):
#     def __init__(self, tuple):
#         self.tuple = tuple

#     def getName(self):
#         return 'imnotesure'

def toNode(rawData):
    # _type = type(node.raw)
    # typeName = _type.name
    # print(typeName)

    node = regexNode()

    if isinstance(rawData, sre_parse.SubPattern):
        node = listNode()

        for subData in rawData.data:
            node.appendChild(toNode(subData))

    elif isinstance(rawData, tuple):
        if rawData[0] == sre_parse.MAX_REPEAT:
            repeatData = rawData[1]
            node = quantNode(repeatData[0], repeatData[1], toNode(repeatData[2]))

        elif rawData[0] == sre_parse.SUBPATTERN:
            node = listNode()

            for subData in rawData[1][3]:
                node.appendChild(toNode(subData))

        elif rawData[0] == sre_parse.LITERAL:
            node = patternNode(chr(rawData[1]) + "")

        elif rawData[0] == sre_parse.IN:
            node = patternNode("thing")

        else:
            print(rawData)

    return node