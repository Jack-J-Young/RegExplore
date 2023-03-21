from enum import Enum
import json

from RegExtra.RegexTree.nodeEnums import NodeType

class StepType(Enum):
    UNKOWN = -1
    REPLACE = 0
    INSERT = 1
    DELETE = 2

def loadConfig(path = './configs/default.json'):
    configFile = open(path)
    config = json.load(configFile)
    
    steps = dict()

    for stepData in config['steps']:
        step = {'type' : StepType.UNKOWN}

        match stepData['type']:
            case 'replace':
                step['type'] = StepType.REPLACE
            case 'insert':
                step['type'] = StepType.INSERT
            case 'delete':
                step['type'] = StepType.DELETE
        
        inputTypes = []
        for inputString in stepData['inputTypes']:
            match inputString:
                case 'list':
                    inputTypes.append(NodeType.LIST)
                case 'quant':
                    inputTypes.append(NodeType.QUANT)
                case 'pattern':
                    inputTypes.append(NodeType.PATTERN)
        step['inputTypes'] = inputTypes

        module = __import__(stepData['module'], fromlist=[stepData['functionName']])

        step['function'] = getattr(module, stepData['functionName'])

        steps[stepData['name']] = step

    operations = dict()

    for operation in config['operations']:
        operations[operation['name']] = operation

    accepts = []
    rejects = []
    with open(config['acceptFile']) as acceptFile:
        accepts = [i.replace('\n','') for i in acceptFile.readlines()]
    with open(config['rejectFile']) as rejectFile:
        rejects = [i.replace('\n','') for i in rejectFile.readlines()]

    config = {
        "accepts" : accepts,
        "rejects" : rejects,
        "steps" : steps,
        "operations" : operations
    }

    return config
