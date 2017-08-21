import abc
import sys

try:
    from StringIO import StringIO
except ImportError:
    # Python 3:
    from io import StringIO


class Serializer(object):
    """
    Abstract base class which all serializers must subclass.
    """
    __metaclass__ = abc.ABCMeta

    backend = "Abstract"

    @abc.abstractmethod
    def doc_front_matter(self, params):
        return self.backend + "\n---"

    @abc.abstractmethod
    def doc_end_matter(self, params):
        return ''

    @abc.abstractmethod
    def path_front_matter(self, chan_num):
        return "Channel #%d" % chan_num

    @abc.abstractmethod
    def path_end_matter(self, chan_num):
        return ''

    @abc.abstractmethod
    def points_to_str(self, sample):
        return "%f, %f" % sample

    def __init__(self, decoder):
        self.decoder = decoder

    def output(self, outfile=sys.stdout):
        """
        path is a list of Point
        """

        with self.decoder as data:
            outfile.write(self.doc_front_matter(self.decoder.params))
            for paths in data:
                is_opening = self.decoder.index - self.decoder.bs == 0
                is_closing = self.decoder.index == self.decoder.params.nframes
                nchannels = len(paths)
                for chan, chan_data in enumerate(paths):
                    if is_opening or nchannels > 1:
                        outfile.write(self.path_front_matter(chan))
                    for sample in chan_data:
                        outfile.write(self.points_to_str(sample))
                    if is_closing or nchannels > 1:
                        outfile.write(self.path_end_matter(chan))
            outfile.write(self.doc_end_matter(self.decoder.params))

    def __str__(self):
        string = StringIO()
        self.output(string)
        return string.getvalue()
    __repr__ = __str__
