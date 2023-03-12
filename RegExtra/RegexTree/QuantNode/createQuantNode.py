import sre_parse
from RegExtra.RegexTree.QuantNode.QuantEnums import QuantSpecials
from RegExtra.RegexTree.nodeEnums import NodeType

def createQuantNode(rawData, child, path):
    return {
        'type' : NodeType.QUANT,
        'value' : {
            'lower' : rawData[0],
            'upper' : QuantSpecials.MAX_REPEAT if rawData[1] == sre_parse.MAXREPEAT else rawData[1],
            'child' : child
        },
        'path' : path
    }