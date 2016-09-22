# pysndfx
Apply audio effects to NumPy ndarrays or audio files.

This is a lightweight Python wrapper for SoX, the Swiss Army knife of sound processing programs. Supported effects range from EQ, compression and noise reduction to phasers, reverbs and pitch shifters.

## Install
First make sure Python and pip are installed, then run:
```sh
pip install "git+ssh://git@github.com/carlthome/python-sound-effects"
```

The system must also have [SoX](http://sox.sourceforge.net/) installed (for Debian-based operating systems: `apt install sox`).

## Usage
Process 
```python
# Import the package and create an audio effects chain.
from pysndfx.dsp import Chain
c = (Chain()
        .phaser(0.5, 0.5, 0.5, 0.5, 0.5)
        .reverb(False, 50, 50, 100, 100, 25, 10))

infile = 'my_audio_file.wav'
outfile = 'my_processed_audio_file.ogg'

# Apply phaser and reverb directly to an audio file.
c(infile, outfile)

# Or, apply the effects directly to a NumPy ndarray
from librosa import load
x, sr = load(infile, sr=None)
y = c(x)
```

It's also possible to load/save from and to ndarrays and files as you go, like:
```python
# Apply the effects and return the results as a NumPy ndarray
y = c(infile)

# Apply the effects to a NumPy ndarray but store the resulting audio to disk.
c(x, outfile)
```

There's also experimental streaming support but only with the default input and output audio device. Try applying reverb to a microphone input and listening to the results live like this:
```sh
python -c "from pysndfx.dsp import Chain; Chain().reverb(False, 100,1,1,1,1,1)(None, None)"
```
