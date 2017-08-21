import wave
import aifc
import struct
from collections import namedtuple


try:
    xrange
except NameError:
    # in Python3 xrange has been renamed to range
    xrange = range

Point = namedtuple('Point', ['x', 'y'])

# The Python 2.7 version of the wave module does not use a namedtuple as the
# return value of getparams(), so we define it here for cross-compatibility
_wave_params = namedtuple('_wave_params',
                          'nchannels sampwidth framerate nframes comptype compname')


class WavDecoder(object):
    """
    A wrapper around the standard library's wave module to make reading from
    WAV files easier. It decodes the raw bytes into a list of Points, one list
    for each channel

    It also optionally scales the data to a maximum width and hight (the height
    according to the bitdepth of the samples).

    It also optionally downsamples the data if downtoss is set. One sample out
    of every downtoss samples is kept and the rest are tossed out. This is a
    very brutal form of downsampling which will both remove high frequencies
    and cause aliasing (no low-pass filtering is applied before decimating).

    Use it as a context manager.
    """
    def __init__(self, filename, decoder_class=wave, endchar=None,
                 max_width=0, max_height=0, bs=0, downtoss=1):
        """
        bs is block size as number of frames to stream from disk on every call
        to next() (a frame is a sample * nchannels). If bs == 0, then the
        entire WAV file will be read into memory before being re-serialized.
        """
        self._filename = filename
        self.decoder = decoder_class
        self.max_width = max_width
        self.max_height = max_height
        self.bs = bs
        self._downtoss = downtoss
        if endchar is None:
            if self.decoder == aifc:
                # AIFF is encoded big-endian
                self.endchar = ">"
            else:
                self.endchar = "<"
        self._reset()

    def __iter__(self):
        return self

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _reset(self):
        self._wav_file = None
        self.params = None
        self.width = None
        self.height = None
        self._samp_fmt = None
        # index keeps track of the next frame in the _wav_file
        # We can't rely on the Wav_read.tell() because the docs say it is
        # implementation specific.
        self.index = None

    def open(self):
        wf = self.decoder.open(self._filename, 'rb')
        self._wav_file = wf
        self.index = 0
        self.params = _wave_params(*wf.getparams())
        if self.max_width <= 0:
            # if max_width is set to 0 then use full width of waveform
            self.width = self.params.nframes
        else:
            self.width = min(self.max_width, self.params.nframes)

        if self.max_height <=0:
            # If max-height is set at 0, then use full bitdepth
            self.height = self.params.sampwidth * 8 -1
        else:
            self.height = min(self.max_height,
                              2**(self.params.sampwidth * 8 - 1))
        samp_fmt = self.struct_fmt_char

        if samp_fmt is None:
            raise ValueError("Unsupported file type.")
        self._samp_fmt = samp_fmt

    def close(self):
        self._wav_file.close()
        self._reset()

    def scale_x(self, x):
        # (explicit cast to float needed for Python2)
        return x*min(1.0, float(self.width)/self.params.nframes)

    def scale_y(self, y):
        # important to multiply by height before dividing so we don't
        # lose floating point resolution on very small numbers:
        # multiply by negative height because in the SVG coordinate system
        # positive numbers move down
        sampwidth = self.params.sampwidth
        bitdepth = sampwidth * 8
        divisor = 2**(bitdepth-1)
        if sampwidth == 1 and self.decoder == wave:
            y -= divisor
        return (y * -self.height/2)/divisor

    @property
    def struct_fmt_char(self):
        """
        Calculates the character to use with struct.unpack() to decode sample
        bytes compatible with the WAV files sample width.

        Only 8-bit (unsigned), 16-bit, and 32-bit (both signed) PCM files are
        supported. Returns None if an unsupported sampwidth is provided.

        see: https://docs.python.org/library/struct.html
        """
        sampwidth = self.params.sampwidth
        if sampwidth == 1 and self.decoder == wave:
            # 8 bit wav samples are unsigned
            return 'B'
        elif sampwidth == 1:
            return 'b'
        elif sampwidth == 2:
            # signed 16-bit
            return 'h'
        elif sampwidth == 4:
            # signed 32-bit
            return 'i'
        else:
            return None

    def next(self):
        """
        Read and decode the next bs frames and return channel-separated data.

        Returns data as a list of Points for each channel:
        [
         [Point(x=1, y=4), ...] # chan 1
         [Point(x=3, y=435), ..] # chan 2
        ]
        """
        if self._wav_file is None:
            # Likely user didn't open(), do it for them:
            #TODO: log this
            self.open()
        p = self.params
        if self.bs == 0:
            # Read all frames into memory if bs == 0:
            frames = p.nframes
        else:
            frames = self.bs
        next_index = self.index + frames

        # check bounds
        if next_index > p.nframes:
            frames = p.nframes - self.index
            if frames <= 0:
                # TODO: log this
                raise StopIteration

        wav_bytes = self._wav_file.readframes(frames)

        fmt = self._samp_fmt

        data = struct.unpack('%s%d%s' %
                             (self.endchar, p.nchannels * frames, fmt),
                             wav_bytes)

        # Extract the tuples of integers into a list of Points for each channel:
        start = self.index + 1
        sep_data = []
        for chan in xrange(0, p.nchannels):
            chan_data = data[chan::p.nchannels]
            # downsample:
            chan_data = chan_data[::self._downtoss]
            chan_points = []
            for i, sample in enumerate(chan_data):
                y_offset = self.height*chan
                x = self.scale_x(i + start)
                y = self.scale_y(sample) + y_offset + self.height/2
                chan_points.append(Point(x, y))
            sep_data.append(chan_points)
        self.index += frames
        return sep_data

    # alias for python3-style iterators:
    __next__ = next
