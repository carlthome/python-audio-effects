import logging
import shlex
import wave
from subprocess import Popen, PIPE

import numpy as np

ENCODINGS_MAPPING = {np.int16: "s16",
                     np.float32: "f32"}

PIPE = "-"

class SoxInput:
    pipe = "-"

    def __init__(self):
        self.cmd_prefix = None


class FilePathInput(SoxInput):

    def __init__(self, filepath):
        super().__init__()
        logging.debug("Running info command : %s" % 'sox --i -c ' + src)
        stdout, stderr = Popen(
            shlex.split(
                'sox --i -c ' + filepath, posix=False),
            stdout=PIPE,
            stderr=PIPE).communicate()
        self.channels = int(stdout)
        self.cmd_prefix = filepath


class FileBufferInput(SoxInput):

    def __init__(self, fp):
        super().__init__()
        wave_file = wave.open(fp, mode="rb") # only seems to support 16bit encodings
        self.channels = wave_file.getnchannels()
        self.data = np.frombuffer(wave_file.readframes(wave_file.getnframes()), dtype=np.int16)
        self.cmd_prefix = ' '.join(["-t s16", # int16
                                    "-r " + str(wave_file.getframerate()),
                                    "-c "+ str(self.channels),
                                    PIPE
                                    ])


class NumpyArrayInput(SoxInput):

    def __init__(self, snd_array, rate):
        super().__init__()
        self.channels = snd_array.ndim
        self.cmd_prefix = ' '.join(["-t " + ENCODINGS_MAPPING[snd_array.dtype],
                                    "-r " + str(rate),
                                    "-c " + str(self.channels),
                                    PIPE
                                    ])

class SoxOutput:

    def __init__(self):
        self.cmd_suffix = None


class FilePathOutput(SoxOutput):

    def __init__(self, filepath):
        super().__init__()
        self.cmd_suffix = filepath


class FileBufferOutput(SoxOutput):

    def __init__(self, fp, samplerate, channels):
        super().__init__()
        self.writer = wave.open(fp, mode="wb")
        self.writer.setnchannels(channels)
        self.writer.setframerate(samplerate)
        self.cmd_suffix = ' '.join(["-t " + ENCODINGS_MAPPING[np.int16],
                                    "-r " + str(samplerate),
                                    "-c " + channels,
                                    PIPE,
                                    ])

    def write(self, data):
        self.writer.writeframes(data)


class NumpyArrayOutput(SoxOutput):

    def __init__(self, encoding, samplerate, channels):
        super().__init__()
        self.cmd_suffix = ' '.join(["-t " + ENCODINGS_MAPPING[encoding],
                                    "-r " + str(samplerate),
                                    "-c " + channels,
                                    PIPE,
                                    ])