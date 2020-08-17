import numpy as np
import time
from VideoFileClip import VideoFileClip
from AudioFileClip import PlayAudio
import threading
import queue


class Model:

    def __init__(self):

        self.video = None

        self.play_start_time = None
        self.playing = False

        self.frame_time = 0  # frame_i / fps [1/fps - duration]
        self.delta_time = 0  # time difference between video time positions

        self.audio_thread = None

        # audio, video synchronization flags
        self.video_flag = None
        self.audio_flag = None

        self.audio_queue = None  # message passing queue between audio & video playback threads

        self.pause_start_time = 0
        self.pause_time = 0

    def LoadVideo(self, filename):

        self.CloseAudio()
        self.CloseVideo()

        self.video = VideoFileClip(filename)

        print("self.video.audio.sample_rate")
        print(self.video.audio.sample_rate)

        print("self.video.fps")
        print(self.video.fps)

    def SaveVideo(self, filename):

        if self.video:

            print("SaveVideo")
            # self.video.save()

        pass

    def SetVideo(self, video):

        self.videofile = video

    def GetVideo(self):

        return self.video

    def Time(self):

        return time.time() - self.pause_time + self.delta_time

    def GetFrame(self):

        raw_frame = self.video.get_frame(self.frame_time)

        self.frame_time += 1 / (self.video.fps)

        frame = np.frombuffer(raw_frame, dtype='uint8')

        w, h = self.video.size

        frame = frame.reshape((h, w, 3))

        # clip.reader.proc.stdout.flush()
        return frame

    def VideoDonePlaying(self):

        return self.frame_time >= self.video.duration

    def PlayVideo(self, t=0):

        self.playing = True

        if self.audio_thread is None:
            # either first time playing

            print("PlayVideo reinit audio thread!!!")

            self.play_start_time = time.time()

            self.frame_time = t

            self.video_flag = threading.Event()
            self.audio_flag = threading.Event()

            self.StartAudioThread(t)

            self.video_flag.set()  # video is ready
            self.audio_flag.wait()  # wait until audio ready

        else:  # t == self.frame_time:
            # unpause

            print("Unpaused video, Resuming audio")
            self.video_flag.set()

            self.pause_time = self.pause_time + time.time() - self.pause_start_time
            self.pause_start_time = 0

            print("self.pause_time: " + str(self.pause_time))

    def PauseVideo(self):

        if self.video_flag is not None:

            self.pause_start_time = time.time()

            self.playing = False

            self.video_flag.clear()

    def ReversePlayVideo(self):

        pass

    def StartAudioThread(self, t=0):

        self.audio_queue = queue.Queue()  # holds the time when the audio stops

        audio_clip = self.video.audio

        self.audio_thread = threading.Thread(
            target=PlayAudio,
            args=(
                audio_clip,
                audio_clip.sample_rate,
                audio_clip.buffersize,
                self.audio_queue,
                self.video_flag,
                self.audio_flag,
                t))
        self.audio_thread.start()

    def SeekAudioThread(self, t):

        print("SeekAudioThread")

        if self.audio_thread is not None:

            self.audio_queue.put(t)

            self.pause_time = 0  # reset pause time
            self.pause_start_time = time.time()  # hack

    def CloseVideo(self):

        if self.video is not None:

            self.video.close()

            self.frame_time = 0
            self.delta_time = 0

            self.video = None

    def CloseAudio(self):

        if self.audio_thread is not None:

            self.audio_queue.put(False)  # terminate audio

            self.video_flag.set()  # set flag to get out of wait() (pause) in audio playback

            self.audio_thread = None
            self.video_flag = None
            self.audio_flag = None

    def SetFrameTime(self, t):

        print("SetFrameTime")

        self.delta_time = t - (time.time() - self.play_start_time)
        self.frame_time = t
