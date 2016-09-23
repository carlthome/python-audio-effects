# coding=utf-8
"""Testing module for the DSP package, preferably run with py.test."""
import librosa as lr

from pysndfx.dsp import AudioEffectsChain

apply_audio_effects = AudioEffectsChain()\
    .phaser()\
    .highshelf()\
    .lowshelf() \
    .delay()\
    .reverb()\

infile = lr.util.example_audio_file()
mono, sr = lr.load(infile, sr=None)
stereo, _ = lr.load(infile, sr=None, mono=False)
outfile = 'test_output.ogg'


def test_file_to_file():
    apply_audio_effects(infile, outfile)
    y = lr.load(outfile, None)[0]
    assert lr.util.valid_audio(y)


def test_file_to_ndarray():
    y = apply_audio_effects(infile)
    assert lr.util.valid_audio(y)


def test_ndarray_to_ndarray():
    y = apply_audio_effects(mono)
    assert lr.util.valid_audio(y)


def test_mono_ndarray_to_file():
    apply_audio_effects(mono, outfile)
    y = lr.load(outfile, None)[0]
    assert lr.util.valid_audio(y)


def test_stereo_ndarray_to_file():
    apply_audio_effects(stereo, outfile)
    y = lr.load(outfile, None, mono=False)[0]
    assert lr.util.valid_audio(y, mono=False)

# TODO How do we test this properly?
#def test_streaming():
#    c(None, None)
