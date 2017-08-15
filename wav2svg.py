import wave
import struct
from collections import namedtuple

try:
    xrange
except NameError:
    # in Python3 xrange has been renamed to range
    xrange = range

Point = namedtuple('Point', ['x', 'y'])

def read_wav_data(filename):
    """
    Open wave file and read all data frames into memory. (Python 2.7 does not
    support using wave.open as a context manager, so instead we manually open
    the file and then call wave.open on it.)

    Returns a 7-tuple:
        (databytes, nchannels, sampwidth, framerate, nframes, comptype, compname)

    The first element is the string of bytes containing the actual wave data
    frames. It can be converted to integers using the struct.unpack() method
    from the standard library.

    The other elements are as documented in the wave module:
    https://docs.python.org/3/library/wave.html
    """
    with open(filename, mode='rb') as f:
        wf = wave.open(f)

        # get wav info
        (nchannels, sampwidth, framerate, nframes, comptype, compname) = \
                wf.getparams()

        # read entire file into memory
        wav_data = wf.readframes(nframes)
        wf.close()
    return (wav_data, nchannels, sampwidth, framerate, nframes, comptype, compname)

def struct_fmt_char(sampwidth):
    """
    Takes a sample width (in bytes) and returns the character character to use
    with struct.unpack() to decode the sample into an integer.

    Only 8-bit (unsigned), 16-bit, and 32-bit (both signed) PCM files are
    supported. Returns None if an unsupported sampwidth is provided.
    
    see: https://docs.python.org/library/struct.html
    """
    if sampwidth == 1:
        # 8 bit wav samples are unsigned
        return 'b'
    elif sampwidth == 2:
        # signed 16-bit
        return 'h'
    elif sampwidth == 4:
        # signed 32-bit
        return 'i'
    else:
        return None

def extract_scale_chan_data(data, chan, width, height, nchannels=2, downtoss=1):
    """
    Takes a tuple of frame data (with interleaved channels), the number of
    channels, a channel number, a maximum width, a maximum height, a
    downsampling figure (we keep 1 out of every downtoss samples), and returns
    a list of points which make up the scaled data for the channel-th channel.
    """
    points = []
    # use slicing to isolate channel data:
    chan_data = data[chan::nchannels]
    # downsample:
    chan_data = chan_data[::downtoss]

    for sample in xrange(0, len(chan_data)):
        chan_offset = height*chan
        x_scale = min(1.0, width/len(chan_data))
        x = sample*x_scale*downtoss
        # important to multiply by height before dividing so we don't
        # lose floating point resolution on very small numbers:
        y = (data[sample] * -height/2)/2**(nbits-1) + chan_offset + height/2
        points.append(Point(x, y))
    return points

def paths_to_svg(paths, width, height):
    """
    Takes a list of paths (which are lists of Points) and returns a string
    containing SVG defining a polyline for each path.
    """
    # We set the width and height so that the initial viewport matches the
    # combined dimensions of all waveforms.
    nchannels = len(paths)
    svg_str = '<svg width="%d" height="%d" xmlns="http://www.w3.org/2000/svg" version="1.1">'\
            % (width, nchannels*height)

    # print a polyline for each channel
    for path in paths:
        svg_str += '<polyline stroke="black" fill="none" points="'
        for p in path:
            svg_str += ' %f, %f' % (p.x, p.y)
        svg_str += '" />'
    svg_str += '</svg>'
    return svg_str

if __name__ == "__main__":
    import argparse
    aparser = argparse.ArgumentParser(description="Convert wav files to SVG graphics",
            epilog="The SVG output is sent to stdout.")
    aparser.add_argument("filename", help="The WAV file to read")
    aparser.add_argument("--width", default=1000, type=int, help="Maximum width of generated SVG (graphic will be scaled down to this size in px)")
    aparser.add_argument("--downtoss", default=1, type=int, help="Downsize by keeping only 1 out of every N samples.", metavar="N")
    aparser.add_argument("--height", default=500, type=int, help=("Maximum height of generated SVG (graphic will be scaled down to this size in px). Note that this scales according to the highest possible amplitude (given the sample bit depth), not the highest amplitude that actually occurs in the data."))

    args = aparser.parse_args()

    (wav_data, nchannels, sampwidth, framerate, nframes, comptype, compname) = \
            read_wav_data(args.filename)
    nbits = sampwidth * 8

    # Select the correct struct.unpack() format string character
    # based on the sample size
    samp_fmt = struct_fmt_char(sampwidth)
    if samp_fmt is None:
        import sys
        sys.exit("File is not 8-bit unsigned nor 16- nor 32-bit signed PCM .wav"\
                " format. Those are the only supported formats.")

    # convert bytes to ints
    # This returns one long tuple of ints; wav channel data is interleaved
    # so that left = data[i+0], right=data[i+1], etc
    # (leftsample0, rightsample0, leftsample1, rightsample1, ...)
    data = struct.unpack('<%d%s' % (nchannels * nframes, samp_fmt), wav_data)

    # Build the path points for each channel from data frames:
    paths = []
    for chan in xrange(0, nchannels):
        points = extract_scale_chan_data(data, chan, args.width, args.height,
                nchannels, args.downtoss)
        paths.append(points)

    svg_str = paths_to_svg(paths, args.width, args.height)
    print(svg_str)
