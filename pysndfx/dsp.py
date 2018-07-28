# coding=utf-8
"""A lightweight Python wrapper of SoX's effects."""
import logging
import shlex
from io import BufferedReader, BufferedWriter
from subprocess import PIPE, Popen

import numpy as np

from .sndfiles import FilePathInput, FileBufferInput, NumpyArrayInput, FilePathOutput, NumpyArrayOutput, FileBufferOutput


def mutually_exclusive(*args):
    return sum(arg is not None for arg in args) < 2


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

    def compand(self, attack=0.2, decay=1, soft_knee=2.0, threshold=-20, db_from=-20.0, db_to=-20.0):
        self.command.append('compand')
        self.command.append(str(attack) + ',' + str(decay))
        self.command.append(str(soft_knee) + ':' + str(threshold) + ',' + str(db_from) + ',' + str(db_to))
        return self

    def sinc(self,
             high_pass_frequency=None,
             low_pass_frequency=None,
             left_t=None,
             left_n=None,
             right_t=None,
             right_n=None,
             attenuation=None,
             beta=None,
             phase=None,
             M=None,
             I=None,
             L=None):
        self.command.append("sinc")
        if not mutually_exclusive(attenuation, beta):
            raise ValueError("Attenuation (-a) and beta (-b) are mutually exclusive arguments")
        if attenuation is not None and beta is None:
            self.command.append("-a")
            self.command.append(str(attenuation))
        elif attenuation is None and beta is not None:
            self.command.append("-b")
            self.command.append(str(beta))

        if not mutually_exclusive(phase, M, I, L):
            raise ValueError("Phase (-p), -M, L, and -I are mutually exclusive arguments")
        if phase is not None:
            self.command.append("-p")
            self.command.append(str(phase))
        elif M is not None:
            self.command.append("-M")
        elif I is not None:
            self.command.append("-I")
        elif L is not None:
            self.command.append("-L")

        if not mutually_exclusive(left_t, left_t):
            raise ValueError("Transition bands options (-t or -n) are mutually exclusive")
        if left_t is not None:
            self.command.append("-t")
            self.command.append(str(left_t))
        if left_n is not None:
            self.command.append("-n")
            self.command.append(str(left_n))
        
        if high_pass_frequency is not None and low_pass_frequency is None:
            self.command.append(str(high_pass_frequency))
        elif high_pass_frequency is not None and low_pass_frequency is not None:
            self.command.append(str(high_pass_frequency) + "-" + str(low_pass_frequency))
        elif high_pass_frequency is None and low_pass_frequency is not None:
            self.command.append(str(low_pass_frequency))

        if not mutually_exclusive(right_t, right_t):
            raise ValueError("Transition bands options (-t or -n) are mutually exclusive")
        if right_t is not None:
            self.command.append("-t")
            self.command.append(str(right_t))
        if right_n is not None:
            self.command.append("-n")
            self.command.append(str(right_n))
        return self

    def bend(self, bends, frame_rate=None, over_sample=None):
        self.command.append("bend")
        if frame_rate is not None and isinstance(frame_rate, int):
            self.command.append("-f %s" % frame_rate)
        if over_sample is not None and isinstance(over_sample, int):
            self.command.append("-o %s" % over_sample)
        for bend in bends:
            self.command.append(",".join(bend))
        return self

    def chorus(self, gain_in, gain_out, decays):
        self.command.append("chorus")
        self.command.append(gain_in)
        self.command.append(gain_out)
        for decay in decays:
            modulation = decay.pop()
            numerical = decay
            self.command.append(" ".join(map(str, numerical)) + " -" + modulation)
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

    def echo(self, **kwargs):
        self.delay(**kwargs)

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

    def overdrive(self, gain=20, colour=20):
        self.command.append('overdrive')
        self.command.append(gain)
        self.command.append(colour)
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

    def pitch(self, shift,
              use_tree=False,
              segment=82,
              search=14.68,
              overlap=12):

        self.command.append("pitch")
        if use_tree:
            self.command.append("-q")
        self.command.append(shift)
        self.command.append(segment)
        self.command.append(search)
        self.command.append(overlap)
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
        self.command.append("reverse")
        return self

    def speed(self, factor, use_semitones=False):
        self.command.append("speed")
        self.command.append(factor if not use_semitones else str(factor) + "c")
        return self

    def synth(self):
        raise NotImplemented()
        return self

    def tempo(self,
              factor,
              use_tree=False,
              opt_flag=None,
              segment=82,
              search=14.68,
              overlap=12):
        self.command.append("pitch")
        if use_tree:
            self.command.append("-q")
        if opt_flag in ("l", "m", "s"):
            self.command.append("-%s" % opt_flag)
        self.command.append(factor)
        self.command.append(segment)
        self.command.append(search)
        self.command.append(overlap)
        return self

    def tremolo(self, freq, depth=40):
        self.command.append("tremolo")
        self.command.append(freq)
        self.command.append(depth)
        return self

    def trim(self, positions):
        self.command.append("trim")
        for position in positions:
            # TODO: check if the position means something
            self.command.append(position)
        return self

    def upsample(self, factor):
        self.command.append("upsample")
        self.command.append(factor)
        return self

    def vad(self):
        raise NotImplemented()
        return self

    def vol(self, gain, type="amplitude", limiter_gain=None):
        self.command.append("vol")
        if type in ["amplitude", "power", "dB"]:
            self.command.append(type)
        else:
            raise ValueError("Type has to be dB, amplitude or power")
        if limiter_gain is not None:
            self.command.append(str(limiter_gain))
        return self

    def custom(self, command):
        """Run arbitrary SoX effect commands.

        Examples:
            custom('echo 0.8 0.9 1000 0.3') for an echo effect.

        References:
            - https://linux.die.net/man/1/soxexam
            - http://sox.sourceforge.net/sox.html
            - http://tldp.org/LDP/LG/issue73/chung.html
            - http://dsl.org/cookbook/cookbook_29.html

        """
        self.command.append(command)
        return self

    def __call__(self,
                 src,
                 dst=np.ndarray,
                 sample_in=44100, # used only for arrays
                 sample_out=None,
                 encoding_out=None,
                 channels_out=None,
                 allow_clipping=True):

        # depending on the input, using the right object to set up the input data arguments
        stdin = None
        if isinstance(src, str):
            infile = FilePathInput(src)
            stdin = src
        elif isinstance(src, np.ndarray):
            infile = NumpyArrayInput(src, sample_in)
            stdin = src
        elif isinstance(src, BufferedReader):
            infile = FileBufferInput(src)
            stdin = infile.data # retrieving the data from the file reader (np array)
        else:
            infile = None

        # finding out which output encoding to use in case the output is ndarray
        if encoding_out is None and dst is np.ndarray:
            if isinstance(stdin, np.ndarray):
                encoding_out = stdin.dtype.type
            elif isinstance(stdin,  str):
                encoding_out = np.float32
        # finding out which channel count to use (defaults to the input file's channel count)
        if channels_out is None:
            channels_out = infile.channels
        if sample_out is None: #if the output samplerate isn't specified, default to input's
            sample_out = sample_in

        # same as for the input data, but for the destination
        if isinstance(dst, str):
            outfile = FilePathOutput(dst, sample_out, channels_out)
        elif dst is np.ndarray:
            outfile = NumpyArrayOutput(encoding_out, sample_out, channels_out)
        elif isinstance(dst, BufferedWriter):
            outfile = FileBufferOutput(dst, sample_out, channels_out)
        else:
            outfile = None

        cmd = shlex.split(
            ' '.join([
                'sox',
                '-N',
                '-V1' if allow_clipping else '-V2',
                infile.cmd_prefix if infile is not None else "-d",
                outfile.cmd_suffix if outfile is not None else "-d",
            ] + list(map(str, self.command))),
            posix=False)

        logging.debug("Running command : %s" % cmd)
        if isinstance(stdin, np.ndarray):
            stdout, stderr = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate(stdin.tobytes(order="F"))
        else:
            stdout, stderr = Popen(cmd, stdout=PIPE, stderr=PIPE).communicate()

        if stderr:
            raise RuntimeError(stderr.decode())
        elif stdout:
            outsound = np.fromstring(stdout, dtype=encoding_out)
            if channels_out > 1:
                outsound = outsound.reshape((channels_out, int(len(outsound) / channels_out)),
                                            order='F')
            if isinstance(outfile, FileBufferOutput):
                outfile.write(outsound)
            return outsound
