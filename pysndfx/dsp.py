# coding=utf-8
"""A lightweight Python wrapper of SoX's effects."""
import shlex
from io import BufferedReader, BufferedWriter
from subprocess import PIPE, Popen

import numpy as np

from .sndfiles import (
    FileBufferInput,
    FileBufferOutput,
    FilePathInput,
    FilePathOutput,
    NumpyArrayInput,
    NumpyArrayOutput,
    logger,
)


def mutually_exclusive(*args):
    return sum(arg is not None for arg in args) < 2


class AudioEffectsChain:
    def __init__(self):
        self.command = []

    def equalizer(self, frequency, q=1.0, db=-3.0):
        """equalizer takes three parameters: filter center frequency in Hz, "q"
        or band-width (default=1.0), and a signed number for gain or
        attenuation in dB.

        Beware of clipping when using positive gain.
        """
        self.command.append('equalizer')
        self.command.append(frequency)
        self.command.append(str(q) + 'q')
        self.command.append(db)
        return self

    def bandpass(self, frequency, q=1.0):
        """bandpass takes 2 parameters: filter center frequency in Hz and "q"
        or band-width (default=1.0).

        It gradually removes frequencies outside the band specified.
        """
        self.command.append('bandpass')
        self.command.append(frequency)
        self.command.append(str(q) + 'q')
        return self

    def bandreject(self, frequency, q=1.0):
        """bandreject takes 2 parameters: filter center frequency in Hz and "q"
        or band-width (default=1.0).

        It gradually removes frequencies within the band specified.
        """
        self.command.append('bandreject')
        self.command.append(frequency)
        self.command.append(str(q) + 'q')
        return self

    def lowshelf(self, gain=-20.0, frequency=100, slope=0.5):
        """lowshelf takes 3 parameters: a signed number for gain or attenuation
        in dB, filter frequency in Hz and slope (default=0.5, maximum=1.0).

        Beware of Clipping when using positive gain.
        """
        self.command.append('bass')
        self.command.append(gain)
        self.command.append(frequency)
        self.command.append(slope)
        return self

    def highshelf(self, gain=-20.0, frequency=3000, slope=0.5):
        """highshelf takes 3 parameters: a signed number for gain or
        attenuation in dB, filter frequency in Hz and slope (default=0.5).

        Beware of clipping when using positive gain.
        """
        self.command.append('treble')
        self.command.append(gain)
        self.command.append(frequency)
        self.command.append(slope)
        return self

    def highpass(self, frequency, q=0.707):
        """highpass takes 2 parameters: filter frequency in Hz below which
        frequencies will be attenuated and q (default=0.707).

        Beware of clipping when using high q values.
        """
        self.command.append('highpass')
        self.command.append(frequency)
        self.command.append(str(q) + 'q')
        return self

    def lowpass(self, frequency, q=0.707):
        """lowpass takes 2 parameters: filter frequency in Hz above which
        frequencies will be attenuated and q (default=0.707).

        Beware of clipping when using high q values.
        """
        self.command.append('lowpass')
        self.command.append(frequency)
        self.command.append(str(q) + 'q')
        return self

    def limiter(self, gain=3.0):
        """limiter takes one parameter: gain in dB.

        Beware of adding too much gain, as it can cause audible
        distortion. See the compand effect for a more capable limiter.
        """
        self.command.append('gain')
        self.command.append('-l')
        self.command.append(gain)
        return self

    def normalize(self):
        """normalize has no parameters.

        It boosts level so that the loudest part of your file reaches
        maximum, without clipping.
        """
        self.command.append('gain')
        self.command.append('-n')
        return self

    def compand(self, attack=0.2, decay=1, soft_knee=2.0, threshold=-20, db_from=-20.0, db_to=-20.0):
        """compand takes 6 parameters:

        attack (seconds), decay (seconds), soft_knee (ex. 6 results
        in 6:1 compression ratio), threshold (a negative value
        in dB), the level below which the signal will NOT be companded
        (a negative value in dB), the level above which the signal will
        NOT be companded (a negative value in dB). This effect
        manipulates dynamic range of the input file.
        """
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
        """sinc takes 12 parameters:

        high_pass_frequency in Hz,
        low_pass_frequency in Hz,
        left_t,
        left_n,
        right_t,
        right_n,
        attenuation in dB,
        beta,
        phase,
        M,
        I,
        L

        This effect creates a steep bandpass or
        bandreject filter. You may specify as few as the first two
        parameters. Setting the high-pass parameter to a lower value
        than the low-pass creates a band-reject filter.
        """
        self.command.append("sinc")
        if not mutually_exclusive(attenuation, beta):
            raise ValueError("Attenuation (-a) and beta (-b) are mutually exclusive arguments.")
        if attenuation is not None and beta is None:
            self.command.append('-a')
            self.command.append(str(attenuation))
        elif attenuation is None and beta is not None:
            self.command.append('-b')
            self.command.append(str(beta))

        if not mutually_exclusive(phase, M, I, L):
            raise ValueError("Phase (-p), -M, L, and -I are mutually exclusive arguments.")
        if phase is not None:
            self.command.append('-p')
            self.command.append(str(phase))
        elif M is not None:
            self.command.append('-M')
        elif I is not None:
            self.command.append('-I')
        elif L is not None:
            self.command.append('-L')

        if not mutually_exclusive(left_t, left_t):
            raise ValueError("Transition bands options (-t or -n) are mutually exclusive.")
        if left_t is not None:
            self.command.append('-t')
            self.command.append(str(left_t))
        if left_n is not None:
            self.command.append('-n')
            self.command.append(str(left_n))

        if high_pass_frequency is not None and low_pass_frequency is None:
            self.command.append(str(high_pass_frequency))
        elif high_pass_frequency is not None and low_pass_frequency is not None:
            self.command.append(str(high_pass_frequency) + '-' + str(low_pass_frequency))
        elif high_pass_frequency is None and low_pass_frequency is not None:
            self.command.append(str(low_pass_frequency))

        if not mutually_exclusive(right_t, right_t):
            raise ValueError("Transition bands options (-t or -n) are mutually exclusive.")
        if right_t is not None:
            self.command.append('-t')
            self.command.append(str(right_t))
        if right_n is not None:
            self.command.append('-n')
            self.command.append(str(right_n))
        return self

    def bend(self, bends, frame_rate=None, over_sample=None):
        """TODO Add docstring."""
        self.command.append("bend")
        if frame_rate is not None and isinstance(frame_rate, int):
            self.command.append('-f %s' % frame_rate)
        if over_sample is not None and isinstance(over_sample, int):
            self.command.append('-o %s' % over_sample)
        for bend in bends:
            self.command.append(','.join(bend))
        return self

    def chorus(self, gain_in, gain_out, decays):
        """TODO Add docstring."""
        self.command.append("chorus")
        self.command.append(gain_in)
        self.command.append(gain_out)
        for decay in decays:
            modulation = decay.pop()
            numerical = decay
            self.command.append(' '.join(map(str, numerical)) + ' -' + modulation)
        return self

    def delay(self,
              gain_in=0.8,
              gain_out=0.5,
              delays=None,
              decays=None,
              parallel=False):
        """delay takes 4 parameters: input gain (max 1), output gain
        and then two lists, delays and decays.

        Each list is a pair of comma seperated values within
        parenthesis.
        """
        if delays is None:
            delays = list((1000, 1800))
        if decays is None:
            decays = list((0.3, 0.25))
        self.command.append('echo' + ('s' if parallel else ''))
        self.command.append(gain_in)
        self.command.append(gain_out)
        self.command.extend(list(sum(zip(delays, decays), ())))
        return self

    def echo(self, **kwargs):
        """TODO Add docstring."""
        self.delay(**kwargs)

    def fade(self):
        """TODO Add docstring."""
        raise NotImplementedError()

    def flanger(self, delay=0, depth=2, regen=0, width=71, speed=0.5, shape='sine', phase=25, interp='linear'):
        """TODO Add docstring."""
        raise NotImplementedError()

    def gain(self, db):
        """gain takes one paramter: gain in dB."""
        self.command.append('gain')
        self.command.append(db)
        return self

    def mcompand(self):
        """TODO Add docstring."""
        raise NotImplementedError()

    def noise_reduction(self, amount=0.5):
        """TODO Add docstring."""
        # TODO Run sox once with noiseprof on silent portions to generate a noise profile.
        raise NotImplementedError()

    def oops(self):
        """TODO Add docstring."""
        raise NotImplementedError()

    def overdrive(self, gain=20, colour=20):
        """overdrive takes 2 parameters: gain in dB and colour which effects
        the character of the distortion effet.

        Both have a default value of 20. TODO - changing color does not seem to have an audible effect
        """
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
        """phaser takes 6 parameters: input gain (max 1.0), output gain (max
        1.0), delay, decay, speed and LFO shape=trianglar (which must be set to
        True or False)"""
        self.command.append("phaser")
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
        """pitch takes 4 parameters: user_tree (True or False), segment, search
        and overlap."""
        self.command.append("pitch")
        if use_tree:
            self.command.append('-q')
        self.command.append(shift)
        self.command.append(segment)
        self.command.append(search)
        self.command.append(overlap)
        return self

    def loop(self):
        """TODO Add docstring."""
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
        """reverb takes 7 parameters: reverberance, high-freqnency damping,
        room scale, stereo depth, pre-delay, wet gain and wet only (True or
        False)"""
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
        """reverse takes no parameters.

        It plays the input sound backwards.
        """
        self.command.append("reverse")
        return self

    def speed(self, factor, use_semitones=False):
        """speed takes 2 parameters: factor and use-semitones (True or False).

        When use-semitones = False, a factor of 2 doubles the speed and raises the pitch an octave. The same result is achieved with factor = 1200 and use semitones = True.
        """
        self.command.append("speed")
        self.command.append(factor if not use_semitones else str(factor) + "c")
        return self

    def synth(self):
        raise NotImplementedError()

    def tempo(self,
              factor,
              use_tree=False,
              opt_flag=None,
              segment=82,
              search=14.68,
              overlap=12):
        """tempo takes 6 parameters: factor, use tree (True or False), option
        flag, segment, search and overlap).

        This effect changes the duration of the sound without modifying
        pitch.
        """
        self.command.append("tempo")

        if use_tree:
            self.command.append('-q')
        if opt_flag in ('l', 'm', 's'):
            self.command.append('-%s' % opt_flag)
        self.command.append(factor)
        self.command.append(segment)
        self.command.append(search)
        self.command.append(overlap)
        return self

    def tremolo(self, freq, depth=40):
        """tremolo takes two parameters: frequency and depth (max 100)"""
        self.command.append("tremolo")
        self.command.append(freq)
        self.command.append(depth)
        return self

    def trim(self, positions):
        """TODO Add docstring."""
        self.command.append("trim")
        for position in positions:
            # TODO: check if the position means something
            self.command.append(position)
        return self

    def upsample(self, factor):
        """TODO Add docstring."""
        self.command.append("upsample")
        self.command.append(factor)
        return self

    def vad(self):
        raise NotImplementedError()

    def vol(self, gain, type="amplitude", limiter_gain=None):
        """vol takes three parameters: gain, gain-type (amplitude, power or dB)
        and limiter gain."""
        self.command.append("vol")
        if type in ["amplitude", "power", "dB"]:
            self.command.append(type)
        else:
            raise ValueError("Type has to be dB, amplitude or power.")
        if limiter_gain is not None:
            self.command.append(str(limiter_gain))
        print(self.command)
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

    def __call__(
            self,
            src,
            dst=np.ndarray,
            sample_in=44100,  # used only for arrays
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
            stdin = infile.data  # retrieving the data from the file reader (np array)
        else:
            infile = None

        # finding out which output encoding to use in case the output is ndarray
        if encoding_out is None and dst is np.ndarray:
            if isinstance(stdin, np.ndarray):
                encoding_out = stdin.dtype.type
            elif isinstance(stdin, str):
                encoding_out = np.float32
        # finding out which channel count to use (defaults to the input file's channel count)
        if channels_out is None:
            channels_out = infile.channels
        if sample_out is None:  # if the output samplerate isn't specified, default to input's
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
                infile.cmd_prefix if infile is not None else '-d',
                outfile.cmd_suffix if outfile is not None else '-d',
            ] + list(map(str, self.command))),
            posix=False,
        )

        logger.debug("Running command : %s" % cmd)
        if isinstance(stdin, np.ndarray):
            stdout, stderr = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate(stdin.tobytes(order='F'))
        else:
            stdout, stderr = Popen(cmd, stdout=PIPE, stderr=PIPE).communicate()

        if stderr:
            raise RuntimeError(stderr.decode())
        elif stdout:
            outsound = np.fromstring(stdout, dtype=encoding_out)
            if channels_out > 1:
                outsound = outsound.reshape((channels_out, int(len(outsound) / channels_out)), order='F')
            if isinstance(outfile, FileBufferOutput):
                outfile.write(outsound)
            return outsound
