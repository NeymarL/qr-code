#-*- coding:utf-8 -*-
# Global variables and Constants defined here

# sizes of QR Code, on increasing in steps of 4 modules per side up to
# Version 40 which measures 177 modules × 177 module
VERSION_TABLE = {1: 21, 2: 25, 3: 29, 40: 177}

# mode indicators
MODES = {'ECI': 7, 'Numeric': 1, 'Alphanumeric': 2, 'Byte': 4, 'Kanji': 8}

# mode indicators bits
MODE_BITS = 4

# ending symbol
ENDING = '0000'

# error correction indicator
ERROR_CORR_INDICATOR = {'L': '01', 'M': '00', 'Q': '11', 'H': '10'}

# the alpha-numeric map table
ALPHANUMERIC_TABLE = {' ': 36, '$': 37, '%': 38, '*': 39, '+': 40,
                      '-': 41, '.': 42, '/': 43, ':': 44, '0': 0, 'A': 10}

# character count indicator
COUNT_INDICATOR = 9

# encode data bits
DATA_BITS = 11
DATA_BITS_MINI = 6

# codeword bits
CODEWORD_BITS = 8

# the data capacity of qr code on specific mode and correction level
DATA_CAPACITY = {2: {'Alphanumeric': {'L': 47, 'M': 38, 'Q': 29, 'H': 20}}}

# number of max data bits
MAX_DATA_BITS = {'L': 272, 'M': 224, 'Q': 176, 'H': 128}

# padding bytes
PADDING_BYTES = ['11101100', '00010001']

# Error correction code per block (c, k, r)
# c = total number of codewords
# k = number of data codewords,
# r = error correction capacity
ERROR_CORR_PER_BLOCK = {'L': (44, 34, 4), 'M': (44, 28, 8),
                        'Q': (44, 22, 11), 'H': (44, 16, 14)}

# Number of error correction codewords
NUM_OF_CORR_CODEWORDS = {'L': 10, 'M': 16, 'Q': 22, 'H': 28}

# Value of p
VALLUE_OF_P = {'L': 2, 'M': 0, 'Q': 0, 'H': 0}

# Galois Field exp table and log table
GF_EXP = [1] * 512
GF_LOG = [0] * 256

# draw direction
UPWARDS = 0
DOWNWARDS = 1
