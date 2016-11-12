#-*- coding:utf-8 -*-
# QR code generator

import numpy as np
import matplotlib.pylab as plt
from util import *

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


def main():
    err_corc_level = 'Q'
    data = 'https://www.liuhe.website'
    version = 2
    generate_gf_table()
    encoded = encode(data, err_corc_level)
    transed = trans_bin_to_int(encoded)
    code = RS_encode(transed,
                     ERROR_CORR_PER_BLOCK[err_corc_level][version] * 2)
    draw_qr_code(code, version, err_corc_level)


def encode(data, err_corc_level):
    encoded_data = []
    data = data.upper()
    for char in data:
        if char >= '0' and char <= '9':
            encoded_data.append(ord(char) - ord('0'))
        elif char >= 'A' and char <= 'Z':
            encoded_data.append(ord(char) - ord('A') + ALPHANUMERIC_TABLE['A'])
        else:
            encoded_data.append(ALPHANUMERIC_TABLE[char])
    # print encoded_data
    # 两两一组，每一组转成11bits的二进制
    bin_encode = ''
    couple = []
    i = 0
    for num in encoded_data:
        if len(couple) == 0:
            couple.append(num)
            if i == len(encoded_data) - 1:
                bin_encode += trans_to_binary(num, DATA_BITS_MINI)
        else:
            tmp = couple[0] * 45 + num
            couple = []
            bin_encode += trans_to_binary(tmp, DATA_BITS)
        i = i + 1
    # print bin_encode
    # add number of characters
    bin_encode = trans_to_binary(len(data), COUNT_INDICATOR) + bin_encode
    # add mode indicator
    bin_encode = trans_to_binary(MODES['Alphanumeric'], MODE_BITS) + bin_encode
    # print bin_encode
    # add ending symbol
    bin_encode += ENDING
    if len(bin_encode) % CODEWORD_BITS != 0:
        length = CODEWORD_BITS - (len(bin_encode) % CODEWORD_BITS)
        for i in range(length):
            bin_encode += '0'
    # add padding bytes
    i = 0
    while len(bin_encode) < MAX_DATA_BITS[err_corc_level]:
        bin_encode += PADDING_BYTES[i]
        i = i + 1
        i = i % 2
    return bin_encode


def RS_encode(msg_in, nsym):
    gen = rs_generator_poly(nsym)
    msg_out = [0] * (len(msg_in) + nsym)
    for i in range(0, len(msg_in)):
        msg_out[i] = msg_in[i]
    for i in range(0, len(msg_in)):
        coef = msg_out[i]
        if coef != 0:
            for j in range(0, len(gen)):
                msg_out[i+j] ^= gf_mul(gen[j], coef)
    for i in range(0, len(msg_in)):
        msg_out[i] = msg_in[i]
    bin_encode = ''
    for msg in msg_out:
        bin_encode += trans_to_binary(msg, CODEWORD_BITS)
    return bin_encode


def BCH_encode(data, nsym):
    gen = [1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1]
    msg_in = [0] * len(data)
    msg_out = [0] * (len(data) + nsym)
    for i in range(0, len(data)):
        msg_in[i] = ord(data[i]) - ord('0')
        msg_out[i] = msg_in[i]
    for i in range(0, len(msg_in)):
        coef = msg_out[i]
        if coef != 0:
            for j in range(0, len(gen)):
                msg_out[i+j] ^= gf_mul(gen[j], coef)
    for i in range(0, len(msg_in)):
        msg_out[i] = msg_in[i]
    # print msg_out
    bin_encode = ''
    for msg in msg_out:
        bin_encode += trans_to_binary(msg, 1)
    return bin_encode


def generate_gf_table():
    x = 1
    for i in range(1, 255):
        x <<= 1
        if x & 0x100:
            x ^= 0x11d
        GF_EXP[i] = x
        GF_LOG[x] = i
    for i in range(255, 512):
        GF_EXP[i] = GF_EXP[i-255]


def gf_mul(x, y):
    if x == 0 or y == 0:
        return 0
    return GF_EXP[GF_LOG[x] + GF_LOG[y]]


def gf_poly_mul(p, q):
    r = [0] * (len(p)+len(q)-1)
    for j in range(0, len(q)):
        for i in range(0, len(p)):
            r[i+j] ^= gf_mul(p[i], q[j])
    return r


def rs_generator_poly(nsym):
    g = [1]
    for i in range(0, nsym):
        g = gf_poly_mul(g, [1, GF_EXP[i]])
    return g


def draw_qr_code(bin_encode, version=2, err_corc_level='Q'):
    qr_code_img = np.zeros([VERSION_TABLE[version], VERSION_TABLE[version]])
    qr_code_flag = np.zeros([VERSION_TABLE[version], VERSION_TABLE[version]])

    draw_pos_detection_pattern(qr_code_img, qr_code_flag)
    draw_alignment_pattern(qr_code_img, qr_code_flag)
    draw_timing_pattern(qr_code_img, qr_code_flag)
    draw_format_information(qr_code_img, err_corc_level, qr_code_flag)
    draw_data(qr_code_img, qr_code_flag, bin_encode)

    # mask
    mask = generate_mask(VERSION_TABLE[version])
    # xor
    for i in xrange(0, VERSION_TABLE[version]):
        for j in xrange(0, VERSION_TABLE[version]):
            qr_code_img[i, j] = int(qr_code_img[i, j]) ^ int(mask[i, j])

    draw_pos_detection_pattern(qr_code_img, qr_code_flag)
    draw_alignment_pattern(qr_code_img, qr_code_flag)
    draw_timing_pattern(qr_code_img, qr_code_flag)
    draw_format_information(qr_code_img, err_corc_level, qr_code_flag)

    plt.figure(figsize=(5, 5))
    plt.imshow(qr_code_img, cmap=plt.cm.gray_r, interpolation='nearest')
    # plt.imshow(mask, cmap=plt.cm.gray_r)
    plt.show()


def draw_pos_detection_pattern(qr_code_img, qr_code_flag):
    pos_det_pattern = np.array(
        [
            [1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1],
            [1, 0, 1, 1, 1, 0, 1],
            [1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1],
        ]
    )
    flag = np.ones([8, 8])
    n = len(qr_code_img)
    # 左上角
    qr_code_img[0: 7, 0: 7] = pos_det_pattern
    qr_code_img[0: 8, 7] = np.zeros([1, 8])
    qr_code_img[7, 0: 8] = np.zeros([1, 8])
    qr_code_flag[0: 8, 0: 8] = flag
    # 左下角
    qr_code_img[n - 7: n, 0: 7] = pos_det_pattern
    qr_code_img[n - 8: n, 7] = np.zeros([1, 8])
    qr_code_img[n - 8, 0: 8] = np.zeros([1, 8])
    qr_code_flag[n - 8: n, 0: 8] = flag
    # 右上角
    qr_code_img[0: 7, n - 7: n] = pos_det_pattern
    qr_code_img[0: 8, n - 8] = np.zeros([1, 8])
    qr_code_img[7, n - 8: n] = np.zeros([1, 8])
    qr_code_flag[0: 8, n - 8: n] = flag


def draw_alignment_pattern(qr_code_img, qr_code_flag):
    align_pattern = np.array(
        [
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 1, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1],
        ]
    )
    flag = np.ones([5, 5])
    n = len(qr_code_img)
    row = 18
    col = 18
    qr_code_img[col - 2: col + 3, row - 2: row + 3] = align_pattern
    qr_code_flag[col - 2: col + 3, row - 2: row + 3] = flag


def draw_timing_pattern(qr_code_img, qr_code_flag):
    timing_pattern = np.array(
        [1, 0, 1, 0, 1, 0, 1, 0, 1]
    )
    flag = np.ones(9)
    n = len(qr_code_img)
    qr_code_img[8: 8 + 9, 6] = timing_pattern
    qr_code_flag[8: 8 + 9, 6] = flag
    qr_code_img[6, 8: 8 + 9] = timing_pattern
    qr_code_flag[6, 8: 8 + 9] = flag


