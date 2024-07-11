# WSI-WebP-Converter
# Jan Buchholz`s Bachelor Thesis

Contains a python script to convert Aperio SVS TIFF files to WebP compressed SVS-like bigTIFF on Windows.

## converter.py:

Requirements: 
- [pyvips](https://pypi.org/project/pyvips/) (working libvips binaries required, follow installation instructions)
- [tifftools](https://pypi.org/project/tifftools/)
- [openslide](https://pypi.org/project/openslide-python/) (OpenSlide binaries required)

Storage: Size of biggest uncompressed image data (for stitching) + additional storage for compression output

## Using the script

Before running: 
- Remove placeholder file from Input folder
- Set OpenSlide binary path in converter.py
- set webp/jpeg compression attributes (Quality)

usage: `converter.py [-h] [-i INPUT] [-o DEST] [-tw WIDTH] [-th HEIGHT] [-c COMP]`

options:
  - `-h, --help`:            show this help message and exit

  - `-i INPUT, --input INPUT`:        a path to a file/directory to be processed
  - `-o DEST, --out DEST`:   output directory
  - `-tw WIDTH`:           tile width (default: 240)
  - `-th HEIGHT`:            tile height (default: 240)
  - `-c COMP`:               compression type (default: webp, options: webp, jpeg)

## Extended Openslide
Prebuilt OpenSlide binaries with webp-support are included.

## Testdata processing
`DeltaE.py`, `filesize.py` and `DeltaE_visualization.py` were used to process and visualize testdata for the separate written theses.
