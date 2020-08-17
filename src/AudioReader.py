import subprocess as sp
import numpy as np

from VideoReader import ffmpeg_parse_info


class AudioReader():

    def __init__(self, filename, sample_rate=44100,
                 num_bytes=2, buffersize=200000, channels=2):

        # 2 channels for stereo sound
        # 44100 Hz sampling rate

        self.filename = filename
        self.channels = channels
        self.num_bytes = num_bytes
        self.sample_rate = sample_rate

        result = ffmpeg_parse_info(filename)

        self.duration = result['duration']

        self.buffersize = min(self.duration * self.sample_rate, buffersize)

        self.proc = None

        self.pos = 0  # sample

    def initialize(self, time=0):

        self.close()

        args = []
        if time != 0:
            args = ['-ss', '%f' % time]

        args.extend(['-i', self.filename])

        cmd = ['ffmpeg'] + args + \
            ['-loglevel', 'error',
             '-f', 's16le',
             '-acodec', 'pcm_s16le',
             '-ar', '%d' % self.sample_rate,
             "-ac", '%d' % self.channels,
             '-vcodec', 'rawvideo', '-']

        self.proc = sp.Popen(
            cmd,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            stdin=None,
            bufsize=self.buffersize)

    def skip_chunk(self, chunk):

        _ = self.proc.stdout.read(chunk * self.num_bytes * self.channels)

        # self.proc.stdout.flush()

        self.pos += chunk

    def read_chunk(self, chunk):

        raw_samples = self.proc.stdout.read(
            chunk * self.num_bytes * self.channels)

        audio_array = np.frombuffer(raw_samples, dtype="int16")

        self.pos += chunk

        return audio_array.reshape(
            int(len(audio_array) / self.channels), self.channels)

    def get_samples(self, time):

        pos = int(self.sample_rate * time)

        # ffmpeg not initialized or not within skip distance
        if not self.proc or (pos < self.pos) or (pos > (self.pos + 1000000)):

            self.initialize(time)

        elif pos > self.pos:

            self.skip_chunk(pos - self.pos)

        self.pos = pos

        return self.read_chunk(self.buffersize)

    def close(self):

        if self.proc:
            self.proc.terminate()
            self.proc.stdout.close()
            self.proc.stderr.close()
            self.proc.wait()
            self.proc = None
