# pysndfx
**Apply audio effects such as reverb and EQ directly to audio files or NumPy ndarrays.**

This is a lightweight Python wrapper for SoX, the Swiss Army knife of sound processing programs. Supported effects range from EQ, compression and noise reduction to phasers, reverbs and pitch shifters.

## Install
The prefered way of installing is with [conda](https://anaconda.org/) as
```sh
conda install -c conda-forge pysndfx
```
but it's also possible to install with pip as
```sh
pip install "git+ssh://git@github.com/carlthome/python-sound-effects"
```
but then the system must also have [SoX](http://sox.sourceforge.net/) installed (for Debian-based operating systems: `apt install sox`).

## Usage
First create an audio effects chain.
```python
# Import the package and create an audio effects chain.
from pysndfx.dsp import Chain
apply_audio_fx = Chain()\
                     .phaser()\
                     .reverb()
```
Then we can call the effects chain object with paths to audio files, or directly with NumPy ndarrays.
```python
infile = 'my_audio_file.wav'
outfile = 'my_processed_audio_file.ogg'

# Apply phaser and reverb directly to an audio file.
apply_audio_fx(infile, outfile)

# Or, apply the effects directly to a NumPy ndarray.
from librosa import load
x, sr = load(infile, sr=None)
y = apply_audio_fx(x)

# Apply the effects and return the results as a NumPy ndarray.
y = apply_audio_fx(infile)

# Apply the effects to a NumPy ndarray but store the resulting audio to disk.
apply_audio_fx(x, outfile)
```
There's also experimental streaming support. Try applying reverb to a microphone input and listening to the results live like this:
```sh
python -c "from pysndfx.dsp import Chain; Chain().reverb()(None, None)"
```
