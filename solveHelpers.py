from itertools import permutations

def getOrderedPerms(startPos, size):
    output = []

    current = []
    for index in range(size):
        current.append(index + startPos)
        output.append(current.copy())

    return output