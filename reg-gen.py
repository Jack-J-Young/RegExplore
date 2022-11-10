import json
from random import SystemRandom
from rstr import Rstr
from sly import Lexer, Parser
from fileManager import saveListToFile, getFileInfoDensity
from regexParse import regexToTree

# regex = r"\d{2,3}-[A-Z]{1,3}-\d+"
regex = r'(?<!\\)(\{\d+(,\d*)?\}|\*|\+|\?)'
# regex = r'(?<!\\).'

sampleSize = 100

rs = Rstr(SystemRandom())

regexToTree(regex)

def genRegexStrings(size, regex):
    output = ["output"]
    for i in range(size):
        output.append(rs.xeger(regex))
    return output

saveListToFile(r'./input.txt', genRegexStrings(sampleSize, regex))

print(getFileInfoDensity(r'./input.txt'))

QUANT = r'[^\\][[{\d*,?\d*}]|*|+|?]'

# string = "test.string.example.3"

# class CalcLexer(Lexer):
#     # Set of token names.   This is always required
#     tokens = { ID, NUMBER, PLUS, MINUS, TIMES,
#                DIVIDE, ASSIGN, LPAREN, RPAREN, DOT }

#     # String containing ignored characters between tokens
#     ignore = ' \t'

#     # Regular expression rules for tokens
#     ID      = r'[a-zA-Z_][a-zA-Z0-9_]*'
#     NUMBER  = r'\d+'
#     PLUS    = r'\+'
#     MINUS   = r'-'
#     TIMES   = r'\*'
#     DIVIDE  = r'/'
#     ASSIGN  = r'='
#     LPAREN  = r'\('
#     RPAREN  = r'\)'
#     DOT     = r'.'

# lexer = CalcLexer()

# tokenised = lexer.tokenize(string)

# for tok in tokenised:
#      print('type=%r, value=%r' % (tok.type, tok.value))

# print(rstr.xeger(regex))    