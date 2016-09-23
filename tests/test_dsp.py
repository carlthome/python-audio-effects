# coding=utf-8
"""Testing module for the DSP package, preferably run with py.test."""
import librosa as lr

from pysndfx.dsp import AudioEffectsChain

apply_audio_effects = AudioEffectsChain()\
    .phaser()\
    .highshelf()\
    .lowshelf()\
    .reverb()

infile = lr.util.example_audio_file()
x, sr = lr.load(infile, sr=None)
outfile = 'test_output.ogg'


def test_file_to_file():
    apply_audio_effects(infile, outfile)
    y = lr.load(outfile, None)[0]
    assert lr.util.valid_audio(y)


def test_file_to_numpy():
    y = apply_audio_effects(infile)
    assert lr.util.valid_audio(y)


def test_numpy_to_numpy():
    y = apply_audio_effects(x)
    assert lr.util.valid_audio(y)


def test_mono_to_file():
    apply_audio_effects(x, outfile)
    y = lr.load(outfile, None)[0]
    assert lr.util.valid_audio(y)


def test_stereo_to_file():
    apply_audio_effects(x, outfile)
    y = lr.load(outfile, None, mono=False)[0]
    assert lr.util.valid_audio(y)

# TODO How do we test this properly?
#def test_streaming():
#    c(None, None)
