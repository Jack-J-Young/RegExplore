from RegExtra.RegexTree.nodeEnums import NodeType

def createQuantNode(rawData, child):
    return {
        'type' : NodeType.QUANT,
        'value' : {
            'lower' : rawData[0],
            'upper' : rawData[1],
            'child' : child
        }
    }