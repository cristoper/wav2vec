import unittest
from unittest.mock import MagicMock
import wave
import random
from wav2vec import WavDecoder
from math import floor


def build_mock_wave(nchannels=2, sampwidth=2, framerate=44100, nframes=100,
                    comptype="NONE", compname="not compressed", bytes=b'\x4a'):
        mock_wave_read = MagicMock(spec=wave.Wave_read)
        mock_wave_read.getparams.return_value = (nchannels, sampwidth,
                                                 framerate, nframes, comptype,
                                                 compname)

        # Return some bytes
        def mock_readframes(frames):
            return bytes * sampwidth * frames * nchannels
        mock_wave_read.readframes = MagicMock(side_effect=mock_readframes)
        mock_wave = MagicMock(spec=wave)
        mock_wave.open.return_value = mock_wave_read
        return mock_wave


class SetupBase(unittest.TestCase):
    def setUp(self):
        mock_wave = build_mock_wave()
        self.wd = WavDecoder("filename", decoder_class=mock_wave)


class TestInit(SetupBase):
    def test_endchar_for_aiff_is_bigendian(self):
        import aifc
        wd = WavDecoder("filename", decoder_class=aifc)
        self.assertEqual(wd.endchar, ">")


class TestMagic(SetupBase):
    def test_context_opens(self):
        with self.wd:
            pass
        self.wd.decoder.open.assert_called_once_with("filename", "rb")

    def test_context_closes(self):
        with self.wd:
            mock_wf = self.wd._wav_file
        mock_wf.close.assert_called_once_with()


class TestOpenClose(SetupBase):
    def test_open_default_width(self):
        """
        When max_width is 0, the width should be set to the number of frames.
        """
        self.wd.max_width = 0
        self.wd.open()
        self.assertEqual(self.wd.width, self.wd.params.nframes)

    def test_open_default_height(self):
        """
        When max_height is 0, the height should be set to 2**bitdepth - 1
        """
        self.wd.max_height = 0
        self.wd.open()
        bitdepth = self.wd.params.sampwidth * 8
        max_height = 2**bitdepth - 1
        self.assertEqual(self.wd.height, max_height)

    def test_close_closes(self):
        self.wd.open()
        wf = self.wd._wav_file
        self.wd.close()
        wf.close.assert_called_once_with()


class TestScaleMethods(unittest.TestCase):
    def test_scale_x_shrink(self):
        random.seed(1)
        nframes = 1000
        mock_wave = build_mock_wave(nframes=nframes)
        wd = WavDecoder("filename", decoder_class=mock_wave, max_width=100)
        wd.open()
        scale = wd.width/nframes
        for i in range(0, 100):
            rand_x = random.randint(0, nframes)
            expected_x = rand_x * scale
            self.assertAlmostEqual(wd.scale_x(rand_x), expected_x)

    def test_scale_x_min(self):
        random.seed(1)
        nframes = 10
        mock_wave = build_mock_wave(nframes=nframes)
        wd = WavDecoder("filename", decoder_class=mock_wave, max_width=100)
        wd.open()
        for i in range(0, 100):
            rand_x = random.randint(0, nframes)
            self.assertAlmostEqual(wd.scale_x(rand_x), rand_x)

    def test_scale_y(self):
        random.seed(1)
        sampwidth = 2
        max_height = 2**(sampwidth*8 - 1)
        mock_wave = build_mock_wave(sampwidth=sampwidth)
        wd = WavDecoder("filename", decoder_class=mock_wave, max_height=1000)
        wd.open()
        scale = wd.height/max_height
        for i in range(0, 100):
            rand_y = random.randint(0, max_height)
            expected_y = rand_y * scale/2
            self.assertAlmostEqual(wd.scale_y(rand_y), expected_y)

    def test_scale_y_max(self):
        random.seed(1)
        sampwidth = 2
        mock_wave = build_mock_wave(sampwidth=sampwidth)
        wd = WavDecoder("filename", decoder_class=mock_wave, max_height=1000)
        wd.open()
        test_y = 2**(sampwidth*8)
        expected_y = 1000
        self.assertAlmostEqual(wd.scale_y(test_y), expected_y)

    def test_scale_y_8_bit(self):
        random.seed(1)
        sampwidth = 1
        max_height = 2**8
        mock_wave = build_mock_wave(sampwidth=sampwidth)
        wd = WavDecoder("filename", decoder_class=mock_wave, max_height=100,
                        signed=False)
        wd.open()
        wd.deocder = wave
        scale = wd.height/max_height
        for i in range(0, 100):
            rand_y = random.randint(0, max_height)
            expected_y = (rand_y-128) * scale
            self.assertAlmostEqual(wd.scale_y(rand_y), expected_y)


