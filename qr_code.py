#-*- coding:utf-8 -*-
# Generate QR code image

import numpy as np
import matplotlib.pylab as plt
from const import *
from util import *


class QR_Code:

    """Generate QR code and draw its image

    Attributes:
        data: origin data
        version: the version of qr code, from 1 to 17, but now 
          it's just implement version 2
        mode: encode mode, one of {'ECI', 'Numeric', 'Alphanumeric', 'Byte', 
          'Kanji'}, but now it's just implement mode 'Alphanumeric'
        err_corc_level: the error correction level, one of 'L', 'M', 'Q', 'H'
        size: the size of qr code
        mask_pattern: which mask pattern should be used
        encoded: the encoded data
        qr_code_img: a size * size matrix that represent qr code image where 1 
          for dark and 0 for light
        qr_code_flag: a size * size matrix that represent whether a element has 
          been drawn, 1 for true and 0 for false
        qr_code_func: a size * size matrix that represent whether a position 
          in the function region, 1 for true, 0 for false

    """

    def __init__(self, data, mode, version, err_corc_level):
        self.data = data
        self.encoded = ''
        self.mode = mode
        self.version = version
        self.err_corc_level = err_corc_level
        self.mask_pattern = '110'
        self.size = VERSION_TABLE[self.version]
        self.qr_code_img = np.zeros([self.size, self.size])
        self.qr_code_flag = np.zeros([self.size, self.size])
        self.qr_code_func = np.zeros([self.size, self.size])

    def draw(self, show=True, save=False, path='', figsize=5):
        """Draw QR code

        Args:
            show: whether to show the image or not, default is true
            save: whether to save the image or not, default is false,
              if turn on this option, you must pass the path too.
            path: where to save the image, default is empty string, 
              this argument is need only if save is true.
            figsize: the size of generate image

        Raises:
            KeyError: Invalid mode.
            NotImplementedError: It only implements mode 'Alphanumeric'
              with version 2 now.
            ValueError: 
                1. The data is too long that beyond its data capacity
                  corresponding to the error correction level
                2. Save is true but path is a empty string

        """
        # encode data
        generate_gf_table()
        self.encode()
        # draw function region
        self.draw_pos_detection_pattern()
        self.draw_alignment_pattern()
        self.draw_timing_pattern()
        self.draw_format_information()
        # assign function region
        for i in xrange(0, self.size):
            for j in xrange(0, self.size):
                self.qr_code_func[i, j] = self.qr_code_flag[i, j]

        # draw data
        self.draw_data()
        # mask
        mask = self.generate_mask()
        # xor
        for i in xrange(0, self.size):
            for j in xrange(0, self.size):
                self.qr_code_img[i, j] = int(
                    self.qr_code_img[i, j]) ^ int(mask[i, j])
        # generate image
        plt.figure(figsize=(figsize, figsize))
        plt.imshow(self.qr_code_img, cmap=plt.cm.gray_r,
                   interpolation='nearest')
        plt.axis('off')
        if show:
            # show
            plt.show()
        if save:
            if path == '':
                raise ValueError("Require path")
            # plt.savefig(path)
            plt.imsave(fname=path, arr=self.qr_code_img,
                       cmap=plt.cm.gray_r)

    def encode(self):
        # param check
        if self.mode not in MODES:
            raise KeyError("Mode Not Found")
        if MODES[self.mode] != MODES['Alphanumeric']:
            raise NotImplementedError("Mode Not Implement", self.mode)
        if self.version != 2:
            raise NotImplementedError("Version Not Implement", self.version)
        if len(self.data) > DATA_CAPACITY[2][self.mode][self.err_corc_level]:
            raise ValueError("Data is too long")
        encoded_data = []
        self.data = self.data.upper()
        for char in self.data:
            if char >= '0' and char <= '9':
                encoded_data.append(ord(char) - ord('0'))
            elif char >= 'A' and char <= 'Z':
                encoded_data.append(
                    ord(char) - ord('A') + ALPHANUMERIC_TABLE['A'])
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
        # add number of characters
        bin_encode = trans_to_binary(
            len(self.data), COUNT_INDICATOR) + bin_encode
        # add mode indicator
        bin_encode = trans_to_binary(
            MODES[self.mode], MODE_BITS) + bin_encode
        # add ending symbol
        bin_encode += ENDING
        if len(bin_encode) % CODEWORD_BITS != 0:
            length = CODEWORD_BITS - (len(bin_encode) % CODEWORD_BITS)
            for i in range(length):
                bin_encode += '0'
        # add padding bytes
        i = 0
        while len(bin_encode) < MAX_DATA_BITS[self.err_corc_level]:
            bin_encode += PADDING_BYTES[i]
            i = i + 1
            i = i % 2
        transed = trans_bin_to_int(bin_encode)
        msg_out = RS_encode(
            transed,
            ERROR_CORR_PER_BLOCK[self.err_corc_level][self.version] * 2
        )
        self.encoded = ''
        for msg in msg_out:
            self.encoded += trans_to_binary(msg, CODEWORD_BITS)
        self.encoded = np.array([ord(x) - ord('0') for x in self.encoded])

    def draw_pos_detection_pattern(self):
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
        n = len(self.qr_code_img)
        # 左上角
        self.qr_code_img[0: 7, 0: 7] = pos_det_pattern
        self.qr_code_img[0: 8, 7] = np.zeros([1, 8])
        self.qr_code_img[7, 0: 8] = np.zeros([1, 8])
        self.qr_code_flag[0: 8, 0: 8] = flag
        # 左下角
        self.qr_code_img[n - 7: n, 0: 7] = pos_det_pattern
        self.qr_code_img[n - 8: n, 7] = np.zeros([1, 8])
        self.qr_code_img[n - 8, 0: 8] = np.zeros([1, 8])
        self.qr_code_flag[n - 8: n, 0: 8] = flag
        # 右上角
        self.qr_code_img[0: 7, n - 7: n] = pos_det_pattern
        self.qr_code_img[0: 8, n - 8] = np.zeros([1, 8])
        self.qr_code_img[7, n - 8: n] = np.zeros([1, 8])
        self.qr_code_flag[0: 8, n - 8: n] = flag

    def draw_alignment_pattern(self):
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
        n = len(self.qr_code_img)
        row = 18
        col = 18
        self.qr_code_img[col - 2: col + 3, row - 2: row + 3] = align_pattern
        self.qr_code_flag[col - 2: col + 3, row - 2: row + 3] = flag

    def draw_timing_pattern(self):
        timing_pattern = np.array(
            [1, 0, 1, 0, 1, 0, 1, 0, 1]
        )
        flag = np.ones(9)
        n = len(self.qr_code_img)
        self.qr_code_img[8: 8 + 9, 6] = timing_pattern
        self.qr_code_flag[8: 8 + 9, 6] = flag
        self.qr_code_img[6, 8: 8 + 9] = timing_pattern
        self.qr_code_flag[6, 8: 8 + 9] = flag

    def draw_format_information(self):
        indicator = ERROR_CORR_INDICATOR[self.err_corc_level]
        BCH_encoded = BCH_encode(indicator + self.mask_pattern, 10)
        mask = '101010000010010'
        format_info = xor(BCH_encoded, mask)
        format_array = np.array([ord(x) - ord('0') for x in format_info])
        flag = np.ones(len(format_array))
        n = len(self.qr_code_img)
        # 左上角
        self.qr_code_img[0:6, 8] = format_array.T[9:][::-1]
        self.qr_code_img[7:9, 8] = format_array.T[7:9]
        self.qr_code_img[8, 7] = format_array[6]
        self.qr_code_img[8, 0:6] = format_array[0:6]
        # flag
        self.qr_code_flag[0:6, 8] = flag.T[0:6]
        self.qr_code_flag[7:9, 8] = flag.T[6:8]
        self.qr_code_flag[8, 7] = flag[8]
        self.qr_code_flag[8, 0:6] = flag[9:][::-1]
        # 右上角
        self.qr_code_img[8, n-8:] = format_array[7:]
        self.qr_code_flag[8, n-8:] = flag[0:8][::-1]
        # 左下角
        self.qr_code_img[n-7:, 8] = format_array.T[0:7][::-1]
        self.qr_code_flag[n-7:, 8] = flag.T[8:]
        self.qr_code_img[n-8, 8] = 1
        self.qr_code_flag[n-8, 8] = 1

    def draw_data(self):
        i = len(self.qr_code_img) - 1
        j = len(self.qr_code_img) - 1
        n = len(self.qr_code_img)
        k = 0
        mode = 0
        direction = UPWARDS
        while k < len(self.encoded):
            if i < n and j < n and self.qr_code_flag[i, j] == 0:
                self.qr_code_img[i, j] = self.encoded[k]
                self.qr_code_flag[i, j] = 1
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
                    self.qr_code_img[i, j] = self.encoded[k]
                    self.qr_code_flag[i, j] = 1
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

    def generate_mask(self):
        mask = np.zeros([self.size, self.size])
        for i in xrange(0, self.size):
            for j in xrange(0, self.size):
                if self.qr_code_func[i, j] == 1:
                    mask[i, j] = 0
                elif ((i * j) % 2 + (i * j) % 3) % 2 == 0:
                    mask[i, j] = 1
                else:
                    mask[i, j] = 0
        return mask

if __name__ == '__main__':
    data = 'https://www.liuhe.website'
    err_corc_level = 'Q'
    mode = 'Alphanumeric'
    version = 2
    qr_code = QR_Code(data, mode, version, err_corc_level)
    qr_code.draw()
