# coding=utf-8
"""A lightweight Python wrapper of SoX's effects."""
import shlex
from subprocess import PIPE, Popen
from warnings import warn

import numpy as np


class AudioEffectsChain:
    def __init__(self):
        self.command = []

    def equalizer(self, frequency, q=1.0, db=-3.0):
        self.command.append('equalizer')
        self.command.append(frequency)
        self.command.append(str(q) + 'q')
        self.command.append(db)
        return self

    def bandpass(self, frequency, q=1.0):
        self.command.append('bandpass')
        self.command.append(frequency)
        self.command.append(str(q) + 'q')
        return self

    def bandreject(self, frequency, q=1.0):
        self.command.append('bandreject')
        self.command.append(frequency)
        self.command.append(str(q) + 'q')
        return self

    def lowshelf(self, gain=-20.0, frequency=100, slope=0.5):
        self.command.append('bass')
        self.command.append(gain)
        self.command.append(frequency)
        self.command.append(slope)
        return self

    def highshelf(self, gain=-20.0, frequency=3000, slope=0.5):
        self.command.append('treble')
        self.command.append(gain)
        self.command.append(frequency)
        self.command.append(slope)
        return self

    def highpass(self, frequency, q=0.707):
        self.command.append('highpass')
        self.command.append(frequency)
        self.command.append(str(q) + 'q')
        return self

    def lowpass(self, frequency, q=0.707):
        self.command.append('lowpass')
        self.command.append(frequency)
        self.command.append(str(q) + 'q')
        return self

    def limiter(self, gain=3.0):
        self.command.append('gain')
        self.command.append('-l')
        self.command.append(gain)
        return self

    def normalize(self):
        self.command.append('gain')
        self.command.append('-n')
        return self

    def compand(self, attack=0.05, decay=0.5):
        raise NotImplemented()
        return self

    def bend(self):
        raise NotImplemented()
        return self

    def chorus(self):
        raise NotImplemented()
        return self

    def delay(self,
              gain_in=0.8,
              gain_out=0.5,
              delays=list((1000, 1800)),
              decays=list((0.3, 0.25)),
              parallel=False):
        self.command.append('echo' + ('s' if parallel else ''))
        self.command.append(gain_in)
        self.command.append(gain_out)
        self.command.extend(list(sum(zip(delays, decays), ())))
        return self

    def fade(self):
        raise NotImplemented()
        return self

    def flanger(self,
                delay=0,
                depth=2,
                regen=0,
                width=71,
                speed=0.5,
                shape='sine',
                phase=25,
                interp='linear'):
        raise NotImplemented()
        return self

    def gain(self, db):
        self.command.append('gain')
        self.command.append(db)
        return self

    def mcompand(self):
        raise NotImplemented()
        return self

    def noise_reduction(self, amount=0.5):
        # TODO Run sox once with noiseprof on silent portions to generate a noise profile.
        raise NotImplemented()
        return self

    def oops(self):
        raise NotImplemented()
        return self

    def overdrive(self):
        raise NotImplemented()
        return self

    def phaser(self,
               gain_in=0.9,
               gain_out=0.8,
               delay=1,
               decay=0.25,
               speed=2,
               triangular=False):
        self.command.append('phaser')
        self.command.append(gain_in)
        self.command.append(gain_out)
        self.command.append(delay)
        self.command.append(decay)
        self.command.append(speed)
        if triangular:
            self.command.append('-t')
        else:
            self.command.append('-s')
        return self

    def pitch(self):
        raise NotImplemented()
        return self

    def loop(self):
        self.command.append('repeat')
        self.command.append('-')
        return self

    def reverb(self,
               reverberance=50,
               hf_damping=50,
               room_scale=100,
               stereo_depth=100,
               pre_delay=20,
               wet_gain=0,
               wet_only=False):
        self.command.append('reverb')
        if wet_only:
            self.command.append('-w')
        self.command.append(reverberance)
        self.command.append(hf_damping)
        self.command.append(room_scale)
        self.command.append(stereo_depth)
        self.command.append(pre_delay)
        self.command.append(wet_gain)
        return self

    def reverse(self):
        raise NotImplemented()
        return self

    def silence(self):
        raise NotImplemented()
        return self

    def speed(self):
        raise NotImplemented()
        return self

    def synth(self):
        # Maybe skip this entirely?
        raise NotImplemented()
        return self

    def tempo(self):
        raise NotImplemented()
        return self

    def tremolo(self):
        raise NotImplemented()
        return self

    def trim(self):
        raise NotImplemented()
        return self

    def upsample(self):
        raise NotImplemented()
        return self

    def vad(self):
        raise NotImplemented()
        return self

    def vol(self):
        raise NotImplemented()
        return self

    def __call__(self,
                 src,
                 dst=np.ndarray,
                 samplerate=44100,
                 allow_clipping=True):

        # Shared SoX flags.
        encoding = '-t f32'
        samplerate = '-r ' + str(samplerate)
        pipe = '-'

        # Parse input flags.
        infile = '-d'
        stdin = None
        if isinstance(src, str):
            infile = src
            stdout, stderr = Popen(
                shlex.split(
                    'sox --i -c ' + src, posix=False),
                stdout=PIPE,
                stderr=PIPE).communicate()
            channels = '-c ' + str(int(stdout))
        elif isinstance(src, np.ndarray):
            channels = '-c ' + str(src.ndim)
            infile = ' '.join([
                encoding,
                samplerate,
                channels,
                pipe,
            ])
            stdin = src.tobytes(order='F')

        # Parse output flags.
        outfile = '-d'
        if isinstance(dst, str):
            outfile = dst
        elif dst is np.ndarray:
            outfile = ' '.join([
                encoding,
                samplerate,
                channels,
                pipe,
            ])

        cmd = shlex.split(
            ' '.join([
                'sox',
                '-N',
                '-V1' if allow_clipping else '-V2',
                infile,
                outfile,
            ] + list(map(str, self.command))),
            posix=False)
        stdout, stderr = Popen(
            cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate(stdin)
        if stderr:
            raise RuntimeError(stderr.decode())
        if stdout:
            outsound = np.fromstring(stdout, dtype=np.float32)
            c = int(channels.split()[-1])
            if c > 1:
                outsound = outsound.reshape(
                    (c, int(len(outsound) / c)), order='F')
            return outsound
