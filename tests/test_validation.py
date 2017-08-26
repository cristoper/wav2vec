"""
These tests must be run with Python 3.4+
"""
import unittest
import subprocess

cmd = 'wav2vec.py'
indir = 'tests/valfiles/snd'
outdir = 'tests/valfiles/out'

test_cases = [
    # Default SVG:
    {
        "infile": "noise-8.wav",
        "flags": "-f SVG",
        "outfile": "noise-8.svg",
    },
    {
        "infile": "noise-8.aiff",
        "flags": "-f SVG",
        "outfile": "noise-8.svg",
    },
    {
        "infile": "noise-16.wav",
        "flags": "-f SVG",
        "outfile": "noise-16.svg",
    },
    {
        "infile": "noise-16.aiff",
        "flags": "-f SVG",
        "outfile": "noise-16-aiff.svg",
    },
    {
        "infile": "noise-32.wav",
        "flags": "-f SVG",
        "outfile": "noise-32.svg",
    },
    {
        "infile": "noise-32.aiff",
        "flags": "-f SVG",
        "outfile": "noise-32-aiff.svg",
    },
    # Default CSV:
    {
        "infile": "noise-8.wav",
        "flags": "-f CSV",
        "outfile": "noise-8.csv",
    },
    {
        "infile": "noise-8.aiff",
        "flags": "-f CSV",
        "outfile": "noise-8.csv",
    },
    {
        "infile": "noise-16.wav",
        "flags": "-f CSV",
        "outfile": "noise-16.csv",
    },
    {
        "infile": "noise-16.aiff",
        "flags": "-f CSV",
        "outfile": "noise-16-aiff.csv",
    },
    {
        "infile": "noise-32.wav",
        "flags": "-f CSV",
        "outfile": "noise-32.csv",
    },
    {
        "infile": "noise-32.aiff",
        "flags": "-f CSV",
        "outfile": "noise-32-aiff.csv",
    },
    # Default PostScript:
    {
        "infile": "noise-8.wav",
        "flags": "-f PostScript",
        "outfile": "noise-8.ps",
    },
    {
        "infile": "noise-8.aiff",
        "flags": "-f PostScript",
        "outfile": "noise-8.ps",
    },
    {
        "infile": "noise-16.wav",
        "flags": "-f PostScript",
        "outfile": "noise-16.ps",
    },
    {
        "infile": "noise-16.aiff",
        "flags": "-f PostScript",
        "outfile": "noise-16-aiff.ps",
    },
    {
        "infile": "noise-32.wav",
        "flags": "-f PostScript",
        "outfile": "noise-32.ps",
    },
    {
        "infile": "noise-32.aiff",
        "flags": "-f PostScript",
        "outfile": "noise-32-aiff.ps",
    },
    # long, stereo, default:
    {
        "infile": "test-16-stereo.wav",
        "flags": "",
        "outfile": "test-16-stereo.svg",
    },
    {
        "infile": "test-16-stereo.aiff",
        "flags": "",
        "outfile": "test-16-stereo-aiff.svg",
    },
    {
        "infile": "test-16-stereo.wav",
        "flags": "-f CSV",
        "outfile": "test-16-stereo.csv",
    },
    {
        "infile": "test-16-stereo.aiff",
        "flags": "-f CSV",
        "outfile": "test-16-stereo-aiff.csv",
    },
    {
        "infile": "test-16-stereo.wav",
        "flags": "-f PostScript",
        "outfile": "test-16-stereo.ps",
    },
    # long, stereo, full height short width:
    {
        "infile": "test-16-stereo.wav",
        "flags": "--width 250 --height 0",
        "outfile": "test-16-stereo-100x0.svg",
    },
    {
        "infile": "test-16-stereo.wav",
        "flags": "--width 250 --height 0 --format PostScript",
        "outfile": "test-16-stereo-100x0.ps",
    },
    # long, stereo, --stream 1000
    {
        "infile": "test-16-stereo.wav",
        "flags": "--stream 1000",
        "outfile": "test-16-stereo-stream.svg",
    },
    {
        "infile": "test-16-stereo.aiff",
        "flags": "--stream 1000",
        "outfile": "test-16-stereo-stream-aiff.svg",
    },
    {
        "infile": "test-16-stereo.wav",
        "flags": "--stream 1000 -f PostScript",
        "outfile": "test-16-stereo-stream.ps",
    },
    {
        "infile": "test-16-stereo.aiff",
        "flags": "--stream 1000 -f PostScript",
        "outfile": "test-16-stereo-stream-aiff.ps",
    },
    # downtoss 3
    {
        "infile": "noise-16.wav",
        "flags": "--downtoss 3",
        "outfile": "noise-16-down3.svg",
    },
    {
        "infile": "noise-16.aiff",
        "flags": "--downtoss 3 -f PostScript",
        "outfile": "noise-16-down3.ps",
    },
]


class TestValidationFiles(unittest.TestCase):
    def test_all(self):
        #self.maxDiff = None
        for i, test in enumerate(test_cases):
            with self.subTest(i=i):
                with open(outdir + '/' + test['outfile']) as f:
                    expected = f.read()
                test_file = indir + '/' + test['infile']
                cmd_line = "python %s %s %s" % (cmd, test['flags'], test_file)
                result = subprocess.check_output(cmd_line.split())
                result = result.decode('utf-8')
                #print(test['infile'], test['outfile'])
                self.assertEqual(result, expected)
