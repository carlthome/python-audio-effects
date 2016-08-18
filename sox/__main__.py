# coding=utf-8
from subprocess import Popen, PIPE

import numpy as np


class EffectsChain:
    def __init__(self):
        self.command = ""

    def reverb(self, wet_only, reverberance, hf_damping, room_scale, stereo_depth, pre_delay, wet_gain):
        self.command += ' reverb '
        if wet_only:
            self.command += ' -w '
        self.command += ' '.join(map(str, [reverberance, hf_damping, room_scale, stereo_depth, pre_delay, wet_gain]))
        return self
    
    def phaser(self, gain_in, gain_out, delay, decay, speed):
        self.command += ' phaser ' + ' '.join(map(str, [gain_in, gain_out, delay, decay, speed]))
        return self

    def __call__(self, inputsound, outputfile=None):

        if isinstance(inputsound, str):
            # TODO Allow headerless input files.
            inputfile = inputsound
            stdin = None
        elif isinstance(inputsound, np.ndarray):
            # TODO Make bit depth and sample rate into parameters.
            inputfile = '-t raw -b 32 -r 44100 -e floating-point -'
            stdin = inputsound.tobytes()
        elif isinstance(inputsound, list):
            # TODO Allow combining files (e.g. take list input args).
            raise ValueError('Combining files not supported yet.')

        if not outputfile:
            # TODO Make bit depth and sample rate into parameters.
            outputfile = '-t raw -b 32 -r 44100 -e floating-point -'

        # TODO Split command into list before passing it to Popen for OS compatitbility.
        x = 'sox'.split()
        x.extend(inputfile.split())
        x.extend(outputfile.split())
        x.extend(self.command.split())
        print(" ".join(x))
        stdout, stderr = Popen(x,
                               stdout=PIPE,
                               stderr=PIPE,
                               bufsize=-1).communicate(stdin)
        if stderr:
            raise Exception("Command: " + str(x), stderr)
        if stdout:
            outputsound = np.frombuffer(stdout)
            return outputsound



# Test
import librosa as lr
p = lr.util.example_audio_file()
y, sr = lr.load(p, sr=None)
print("Sample rate: ", sr)
print("Bit depth: ", y.dtype)
s = EffectsChain().phaser(0.1, 0.1, 0.1, 0.1, 0.1).reverb(True, 50, 50, 100, 100, 25, 10)

# Apply effects.
output = s(y)
print(output.shape)

# Load file, and apply effects.
output = s(p)
print(output.shape)

# Apply effects and output file.
s(y, 'output.ogg')

# Load file, apply effects and output file.
s(p, 'output.wav')




