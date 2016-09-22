# coding=utf-8
"""
Testing module for the DSP package.
"""
import librosa as lr

from pysndfx.dsp import Chain


c = (Chain()
        .phaser(0.5, 0.5, 0.5, 0.5, 0.5)
        .reverb(False, 50, 50, 100, 100, 25, 10))

infile = lr.util.example_audio_file()
x, sr = lr.load(infile, sr=None)
outfile = 'test_output.ogg'


def test_file_to_file():
    c(infile, outfile)
    y = lr.load(outfile, None)[0]
    assert lr.util.valid_audio(y)


def test_file_to_numpy():
    y = c(infile)
    assert lr.util.valid_audio(y)


def test_numpy_to_numpy():
    y = c(x)
    assert lr.util.valid_audio(y)


def test_mono_to_file():
    c(x, outfile)
    y = lr.load(outfile, None)[0]
    assert lr.util.valid_audio(y)

    
def test_stereo_to_file():
    c(x, outfile)
    y = lr.load(outfile, None, mono=False)[0]
    assert lr.util.valid_audio(y)

# TODO
#def test_streaming():
#    c(None, None)
