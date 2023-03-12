from enum import Enum
import json

class ToolType(Enum):
    UNKOWN = -1
    QUANT = 0
    PATTERN = 1
    SPLIT = 2

def loadTools(path = './configs/default.json'):
    configFile = open(path)
    config = json.load(configFile)
    
    tools = []

    for toolData in config['tools']:
        tool = {'type' : ToolType.UNKOWN}

        match toolData['type']:
            case 'quant':
                tool['type'] = ToolType.QUANT
            case 'pattern':
                tool['type'] = ToolType.PATTERN
            case 'split':
                tool['type'] = ToolType.SPLIT
            
        
        module = __import__(toolData['module'], fromlist=[toolData['functionName']])

        tool['function'] = getattr(module, toolData['functionName'])

        tools.append(tool)

    return tools