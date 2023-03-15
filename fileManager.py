import bz2, os
import zlib
from random import SystemRandom

from rstr import Rstr

compressionLevel = 9
rs = Rstr(SystemRandom())

def compressBytes(bytes, level=2):
    return zlib.compress(bytes, level=level)

def genRegexStrings(regex, size):
    output = []
    for i in range(size):
        output.append(rs.xeger(regex))
    return output

def getListCompressability(stringList):
    agregate = ""
    for string in stringList:
        agregate += string + '\n'
    
    uncompressedString = str.encode(agregate)

    compressedString = compressBytes(uncompressedString)

    return len(compressedString) / len(uncompressedString)

def getRegexCompressability(regex, sampleSize = 100):
    return getListCompressability(genRegexStrings(regex, sampleSize))

def getDensityScoreFromReference(referenceDensity, density):
    if density > referenceDensity:
        return 1 - (density - referenceDensity) / (1 - referenceDensity)
    else:
        return density / referenceDensity

# def saveListToFile(fileName, data):
#     with open(fileName, 'w') as file:
#         for line in data:
#             # write each item on a new line
#             file.write('%s\n' % line)

# def getFileSize(fileName):
#     return os.stat(fileName).st_size

# def getFileInfoDensity(inputDir):

#     # Compress File with bz2
#     text = bz2.compress(open(inputDir, 'rb').read(), compressionLevel)

#     # Temporarily save file to get filesize
#     compressedFile = open(r'./.temp', "wb")
#     compressedFile.write(text)
#     compressedFile.close()

#     # Return compression ratio = compressed size / original size
#     return getFileSize(r'./.temp') / getFileSize(inputDir)

# def getRegexDensity(regex, sampleSize = 500):
#     saveListToFile(r'./input.txt', genRegexStrings(sampleSize, regex))
#     return getFileInfoDensity(r'./input.txt')

# def getListDensity(list):
#     saveListToFile(r'./input.txt', list)
#     return getFileInfoDensity(r'./input.txt')