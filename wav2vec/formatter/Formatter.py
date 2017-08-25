"""
This module contains the abstract base class which formatters inheret from.

New formatters need only to override the five abstract methods.
"""

import abc
import sys
import logging

logger = logging.getLogger(__name__)

try:
    from StringIO import StringIO
except ImportError:
    # Python 3:
    from io import StringIO


class Formatter(object):
    """
    Abstract base class which all formatters must subclass.

    It takes a WavDecoder object in its constructor which is what is responsible
    for reading/decoding data from a WAV or AIFF file.

    The output() method will stream output to a file (stdout by default), but
    the entire output string can be captured using the __str__() method.

    >>> wd = WavDecoder("filename")
    >>> svgformatter = SVGFormatter(wd)
    >>> svgformatter.output() # outputs SVG to stdout
    >>> svg_str = str(svgformatter) # get SVG as a string
    """
    __metaclass__ = abc.ABCMeta

    # name of the formatter (subclasses should override this)
    backend = "Abstract"

    @abc.abstractmethod
    def doc_front_matter(self, params):
        """
        This method should return a string which is output once at the very
        beginning of the formatted output.

        params: a tuple of parameters (the same as that returned by
            Wave_read.getparams()
        """
        return self.backend + "\n---"

    @abc.abstractmethod
    def doc_end_matter(self, params):
        """
        This method should return a string which is output once at the very
        end of the formatted output.

        params: a tuple of parameters (the same as that returned by
            Wave_read.getparams()
        """
        return ''

    @abc.abstractmethod
    def path_front_matter(self, first, chan_num):
        """
        This method should return a string which is output at the BEGINNING of
        the data points every time a path (there is one path for each channel)
        is started or resumed (resumed in the case the decoder is reading data
        in chunked from the waveform file -- that is, when bs > 0)

        chan_num (int): The channel number corresponding to the current path
        first_samp (Point): The first sample in this segment of the path
        """
        return "Channel #%d" % chan_num

    @abc.abstractmethod
    def path_end_matter(self, last, chan_num):
        """
        This method should return a string which is output at the END of the
        data points every time a path (there is one path for each channel) is
        started or resumed (resumed in the case the decoder is reading data in
        chunked from the waveform file -- that is, when bs > 0)

        chan_num (int): The channel number corresponding to the current path
        """
        return ''

    @abc.abstractmethod
    def points_to_str(self, sample, chan):
        """
        This method takes the actual sample data and outputs a string in the
        required format.

        sample (Point): A tuple (x,y) containing the sample data.
        chan (int): The channel number corresponding to the current sample.
        """
        return "%f, %f" % sample

    def __init__(self, decoder):
        """
        Args:
            decoder (WavDecoder): the decoder to use to read/decode data which
                is then formatted by this object.
        """
        self.decoder = decoder
        logger.debug("Initialized formatter with %s" % decoder)

    def y_offset(self, chan):
        """
        A convenience for formatters who want to stack channels vertically:
            returns an offset to be added to each y-component.
        """
        return self.decoder.height*chan + self.decoder.height/2.0

    def output(self, outfile=sys.stdout):
        """
        outfile (filehandle): The file to output formatted data to.
        """
        logger.debug("Outputting data to %s" % outfile)
        with self.decoder as data:
            outfile.write(self.doc_front_matter(self.decoder.params))
            for paths in data:
                is_opening = (self.decoder.bs == 0) or\
                    (self.decoder.index - self.decoder.bs == 0)
                is_closing = self.decoder.index == self.decoder.params.nframes
                nchannels = len(paths)
                for chan, chan_data in enumerate(paths):
                    if is_opening or nchannels > 1:
                        # beginning of channel chunk
                        sample = chan_data[0]
                        outfile.write(self.path_front_matter(sample, chan))
                    for sample in chan_data:
                        outfile.write(self.points_to_str(sample, chan))
                    if is_closing or nchannels > 1:
                        # end ofchannel chunk
                        outfile.write(self.path_end_matter(sample, chan))
            outfile.write(self.doc_end_matter(self.decoder.params))

    def __str__(self):
        string = StringIO()
        self.output(string)
        return string.getvalue()
    __repr__ = __str__
