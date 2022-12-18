from itertools import permutations

def getOrderedPerms(startPos, size):
    output = []

    current = []
    for index in range(size):
        current.append(index + startPos)
        output.append(current.copy())

    return output


    # if len(perms[0]) != 0:


# def getOrderedPerms(startPos, size):
#     output = []
#     for index in range(size):
#         perms = permutations(range(size), index + 1)
#         for permTuple in perms:
#             if all(permTuple[i] <= permTuple[i+1] for i in range(len(permTuple) - 1)):
#                 output.append(tuple(x+startPos for x in permTuple))

#     return output


#     # if len(perms[0]) != 0:
