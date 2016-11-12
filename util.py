#-*- coding:utf-8 -*-
# utilities used by QR code generator


def trans_to_binary(num, bits):
    """Transform int valuable to binary string

    Args:
        num: int valuable, e.g. 10
        bits: the number of bits of the binary string, e.g. 4

    Returns:
        A string that represent the binary value of `num`, e.g. '1010'

    """
    binary = bin(num)[2:]
    if len(binary) < bits:
        length = bits - len(binary)
        for i in range(length):
            binary = '0' + binary
    elif len(binary) > bits:
        binary = binary[len(binary) - bits:]
    return binary


def trans_bin_to_int(binary):
    """Transform binary string to list of demical

    Every 8-bit binary number take as a demical value,
    transform to lists of demical.

    Args:
        binary: the binary string whose length must be divisible by 8
          e.g. '01001010'

    Returns:
        The list of demical value, e.g. [4, 10]

    """
    dem_list = []
    for i in xrange(0, len(binary) / 8):
        dem_list.append(int(binary[i * 8: (i + 1) * 8], 2))
    return dem_list


def xor(bin1, bin2):
    """Xor operation for every bit int bin1 and bin2

    Args:
        bin1: the first oprand(binary string), e.g. '1010'
        bin2: the second oprand, the two string must have the same length
          e.g. '0011'

    Returns:
        The result string, e.g. '1001'

    """
    n = len(bin1)
    dem1 = int(bin1, 2)
    dem2 = int(bin2, 2)
    result = dem1 ^ dem2
    return trans_to_binary(result, n)
