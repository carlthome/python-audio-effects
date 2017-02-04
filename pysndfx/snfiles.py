import logging
import shlex
import wave
from subprocess import PIPE, run

import numpy as np

ENCODINGS_MAPPING = {np.int16: "s16",
                     np.float32: "f32",
                     np.float64: "f64"}

PIPE_CHAR = "-"

class SoxInput:
    pipe = "-"

    def __init__(self):
        self.cmd_prefix = None


class FilePathInput(SoxInput):

    def __init__(self, filepath):
        super().__init__()
        info_cmd = 'sox --i -c ' + filepath
        logging.debug("Running info command : %s" % info_cmd)
        stdout = run(shlex.split(info_cmd, posix=False),
                     stdout=PIPE,
                     stderr=PIPE).stdout
        self.channels = int(stdout)
        self.cmd_prefix = filepath


class FileBufferInput(SoxInput):

    def __init__(self, fp):
        super().__init__()
        wave_file = wave.open(fp, mode="rb") # wave.open() seems to support only 16bit encodings
        self.channels = wave_file.getnchannels()
        self.data = np.frombuffer(wave_file.readframes(wave_file.getnframes()), dtype=np.int16)
        self.cmd_prefix = ' '.join(["-t s16", # int16 encoding by default
                                    "-r " + str(wave_file.getframerate()),
                                    "-c " + str(self.channels),
                                    PIPE_CHAR
                                    ])


class NumpyArrayInput(SoxInput):

    def __init__(self, snd_array, rate):
        super().__init__()
        self.channels = snd_array.ndim
        self.cmd_prefix = ' '.join(["-t " + ENCODINGS_MAPPING[snd_array.dtype.type],
                                    "-r " + str(rate),
                                    "-c " + str(self.channels),
                                    PIPE_CHAR
                                    ])

class SoxOutput:

    def __init__(self):
        self.cmd_suffix = None


class FilePathOutput(SoxOutput):

    def __init__(self, filepath, encoding, samplerate, channels):
        super().__init__()
        self.cmd_suffix = ' '.join(["-t " + ENCODINGS_MAPPING[encoding],
                                    "-r " + str(samplerate),
                                    "-c " + str(channels),
                                    filepath,
                                    ])


class FileBufferOutput(SoxOutput):

    def __init__(self, fp, samplerate, channels):
        super().__init__()
        self.writer = wave.open(fp, mode="wb")
        self.writer.setnchannels(channels)
        self.writer.setframerate(samplerate)
        self.writer.setsampwidth(2)
        self.cmd_suffix = ' '.join(["-t " + ENCODINGS_MAPPING[np.int16],
                                    "-r " + str(samplerate),
                                    "-c " + str(channels),
                                    PIPE_CHAR,
                                    ])

    def write(self, data):
        self.writer.writeframesraw(data)


class NumpyArrayOutput(SoxOutput):

    def __init__(self, encoding, samplerate, channels):
        super().__init__()
        self.cmd_suffix = ' '.join(["-t " + ENCODINGS_MAPPING[encoding],
                                    "-r " + str(samplerate),
                                    "-c " + str(channels),
                                    PIPE_CHAR,
                                    ])