class TestStructFmt(unittest.TestCase):
    def test_struct_fmt_char_B(self):
        mock_wave = build_mock_wave(sampwidth=1)
        wd = WavDecoder("filename", decoder_class=mock_wave, signed=False)
        wd.open()
        self.assertEqual(wd.struct_fmt_char, 'B')

    def test_struct_fmt_char_b(self):
        mock_wave = build_mock_wave(sampwidth=1)
        wd = WavDecoder("filename", decoder_class=mock_wave, signed=True)
        wd.open()
        self.assertEqual(wd.struct_fmt_char, 'b')

    def test_struct_fmt_char_h(self):
        mock_wave = build_mock_wave(sampwidth=2)
        wd = WavDecoder("filename", decoder_class=mock_wave)
        wd.open()
        self.assertEqual(wd.struct_fmt_char, 'h')

    def test_struct_fmt_char_i(self):
        mock_wave = build_mock_wave(sampwidth=4)
        wd = WavDecoder("filename", decoder_class=mock_wave)
        wd.open()
        self.assertEqual(wd.struct_fmt_char, 'i')

    def test_struct_fmt_char_24(self):
        mock_wave = build_mock_wave(sampwidth=3)
        wd = WavDecoder("filename", decoder_class=mock_wave)
        with self.assertRaises(ValueError):
            wd.open()

    def test_struct_fmt_char_0(self):
        mock_wave = build_mock_wave(sampwidth=0)
        wd = WavDecoder("filename", decoder_class=mock_wave)
        with self.assertRaises(ValueError):
            wd.open()

    def test_struct_fmt_char_big(self):
        for i in range(5, 12):
            mock_wave = build_mock_wave(sampwidth=i)
            wd = WavDecoder("filename", decoder_class=mock_wave)
            with self.assertRaises(ValueError):
                wd.open()


class TestNext(SetupBase):
    def test_not_open(self):
        self.wd.next()
        self.wd.decoder.open.assert_called_once_with("filename", "rb")

    def test_slurp_data(self):
        mock_wave = build_mock_wave(bytes=b'\x01', nframes=10, nchannels=2,
                                    sampwidth=2)
        self.wd.decoder = mock_wave
        data = self.wd.next()

        # should be two channels
        self.assertEqual(len(data), 2)

        for chan in data:
            # should be 10 samples:
            self.assertEqual(len(chan), 10)

            for i, x in enumerate(chan):
                # each sample should be (about, because of scaling) 257 ==
                # b'\x01\x01'
                self.assertEqual(x.x, i+1)
                self.assertAlmostEqual(x.y, 257, delta=5)

    def test_iterate_data(self):
        mock_wave = build_mock_wave(bytes=b'\x01', nframes=10, nchannels=2,
                                    sampwidth=2)
        self.wd.decoder = mock_wave
        self.wd.bs = 2
        for data in self.wd:
            for chan in data:
                i = 0
                for x, point in enumerate(chan):
                    i += 1
                    self.assertAlmostEqual(point.y, 257, delta=5)
                self.assertEqual(i, self.wd.bs)
