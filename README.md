# WSI-WebP-Converter
# Jan Buchholz`s Bachelor Thesis

Contains a python script to convert Aperio SVS TIFF files to WebP compressed SVS-like bigTIFF.

## converter.py:

Requirements: 
- pyvips (working libvips binaries required, follow pyvips instructions at: https://pypi.org/project/pyvips/)
- tifftools
- openslide binaries with webp-support (included)

Storage: Size of biggest uncompressed image data (for stitching) + additional storage for compression output

## Using the script

Before running: 
- Set Openslide binary path in converter.py
- set webp/jpeg compression attributes (Quality)

usage: `converter.py [-h] [-i INPUT] [-o DEST] [-tw WIDTH] [-th HEIGHT] [-c COMP]`

options:
  - `-h, --help`:            show this help message and exit

  - `-i INPUT, --input INPUT`:        a path to a file/directory to be processed
  - `-o DEST, --out DEST`:   output directory
  - `-tw WIDTH`:           tile width (default: 240)
  - `-th HEIGHT`:            tile height (default: 240)
  - `-c COMP`:               compression type (default: webp, options: webp, jpeg, all)

## Extended Openslide
Prebuilt openslide binaries with webp-support are included.

## Testdata processing
`DeltaE.py`, `filesize.py` and `DeltaE_visualization.py` were used to process and visualize testdata for the separate written theses.
