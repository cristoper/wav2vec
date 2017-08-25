from .Formatter import Formatter
from ..WavDecoder import Point


class CSVFormatter(Formatter):
    """
    """
    backend = "CSV"

    def doc_front_matter(self, *args):
        return super(CSVFormatter, self).doc_front_matter(*args)

    def doc_end_matter(self, *args):
        return ''

    def path_front_matter(self, first, chan_num):
        csv = "Channel #%d\n" % (chan_num + 1)
        csv += "X, Y\n"
        return csv

    def path_end_matter(self, last, chan_num):
        return ''

    def points_to_str(self, sample, chan):
        return "%f, %f\n" % sample


class SVGFormatter(Formatter):
    """
    Convert paths to SVG.
    """
    backend = 'SVG'

    def doc_front_matter(self, params):
        nchannels = params.nchannels
        width = 'width="%d"' % self.decoder.width
        height = 'height="%d"' % (self.decoder.height*nchannels)
        svg = '<svg %s %s xmlns="http://www.w3.org/2000/svg" version="1.1">'\
            % (width, height)
        return svg

    def doc_end_matter(self, *args):
        return '</svg>'

    def path_front_matter(self, first, chan):
        return '<polyline stroke="black" stroke-linecap="round"'\
            ' stroke-linejoin="round" fill="none" points="'

    def path_end_matter(self, last, chan):
        return '" />'

    def points_to_str(self, sample, chan):
        # multiply by negative height because in the SVG coordinate system
        # positive numbers move down
        (x, y) = sample.x, -1*sample.y + self.y_offset(chan)
        return ' %f, %f' % (x, y)


class PSFormatter(Formatter):
    """
    Convert paths to PostScript.
    """
    backend = 'PostScript'

    def doc_front_matter(self, params):
        # This dict tracks the last point in each channel chunk so we can moveto
        # back to it at the beginning of the next chunk
        self.last_point = {}
        nchannels = params.nchannels
        height = self.decoder.height*nchannels
        width = self.decoder.width
        documentmedia = "%%%%DocumentMedia: wxh %d %d" % (width, height)
        setpagedevice = "<< /PageSize [%d %d] >> setpagedevice"\
            % (width, height)
        ps = "%!PS"
        ps = ps + "\n" + documentmedia + "\n" + setpagedevice
        # We translate so that origin is at top-left
        ps = ps + "\n" + "newpath\n0 %d translate\n" % height
        return ps

    def doc_end_matter(self, *args):
        return "stroke\nshowpage"

    def path_front_matter(self, first, chan):
        last = self.last_point.get(chan, Point(0, 0))
        (x, y) = last.x, last.y - self.y_offset(chan)
        return "%f %f moveto\n" % (x, y)

    def path_end_matter(self, last, chan):
        self.last_point[chan] = last
        return ""

    def points_to_str(self, sample, chan):
        (x, y) = sample.x, sample.y - self.y_offset(chan)
        return "%f %f lineto\n" % (x, y)
