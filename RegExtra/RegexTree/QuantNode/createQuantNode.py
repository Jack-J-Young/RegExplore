from RegExtra.RegexTree.regexTree import NodeType

def createQuantNode(rawData):
    return {
        'type' : NodeType.QUANT,
        'value' : {
            'lower' : rawData[1][0],
            'upper' : rawData[1][1],
            'child' : rawData[1](rawData[1][2])
        }
    }