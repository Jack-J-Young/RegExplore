import bz2, os

compressionLevel = 9

def saveListToFile(fileName, data):
    with open(fileName, 'w') as file:
        for line in data:
            # write each item on a new line
            file.write('%s\n' % line)

def getFileSize(fileName):
    return os.stat(fileName).st_size

def getFileInfoDensity(inputDir):

    # Compress File with bz2
    text = bz2.compress(open(inputDir, 'rb').read(), compressionLevel)

    # Temporarily save file to get filesize
    compressedFile = open(r'./.temp', "wb")
    compressedFile.write(text)
    compressedFile.close()

    # Return compression ratio = compressed size / original size
    return getFileSize(r'./.temp') / getFileSize(inputDir)