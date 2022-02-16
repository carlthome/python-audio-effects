# Deprecated: I strongly recommend checking out github.com/spotify/pedalboard instead!
Contact me if you'd like this package to persist, and/or if you'd like to take over ownership of this repo.

# pysndfx
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/carlthome/python-audio-effects/Test%20Python%20Package)](https://github.com/carlthome/python-audio-effects/actions?query=workflow%3A%22Test+Python+Package%22) [![PyPI](https://img.shields.io/pypi/v/pysndfx.svg)](https://pypi.python.org/pypi/pysndfx) [![PyPI](https://img.shields.io/pypi/pyversions/pysndfx.svg)](http://py3readiness.org/) [![license](https://img.shields.io/github/license/mashape/apistatus.svg)](LICENSE)

**Apply audio effects such as reverb and EQ directly to audio files or NumPy ndarrays.**

This is a lightweight Python wrapper for SoX - Sound eXchange. Supported effects range from EQ and compression to phasers, reverb and pitch shifters.

## Install
Command:
```sh
pip install pysndfx
```
The system must also have [SoX](http://sox.sourceforge.net/) installed.

For Debian-based operating systems: `apt install sox`

For Anaconda: `conda install -c conda-forge sox`

## Usage
First create an audio effects chain.
```python
# Import the package and create an audio effects chain function.
from pysndfx import AudioEffectsChain

fx = (
    AudioEffectsChain()
    .highshelf()
    .reverb()
    .phaser()
    .delay()
    .lowshelf()
)
```
Then we can call the effects chain object with paths to audio files, or directly with NumPy ndarrays.
```python
infile = 'my_audio_file.wav'
outfile = 'my_processed_audio_file.ogg'

# Apply phaser and reverb directly to an audio file.
fx(infile, outfile)

# Or, apply the effects directly to a ndarray.
from librosa import load
y, sr = load(infile, sr=None)
y = fx(y)

# Apply the effects and return the results as a ndarray.
y = fx(infile)

# Apply the effects to a ndarray but store the resulting audio to disk.
fx(x, outfile)
```
There's also experimental streaming support. Try applying reverb to a microphone input and listening to the results live like this:
```sh
python -c "from pysndfx import AudioEffectsChain; AudioEffectsChain().reverb()(None, None)"
```