def draw_format_information(qr_code_img, err_corc_level, qr_code_flag):
    indicator = ERROR_CORR_INDICATOR[err_corc_level]
    # mask_pattern = '111'
    mask_pattern = '110'
    BCH_encoded = BCH_encode(indicator + mask_pattern, 10)
    mask = '101010000010010'
    format_info = xor(BCH_encoded, mask)
    format_array = np.array([ord(x) - ord('0') for x in format_info])
    flag = np.ones(len(format_array))
    n = len(qr_code_img)
    # 左上角
    qr_code_img[0:6, 8] = format_array.T[9:][::-1]
    qr_code_img[7:9, 8] = format_array.T[7:9]
    qr_code_img[8, 7] = format_array[6]
    qr_code_img[8, 0:6] = format_array[0:6]
    # flag
    qr_code_flag[0:6, 8] = flag.T[0:6]
    qr_code_flag[7:9, 8] = flag.T[6:8]
    qr_code_flag[8, 7] = flag[8]
    qr_code_flag[8, 0:6] = flag[9:][::-1]
    # 右上角
    qr_code_img[8, n-8:] = format_array[7:]
    qr_code_flag[8, n-8:] = flag[0:8][::-1]
    # 左下角
    qr_code_img[n-7:, 8] = format_array.T[0:7][::-1]
    qr_code_flag[n-7:, 8] = flag.T[8:]
    qr_code_img[n-8, 8] = 1
    qr_code_flag[n-8, 8] = 1


def draw_data(qr_code_img, qr_code_flag, data):
    data_list = np.array([ord(x) - ord('0') for x in data])
    i = len(qr_code_img) - 1
    j = len(qr_code_img) - 1
    n = len(qr_code_img)
    k = 0
    mode = 0
    direction = UPWARDS
    while k < len(data_list):
        if i < n and j < n and qr_code_flag[i, j] == 0:
            qr_code_img[i, j] = data_list[k]
            qr_code_flag[i, j] = 1
            if direction == UPWARDS:
                if mode == 0:
                    j = j - 1
                else:
                    i = i - 1
                    j = j + 1
            else:
                if mode == 0:
                    j = j - 1
                else:
                    i = i + 1
                    j = j + 1
            mode = 1 - mode
        else:
            if i <= 8 and j >= n - 7:
                j = j - 2
                i = i + 1
                direction = DOWNWARDS
            elif i >= n:
                if i == 25 and j == 10:
                    j = j - 2
                    i = 16
                else:
                    j = j - 2
                    i = i - 1
                direction = UPWARDS
            elif j > 16 and j <= 20:
                if i > 18:
                    i = i - 5
                else:
                    i = i + 5
            elif j == 16 and i >= 16:
                j = j - 1
                qr_code_img[i, j] = data_list[k]
                qr_code_flag[i, j] = 1
                if i == 16:
                    j = j + 1
                    mode = 1
                i = i - 1
                mode = 1 - mode
                k = k + 1
            elif i == 6:
                if direction == UPWARDS:
                    i = i - 1
                else:
                    i = i + 1
            elif i < 0:
                i = i + 1
                j = j - 2
                direction = DOWNWARDS
            elif i == 8 and j == 8:
                j = j - 3
                i = i + 1
                direction = DOWNWARDS
            elif i >= 17:
                j = j - 2
                i = i - 1
                direction = UPWARDS
            elif i <= 8:
                j = j - 2
                i = i + 1
                direction = DOWNWARDS
            else:
                break
            k = k - 1

        k = k + 1


def generate_mask(size):
    mask = np.zeros([size, size])
    for i in xrange(0, size):
        for j in xrange(0, size):
            # mask[j, i] = 1 - ((i * j) % 3 + (i + j) % 2) % 2
            if ((i * j) % 2 + (i * j) % 3) % 2 == 0:
                mask[i, j] = 1
            else:
                mask[i, j] = 0
    '''
    for i in xrange(0, 9):
        for j in xrange(0, 9):
            mask[i, j] = 0
    for i in xrange(size - 8, size):
        for j in xrange(0, 9):
            mask[i, j] = 0
    for i in xrange(0, 9):
        for j in xrange(size - 8, size):
            mask[i, j] = 0
    '''
    return mask


if __name__ == '__main__':
    main()
