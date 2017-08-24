from .Formatter import Formatter


class CSVFormatter(Formatter):
    """
    """
    backend = "CSV"

    def doc_front_matter(self, *args):
        return super(CSVFormatter, self).doc_front_matter()

    def doc_end_matter(self, *args):
        return ''

    def path_front_matter(self, chan_num):
        csv = "Channel #%d\n" % (chan_num + 1)
        csv += "X, Y\n"
        return csv

    def path_end_matter(self, chan_num):
        return ''

    def points_to_str(self, sample):
        return "%f, %f\n" % sample


class SVGFormatter(Formatter):
    """
    Convert paths to SVG.
    """
    def doc_front_matter(self, params):
        nchannels = params.nchannels
        width = 'width="%d"' % self.decoder.width
        height = 'height="%d"' % (self.decoder.height*nchannels)
        svg = '<svg %s %s xmlns="http://www.w3.org/2000/svg" version="1.1">'\
            % (width, height)
        return svg

    def doc_end_matter(self, *args):
        return '</svg>'

    def path_front_matter(self, chan):
        return '<polyline stroke="black" stroke-linecap="round"'\
            ' stroke-linejoin="round" fill="none" points="'

    def path_end_matter(self, chan):
        return '" />'

    def points_to_str(self, sample, chan):
        # multiply by negative height because in the SVG coordinate system
        # positive numbers move down
        (x, y) = sample.x, -1*sample.y + self.y_offset(chan)
        return ' %f, %f' % (x, y)
