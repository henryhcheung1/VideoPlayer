from VideoReader import VideoReader
from AudioFileClip import AudioFileClip


class VideoFileClip:

    def __init__(self, filename, target_resolution=None,
                 resize_algorithm='bicubic', pixel_format='rgb24', sample_rate=None):

        self.reader = VideoReader(filename, target_resolution=target_resolution,
                                  resize_algorithm=resize_algorithm,
                                  pixel_format=pixel_format)

        self.duration = self.reader.duration
        self.fps = self.reader.fps
        self.size = self.reader.size  # w x h

        if not sample_rate:
            sample_rate = self.reader.sample_rate

        self.audio = AudioFileClip(filename, sample_rate)

    def get_frame(self, time):
        return self.reader.get_frame(time)

    def close(self):

        if self.reader:
            self.reader.close()
            self.reader = None

        if self.audio:
            self.audio.close()
