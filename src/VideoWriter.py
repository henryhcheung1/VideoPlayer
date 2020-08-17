import subprocess as sp
import numpy as np


class VideoWriter:

    def __init__(self, filename, fps, size, audiofile=None):

        cmd = ["ffmpeg",
               '-y',
               '-f', 'rawvideo',
               '-vcodec', 'rawvideo',
               '-s', '%dx%d' % (size[0], size[1]),  # size: w x h
               '-pix_fmt', 'rgb24',
               '-r', '%f' % fps,  # fps
               '-i', '-',
               '-an',
               '-vcodec', 'mpeg4',
               filename]

        # check audio

        # self.proc = sp.Popen(cmd, stdout=None, stdin=sp.PIPE, stderr=sp.PIPE)
        self.proc = sp.Popen(cmd, stdout=None, stdin=sp.PIPE, stderr=None)

    def write_frame(self, frame_array):

        # frame_array is a numpy array
        # self.proc.stdin.write(frame_array.tostring())

        self.proc.stdin.write(frame_array)

    def close(self):

        if self.proc:
            self.proc.stdin.close()
            self.proc.wait()
        self.proc = None


def WriteVideo(clip, filename, fps, size, audiofile=None):

    writer = VideoWriter(filename, clip.fps, size)

    for t in np.arange(0, clip.duration, 1.0 / fps):

        raw_frame = clip.get_frame(t)

        # frame = np.frombuffer(raw_frame, dtype='uint8')
        # writer.write_frame(frame)

        writer.write_frame(raw_frame)

    writer.close()


# test

# from VideoFileClip import VideoFileClip

# clip = VideoFileClip("Butterfly.mp4")

# WriteVideo(clip, "outputtest.avi", 30, (640, 360))
