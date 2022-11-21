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
    # Range, a-b, i = sre_parse.MAXREPEAT

    def __init__(self, lower, upper, childNode):
        self.lower = lower
        self.upper = upper
        self.childNode = childNode

    def getName(self):
        if self.lower == 0 and self.upper == sre_parse.MAXREPEAT:
            return f'{self.childNode.getName()}*'
        elif self.lower == 1 and self.upper == sre_parse.MAXREPEAT:
            return f'{self.childNode.getName()}+'
        elif self.lower == 0 and self.upper == 1:
            return f'{self.childNode.getName()}?'
        elif self.upper == sre_parse.MAXREPEAT:
            return f'{self.childNode.getName()}{{{self.lower},}}'
        else:
            return f'{self.childNode.getName()}{{{self.lower},{self.upper}}}'

class patternNode(regexNode):
    def __init__(self, char):
        self.char = char

    def getName(self):
        return self.char

def toNode(rawData):

    node = regexNode()

    if isinstance(rawData, sre_parse.SubPattern):
        if len(rawData.data) == 1:
            node = toNode(rawData.data[0])
        else:
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
            value = ''

            for charData in rawData[1]:
                if charData[0] == sre_parse.CATEGORY:
                    if charData[1] == sre_parse.CATEGORY_DIGIT:
                        value += r'\d'
                    elif charData[1] == sre_parse.CATEGORY_WORD:
                        value += r'\w'
                elif charData[0] == sre_parse.RANGE:
                    value += f'[{chr(charData[1][0])}-{chr(charData[1][1])}]'
                else:
                    print(rawData)
            
            node = patternNode(value)

        else:
            print(rawData)

    return node