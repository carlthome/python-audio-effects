# coding=utf-8
from subprocess import Popen, PIPE

import numpy as np

class Sox:
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

    def __call__(self, src=None, dst=np.ndarray):
        if isinstance(src, np.ndarray):
            # TODO Don't assume input bit depth and sample rate.
            inputfile = '-t raw -b 32 -r 44100 -e floating-point -'
            stdin = src.tobytes()                    
        elif isinstance(src, str):
            # TODO Allow headerless input files.
            inputfile = src
            stdin = None
        elif isinstance(src, list):
            # TODO Allow combining files (e.g. take list input args).
            raise ValueError('Combining files not supported yet.')
        elif src is None:
            # TODO Allow other audio devices but the default.
            inputfile = '-d'        
        else:
            raise ValueError("Invalid input.")

        if dst is np.ndarray:
            # TODO Make output bit depth and output sample rate into parameters.
            outputfile = '-t raw -b 32 -r 44100 -e floating-point -'
        elif isinstance(dst, str):
            outputfile = dst
        elif dst is None:
            # TODO Allow other audio devices but the default.
            outputfile = '-d'
        else:
            raise ValueError("Invalid output.")
            
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
s = Sox().phaser(0.1, 0.1, 0.1, 0.1, 0.1).reverb(True, 50, 50, 100, 100, 25, 10)

# Apply effects.
output = s(y)
print(output.shape)

# Apply effects to file.
output = s(p)
print(output.shape)

# Apply effects and save results.
s(y, 'output.ogg')

# Apply effects to file and save results.
s(p, 'output.wav')

# Stream
s()


