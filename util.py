#-*- coding:utf-8 -*-
# utilities used by QR code generator


# Galois Field exp table and log table
GF_EXP = [1] * 512
GF_LOG = [0] * 256


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


def RS_encode(msg_in, nsym):
    """Generate Reed Solemn correction code

        Args:
            msg_in: the data list, every element is either 0 or 1
            nsym: the length of required RS correction code

        Returns:
            A binary list which contain the origin data and the 
              correction code
    """
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
    return msg_out


def BCH_encode(data, nsym):
    """Generate BCH correction code

        Args:
            msg_in: the binary string
            nsym: the length of required BCH correction code

        Returns:
            A binary string which contain the origin data and the 
              correction code
    """
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
