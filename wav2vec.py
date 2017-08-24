#!/usr/bin/env python
import sys
from wav2vec import *


def main():
    aparser = argparse.ArgumentParser(description="Convert wav files to SVG graphics",
                                      epilog="The SVG output is sent to stdout.")
    aparser.add_argument("filename", help="The WAV file to read")
    aparser.add_argument("--width", default=1000, type=int, help="Maximum width of generated SVG (graphic will be scaled down to this size in px)")
    aparser.add_argument("--downtoss", default=1, type=int, help="Downsize by keeping only 1 out of every N samples.", metavar="N")
    aparser.add_argument("--height", default=500, type=int, help=("Maximum height of generated SVG (graphic will be scaled down to this size in px). Note that this scales according to the highest possible amplitude (given the sample bit depth), not the highest amplitude that actually occurs in the data."))

    args = aparser.parse_args()

    # setup logging
    logging.basicConfig(level=logging.DEBUG)

    # Test whether WAV or AIFF
    decoder_class = wave
    sndtype = sndhdr.what(args.filename)[0]
    if sndtype == 'aiff' or sndtype == 'aifc':
        import aifc
        decoder_class = aifc

    decoder = WavDecoder(args.filename, decoder_class=decoder_class, bs=0,
                         max_width=args.width, max_height=args.height,
                         downtoss=args.downtoss)
    formatter = SVGFormatter(decoder)
    #formatter = CSVFormatter(decoder)
    formatter.output(sys.stdout)
    #print(formatter)

if __name__ == "__main__":
    import argparse
    import sndhdr
    import wave
    import logging
    main()
