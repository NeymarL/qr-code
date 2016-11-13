# QR Code Generator

This is a demo QR code generator, I only implement mode `Alphanumeric` with version `2`.

## Usage

```
git clone https://github.com/NeymarL/qr_code.git
cd qr_code
chmod 755 main.py
./main.py -d "The data you want to encode" -e "Q"
```

**Command line option**

* `-h` list usage
* `-d <data>` The data you want to encode
* `-e <level>` The error correction level, one of {'L', 'M', 'Q', 'H'}
* `-s <path>` Save the image, `path` is the path you want to save, include file name
* `--notshow` Do not show the image
* `--size <size>` Change the image size

## Requirements

* numpy
* matplotlib

## Code


## More

![My Website](QR_CODE.png)

