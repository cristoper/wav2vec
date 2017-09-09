import sys
from .formatter import formatters
from . import WavDecoder
import argparse
import sndhdr
import wave
import logging


def main():
    aparser = argparse.ArgumentParser(description=("Convert WAV and AIFF files "
                                                   "to vector (SVG, PostScript,"
                                                   " CVS) graphics."),
                                      epilog="The output is sent to stdout.")
    aparser.add_argument("filename", help="The WAV file to read")
    aparser.add_argument("--format", "-f", default="SVG", type=str,
                         choices=formatters.keys(),
                         help="The output format, one of: SVG, CSV, PostScript. Default is SVG.")
    aparser.add_argument("--width", default=1000,
                         type=int, help=("Maximum width of generated SVG "
                                         "(graphic will be scaled down to "
                                         "this size in px)"))
    aparser.add_argument("--height", default=500,
                         type=int, help="Maximum height of generated SVG (graphic will be scaled down to this size in px). Note that this scales according to the highest possible amplitude (given the sample bit depth), not the highest amplitude that actually occurs in the data.")
    aparser.add_argument("--stream", metavar="BS", default=0, type=int,
                         help=("Stream the input file size in chunks (of BS "
                               "number of frames at a time) and process/format "
                               "each chunk separately. Useful for conserving "
                               "memory when processing large files, but note "
                               "that multi-channel paths will be split up into "
                               "BS-sized chunks. By default BS=0, which causes "
                               "the entire file to be read into memory before "
                               "processing."))
    aparser.add_argument("--downtoss", default=1,
                         type=int, help="Downsample by keeping only 1 out of every N samples.", metavar="N")
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

    # setup decoder and formatter
    decoder = WavDecoder(args.filename, decoder_class=decoder_class, bs=args.stream,
                         max_width=args.width, max_height=args.height,
                         downtoss=args.downtoss)
    formatter_class = formatters[args.format]
    logging.debug("formatter_class: %s" % formatter_class)
    formatter = formatter_class(decoder)

    # decode and format
    formatter.output(sys.stdout)
