#-*- coding:utf-8 -*-
# Draw QR code image by given formated data stream


class Draw_QR:

    """Draw QR code image by given formated data stream

    Attributes:
        data: formated data, a binary list where every element is a either 0 or 1

    """

    def __init__(self, data):
        super(Draw_QR, self).__init__()
        self.data = data
