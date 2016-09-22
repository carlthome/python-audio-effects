# coding=utf-8
"""
A lightweight Python wrapper of SoX's effects.
"""
import re
import shlex
from subprocess import PIPE, Popen

import numpy as np


class Chain:
    def __init__(self):
        self.command = ""                  
        
        
        # TODO Remove
        """
        stdout, stderr = Popen(
            ['sox', '--help'], stdout=PIPE, stderr=PIPE).communicate()
        if stderr:
            raise Exception(stderr)
        r = re.search('EFFECTS: ([\w+#* ]+)', stdout.decode())
        effects = r.group(1).split()
        for e in effects:
            stdout, stderr = Popen(
                ['sox', '--help-effect', e], stdout=PIPE,
                stderr=PIPE).communicate()
            if stderr:
                raise Exception(stderr)
            r = re.search(e + ' (.*)', stdout.decode())
            if r:
                print(e + ': ' + str(r.group(1).split()))
        """
                

    def allpass(self):
        pass

    def band(self):
        pass

    def bandpass(self):
        pass

    def bandreject(self):
        pass

    def bass(self):
        pass

    def bend(self):
        pass

    def biquad(self):
        pass

    def chorus(self):
        pass

    def channels(self):
        pass

    def compand(self):
        pass

    def contrast(self):
        pass

    def dcshift(self):
        pass

    def deemph(self):
        pass

    def delay(self):
        pass

    def dither(self):
        pass

    def downsample(self):
        pass

    def earwax(self):
        pass

    def echo(self):
        pass

    def echos(self):
        pass

    def equalizer(self):
        pass

    def fade(self):
        pass

    def fir(self):
        pass

    def flanger(self):
        pass

    def gain(self):
        pass

    def highpass(self):
        pass

    def hilbert(self):
        pass

    def ladspa(self):
        pass

    def loudness(self):
        pass

    def lowpass(self):
        pass

    def mcompand(self):
        pass

    def noiseprof(self):
        pass

    def noisered(self):
        pass

    def norm(self):
        pass

    def oops(self):
        pass

    def overdrive(self):
        pass

    def pad(self):
        pass

    def phaser(self, gain_in, gain_out, delay, decay, speed):
        self.command += ' phaser ' + ' '.join(
            map(str, [gain_in, gain_out, delay, decay, speed]))
        return self

    def pitch(self):
        pass

    def rate(self):
        pass

    def remix(self):
        pass

    def repeat(self):
        pass

    def reverb(self, wet_only, reverberance, hf_damping, room_scale,
               stereo_depth, pre_delay, wet_gain):
        self.command += ' reverb '
        if wet_only:
            self.command += ' -w '
        self.command += ' '.join(
            map(str, [reverberance, hf_damping, room_scale, stereo_depth,
                      pre_delay, wet_gain]))
        return self

    def reverse(self):
        pass

    def riaa(self):
        pass

    def silence(self):
        pass

    def sinc(self):
        pass

    def spectrogram(self):
        pass

    def speed(self):
        pass

    def splice(self):
        pass

    def stat(self):
        pass

    def stats(self):
        pass

    def stretch(self):
        pass

    def swap(self):
        pass

    def synth(self):
        pass

    def tempo(self):
        pass

    def treble(self):
        pass

    def tremolo(self):
        pass

    def trim(self):
        pass

    def upsample(self):
        pass

    def vad(self):
        pass

    def vol(self):
        pass
        
    def save(self, outfile):
        self.outfile = outfile

    def __call__(self, src, dst=np.ndarray, samplerate=44100):
        if isinstance(src, np.ndarray):
            if src.ndim == 2 and src.shape[0] == 2:
                channels = '-c 2'
            else:
                channels = '-c 1'
            infile = '-t raw -e floating-point -b 32 -r ' + str(samplerate) + ' ' + channels + ' -'
            stdin = src.tobytes()
        elif isinstance(src, str):
            # TODO Allow headerless input files.
            infile = src
            stdin = None
        elif isinstance(src, list):
            # TODO Allow combining files.
            raise ValueError('Combining files not supported yet.')
        else:
            # TODO Allow other audio devices but the default.
            infile = '-d'
            stdin = None
        if dst is np.ndarray:
            # TODO Make output bit depth and output sample rate into parameters.
            outfile = '-t raw -b 32 -r 44100 -e floating-point -c 2 -'
        elif isinstance(dst, str):
            outfile = dst
        else:
            # TODO Allow other audio devices but the default.
            outfile = '-d'

        cmd = shlex.split(' '.join(['sox', infile, outfile, self.command]))
        stdout, stderr = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate(stdin)
        if stderr:
            raise RuntimeError("Command: " + str(cmd), stderr)
        if stdout:
            outsound = np.frombuffer(stdout)
            return outsound
