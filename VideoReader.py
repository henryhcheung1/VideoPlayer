import subprocess as sp
import re


class VideoReader:

    def __init__(self, filename, target_resolution=None,
                 resize_algorithm='bicubic', pixel_format='rgb24'):

        # target_resolution: w x h

        self.filename = filename
        self.proc = None    # pipe to ffmpeg
        result = ffmpeg_parse_info(filename)
        self.depth = 3  # RGB || YCbCr

        if not target_resolution:
            self.size = result['size']
        else:
            self.size = target_resolution

        w, h = self.size
        self.buffersize = self.depth * w * h + 100

        self.resize_algorithm = resize_algorithm
        self.pixel_format = pixel_format

        self.duration = result['duration']

        self.fps = result['fps']

        self.sample_rate = result['sample_rate']

        self.pos = 1

        self.prev_frame = None

    def initialize(self, time=0):
        # open video with ffmpeg and create a pipe to ffmpeg
        # time: seconds

        self.close()

        args = []
        if time != 0:
            args = ['-ss', '%f' % time]

        args.extend(['-i', self.filename])

        cmd = ['ffmpeg'] + args + \
            ['-loglevel', 'error',
             '-f', 'image2pipe',
             '-vf', 'scale=%d:%d' % (self.size[0], self.size[1]),
             '-sws_flags', self.resize_algorithm,
             "-pix_fmt", self.pixel_format,
             '-vcodec', 'rawvideo', '-']

        self.proc = sp.Popen(
            cmd,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            stdin=None,
            bufsize=self.buffersize)

    def read_frame(self):
        w, h = self.size
        self.prev_frame = self.proc.stdout.read(w * h * self.depth)
        return self.prev_frame

    def skip_frames(self, n=1):

        w, h = self.size

        for _ in range(n):
            self.proc.stdout.read(w * h * self.depth)

        self.pos += n

    def get_frame(self, time):

        pos = int(self.fps * time)

        # print("self.pos: " + str(self.pos))

        # print("pos: " + str(pos))

        # ffmpeg child process not initialized or not within skip distance
        if not self.proc or (pos < self.pos) or (pos > self.pos + 100):

            # print("initializing!!")

            self.initialize(time)

        elif pos > self.pos:

            # print("skip_frames!!")
            self.skip_frames(pos - self.pos - 1)

        else:
            print("pos == self.pos")
            return self.prev_frame

        self.pos = pos

        return self.read_frame()

    def close(self):

        if self.proc:
            self.proc.terminate()
            self.proc.stdout.close()
            self.proc.stderr.close()
            self.proc.wait()
            self.proc = None


def ffmpeg_parse_info(filename):

    cmd = ["ffmpeg", "-i", filename]

    proc = sp.Popen(
        cmd,
        stdout=sp.PIPE,
        stderr=sp.PIPE,
        stdin=None,
        bufsize=10**8)

    (output, error) = proc.communicate()
    infos = error.decode('utf8')

    lines = infos.splitlines()

    result = {}

    # get duration
    line = [l for l in lines if 'Duration: ' in l][0]

    match = re.findall(
        "([0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9])",
        line)[0]

    result['duration'] = convert_seconds(match)

    # get size w x h
    lines_video = [l for l in lines if ' Video: ' in l]

    match = re.search(" [0-9]*x[0-9]*( |,)", lines_video[0])

    result['size'] = [int(x) for x in lines_video[0]
                      [match.start():match.end() - 1].split('x')]

    # get fps
    match = re.search("([0-9]+.)?[0-9]+ fps", lines_video[0])

    result['fps'] = float(
        lines_video[0][match.start():match.end() - 4])  # remove ' fps'

    # get audio
    lines_audio = [l for l in lines if ' Audio: ' in l]

    match = re.search("[0-9]* Hz", lines_audio[0])

    result['sample_rate'] = int(
        lines_audio[0][match.start():match.end() - 3])  # remove ' Hz'

    print(result)

    return result


def convert_seconds(time):

    # HH:MM:SS.SS format

    expr = r"(\d+)"
    match = re.findall(expr, time)

    return 3600 * int(match[0]) + 60 * int(match[1]) + \
        int(match[2]) + int(match[3]) / 10**(len(match[3]))


# import numpy as np
# import pygame as pg
# import time


# ffmpeg_parse_info("Butterfly.mp4")

# # print(convert_seconds("01:12:43.045"))


# reader = VideoReader("Examples\\bunny_1080p_60fps.mp4")
# reader = VideoReader("Examples\\big_buck_bunny_480p_surround-fix.avi")

# reader.initialize()

# print(reader.fps)
# print(reader.duration)

# w, h = reader.size
# d = reader.depth


# # screen = None
# screen = pg.display.set_mode((1000,1000))

# pg.init()

# t0 = time.time()
# t1 = None
# print("t0: " + str(t0))

# frame_count = 0

# for t in np.arange(1.0 / reader.fps, reader.duration - 0.001, 1.0 /
# reader.fps):

#     # print(frame_count)

#     # frame_count += 1
#     # t1 = time.time()

#     # if (t1 - t0 > 10):
#     #     print(frame_count)
#     #     print((t1 - t0))
#     #     print(frame_count / (t1 - t0))
#     #     break

#     # raw_image = reader.read_frame()
#     raw_image = reader.get_frame(t)

#     for event in pg.event.get():
#         if event.type == pg.QUIT:
#             running = False

#     # transform the byte read into a numpy array
#     image = np.frombuffer(raw_image, dtype='uint8')

#     image = image.reshape((h, w, d))

#     reader.proc.stdout.flush()

#     # t1 = time.time()
#     # time.sleep(max(0, t - (t1-t0)))

#     # print("-------------")
#     # print(max(0, t - (t1-t0)))
#     # print("t: " + str(t))
#     # print("t1: " + str(t1))
#     # print(image)
#     # print("-------------")

#     a = pg.surfarray.make_surface(image.swapaxes(0, 1))
#     if screen is None:
#         screen = pg.display.set_mode(image.shape[:2][::-1])
#     screen.blit(a, (0, 0))
#     pg.display.flip()
