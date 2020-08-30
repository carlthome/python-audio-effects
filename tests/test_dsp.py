"""Testing module for the DSP package, preferably run with py.test."""
import logging

import librosa as lr
import soundfile as sf

from pysndfx.dsp import AudioEffectsChain

logger = logging.getLogger('pysndfx')
logger.setLevel(logging.DEBUG)

apply_audio_effects = \
    (AudioEffectsChain()
     .highshelf()
     .reverb()
     .phaser()
     .delay()
     .lowshelf())

infile = lr.util.example_audio_file()
mono, sr = lr.load(infile, sr=None)
stereo, _ = lr.load(infile, sr=None, mono=False)
outfile = 'test_output.ogg'


def test_file_to_file():
    apply_audio_effects(infile, outfile)
    y = lr.load(outfile, sr=None, mono=False)[0]
    sf.write('test_file_to_file.wav', y.T, sr)
    assert lr.util.valid_audio(y, mono=False)


def test_ndarray_to_ndarray():
    y = apply_audio_effects(mono)
    sf.write('test_ndarray_to_ndarray_mono.wav', y, sr)
    assert lr.util.valid_audio(y)

    y = apply_audio_effects(stereo)
    sf.write('test_ndarray_to_ndarray_stereo.wav', y.T, sr)
    assert lr.util.valid_audio(y, mono=False)


def test_ndarray_to_file():
    apply_audio_effects(mono, outfile)
    y = lr.load(outfile, sr=None)[0]
    sf.write('test_ndarray_to_file_mono.wav', y, sr)
    assert lr.util.valid_audio(y)

    apply_audio_effects(stereo, outfile)
    y = lr.load(outfile, sr=None, mono=False)[0]
    sf.write('test_ndarray_to_file_stereo.wav', y.T, sr)
    assert lr.util.valid_audio(y, mono=False)


def test_file_to_ndarray():
    y = apply_audio_effects(infile)
    sf.write('test_file_to_ndarray.wav', y.T, sr)
    assert lr.util.valid_audio(y, mono=False)
