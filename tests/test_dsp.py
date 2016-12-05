# coding=utf-8
"""Testing module for the DSP package, preferably run with py.test."""
import numpy as np
import librosa as lr

from pysndfx.dsp import AudioEffectsChain

apply_audio_effects = AudioEffectsChain()\
    .highshelf()\
    .reverb()\
    .phaser()\
    .delay()\
    .lowshelf()

infile = lr.util.example_audio_file()
mono, sr = lr.load(infile, sr=None)
stereo, _ = lr.load(infile, sr=None, mono=False)
outfile = 'test_output.wav'


def test_file_to_file():
    apply_audio_effects(infile, outfile)
    y = lr.load(outfile, sr=None, mono=False)[0]
    lr.output.write_wav('test_file_to_file.wav', y, sr)
    assert lr.util.valid_audio(y, mono=False)


def test_ndarray_to_ndarray():
    y = apply_audio_effects(mono)
    lr.output.write_wav('test_ndarray_to_ndarray_mono.wav', y, sr)
    assert lr.util.valid_audio(y)

    y = apply_audio_effects(stereo)
    lr.output.write_wav('test_ndarray_to_ndarray_stereo.wav', y, sr)
    assert lr.util.valid_audio(y, mono=False)


def test_ndarray_to_file():
    apply_audio_effects(mono, outfile)
    y = lr.load(outfile, sr=None)[0]
    lr.output.write_wav('test_ndarray_to_file_mono.wav', y, sr)
    assert lr.util.valid_audio(y)

    apply_audio_effects(stereo, outfile)
    y = lr.load(outfile, sr=None, mono=False)[0]
    lr.output.write_wav('test_ndarray_to_file_stereo.wav', y, sr)
    assert lr.util.valid_audio(y, mono=False)


def test_file_to_ndarray():
    y = apply_audio_effects(infile)
    lr.output.write_wav('test_file_to_ndarray.wav', y, sr)
    assert lr.util.valid_audio(y, mono=False)


# TODO How do we test this properly?
#def test_streaming():
#    c(None, None)
