#!/usr/bin/python
#-*- coding:utf-8 -*-
# Invoke the QR code generator

import getopt
import sys
from qr_code import QR_Code


def main():
    data = ''
    err_corc_level = ''
    mode = 'Alphanumeric'
    version = 2
    show = True
    save = False
    path = ''
    size = 5

    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "hd:e:s:", ["notshow", "size="])
        for opt, arg in opts:
            if opt == '-h':
                usage()
                sys.exit(1)
            if opt == '-d':
                data = arg
            if opt == '-e':
                err_corc_level = arg
            if opt == '--notshow':
                show = False
            if opt == '-s':
                path = arg
            if opt == '--size':
                size = int(arg)
    except getopt.GetoptError:
        usage()
        sys.exit(1)

    if data == '' or err_corc_level == '':
        usage()
        sys.exit(1)
    qr_code = QR_Code(data, mode, version, err_corc_level)
    qr_code.draw(show=show, save=save, path=path, figsize=size)


def usage():
    print "Usage: %s -d <data> -e <level> [-s <path>] [-h] [--notshow]" %\
        sys.argv[0]

if __name__ == '__main__':
    main()
