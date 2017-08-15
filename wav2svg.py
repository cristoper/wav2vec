import wave
import struct
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])

try:
    xrange
except NameError:
    # in Python3 xrange has been renamed to range
    xrange = range

if __name__ == "__main__":
    import argparse
    aparser = argparse.ArgumentParser(description="Convert wav (.wav and .aiff) files to SVG graphics")
    aparser.add_argument("filename", help="The WAV file to read")
    aparser.add_argument("--width", default=1000, type=int, help="Maximum width of generated SVG (graphic will be scaled down to this size in px)")
    aparser.add_argument("--downtoss", default=1, type=int, help="Downsize by keeping only 1 out of every N samples.", metavar="n")
    aparser.add_argument("--height", default=500, type=int, help=("Maximum height of generated SVG (graphic will be scaled down to this size in px). Note that this scales the highest possible amplitude (given the sample bit depth), not the highest amplitude that actually occurs in the data."))

    args = aparser.parse_args()

    # Open wave file and start converting samples to SVG points
    # (Python 2.7 does not support using wave.open as a context manager)
    with open(args.filename, mode='rb') as file:
        wf = wave.open(file)

        # get wav info
        (nchannels, sampwidth, framerate, nframes, comptype, compname) = \
                wf.getparams()
        nbits = sampwidth * 8

        # read entire file into memory
        wav_data = wf.readframes(nframes)
        wf.close()

    # Select the correct struct.unpack() format string character
    # based on the sample size
    # see: https://docs.python.org/library/struct.html
    if sampwidth == 1:
        # 8 bit wav samples are unsigned
        samp_fmt = 'b'
    elif sampwidth == 2:
        # signed 16-bit
        samp_fmt = 'h'
    elif sampwidth == 4:
        # signed 32-bit
        samp_fmt = 'i'
    else:
        import sys
        sys.exit("File is not 8-bit unsigned nor 16- nor 32-bit signed PCM .wav"\
                " format. Those are the only supported formats.")

    # convert bytes to ints
    # This returns one long tuple of ints, but wav channel data is interleaved
    # so that left = data[i+0], right=data[i+1], etc
    # (leftsample0, rightsample0, leftsample1, rightsample1, ...)
    data = struct.unpack('<%d%s' % (nchannels * nframes, samp_fmt), wav_data)
    

    # There is a path for each channel, and each path is an array of points
    paths = []

    # Build the path points for each channel from data frames:
    x_scale = min(1.0, args.width/nframes)
    for chan in xrange(0, nchannels):
        points = []
        # use slicing to isolate channel data:
        chan_data = data[chan::nchannels]
        # downsample:
        chan_data = chan_data[::args.downtoss]

        for sample in xrange(0, len(chan_data)):
            chan_offset = args.height*chan
            x = sample*x_scale*args.downtoss
            # important to multiply by args.height before dividing so we don't
            # lose floating point resolution on very small numbers:
            y = (data[sample] * -args.height/2)/2**(nbits-1) + chan_offset + args.height/2
            points.append(Point(x, y))
        paths.append(points)

    # print SVG
    svg_str = '<svg width="%d" height="%d" xmlns="http://www.w3.org/2000/svg" version="1.1">'\
            % (args.width, 2*args.height)

    # print a polyline for each channel
    for path in paths:
        svg_str += '<polyline stroke="black" fill="none" points="'
        for p in path:
            svg_str += ' %f, %f' % (p.x, p.y)
        svg_str += '" />'

    svg_str += '</svg>'
    print(svg_str)
