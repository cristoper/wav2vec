#!/usr/bin/env python
import sys
from wav2vec.formatter import formatters
from wav2vec import WavDecoder


def main():
    aparser = argparse.ArgumentParser(description="Convert wav files to SVG graphics",
                                      epilog="The SVG output is sent to stdout.")
    aparser.add_argument("filename", help="The WAV file to read")
    aparser.add_argument("--width", default=1000,
                         type=int, help=("Maximum width of generated SVG "
                                         "(graphic will be scaled down to "
                                         "this size in px)"))
    aparser.add_argument("--downtoss", default=1,
                         type=int, help="Downsize by keeping only 1 out of every N samples.", metavar="N")
    aparser.add_argument("--height", default=500,
                         type=int, help="Maximum height of generated SVG (graphic will be scaled down to this size in px). Note that this scales according to the highest possible amplitude (given the sample bit depth), not the highest amplitude that actually occurs in the data.")
    aparser.add_argument("--format", "-f", default="SVG", type=str,
                         choices=formatters.keys(),
                         help="The output format, one of: SVG, CSV, PostScript. Default is SVG.")
    aparser.add_argument("--log", dest="loglevel",
                         choices=['DEBUG', 'INFO', 'WARNING', 'ERROR',
                                  'CRITICAL'], help="Set the logging level.",
                         default='ERROR', type=str)

    args = aparser.parse_args()

    # setup logging
    logging.basicConfig(level=logging.getLevelName(args.loglevel))

    # Test whether WAV or AIFF
    decoder_class = wave
    sndtype = sndhdr.what(args.filename)[0]
    if sndtype == 'aiff' or sndtype == 'aifc':
        import aifc
        decoder_class = aifc

    decoder = WavDecoder(args.filename, decoder_class=decoder_class, bs=0,
                         max_width=args.width, max_height=args.height,
                         downtoss=args.downtoss)
    formatter_class = formatters[args.format]
    logging.debug("formatter_class: %s" % formatter_class)
    formatter = formatter_class(decoder)
    formatter.output(sys.stdout)

if __name__ == "__main__":
    import argparse
    import sndhdr
    import wave
    import logging
    main()
