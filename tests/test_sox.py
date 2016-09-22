# coding=utf-8
"""
Basic testing module for the package.
"""
from tempfile import NamedTemporaryFile

import librosa as lr

from sox.sox import Sox


def test_file_to_file():
    infile = lr.util.example_audio_file()
    s = Sox()\
        .phaser(0.1, 0.1, 0.1, 0.1, 0.1)\
        .reverb(True, 50, 50, 100, 100, 25, 10)
    outfile = 'test_file_to_file.wav'
    s(infile, outfile)
    y, sr = lr.load(outfile, sr=None)
    assert lr.util.valid_audio(y)


def test_file_to_numpy():
    infile = lr.util.example_audio_file()
    _, sr = lr.load(infile)
    s = Sox()\
        .phaser(0.1, 0.1, 0.1, 0.1, 0.1)\
        .reverb(True, 50, 50, 100, 100, 25, 10)
    output = s(infile)
    with NamedTemporaryFile() as ntf:
        lr.output.write_wav(ntf.name, output, sr)
        y, sr = lr.load(ntf.name, sr=None)
        assert lr.util.valid_audio(y)


def test_numpy_to_file():
    y, sr = lr.load(lr.util.example_audio_file(), sr=None)
    s = Sox() \
        .phaser(0.1, 0.1, 0.1, 0.1, 0.1) \
        .reverb(True, 50, 50, 100, 100, 25, 10)
    outfile = 'test_file_to_numpy.ogg'
    s(y, outfile)
    y, sr = lr.load(outfile, sr=None)
    assert lr.util.valid_audio(y)


def test_numpy_to_numpy():
    y, sr = lr.load(lr.util.example_audio_file(), sr=None)
    s = Sox()\
        .phaser(0.1, 0.1, 0.1, 0.1, 0.1)\
        .reverb(True, 50, 50, 100, 100, 25, 10)
    output = s(y)
    print(output.shape)
    with NamedTemporaryFile() as ntf:
        lr.output.write_wav(ntf.name, output, sr)
        y, sr = lr.load(ntf.name, sr=None)
        assert lr.util.valid_audio(y)


def test_streaming():
    # TODO Run in separate process and terminate it.
    Sox()\
        .phaser(0.1, 0.1, 0.1, 0.1, 0.1)\
        .reverb(True, 50, 50, 100, 100, 25, 10)()
