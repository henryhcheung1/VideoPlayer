from AudioReader import AudioReader
import pygame as pg
import time
import numpy as np


class AudioFileClip:

    def __init__(self, filename, sample_rate=44100,
                 num_bytes=2, buffersize=200000):

        self.filename = filename
        self.reader = AudioReader(filename, sample_rate, num_bytes, buffersize)

        self.sample_rate = self.reader.sample_rate
        self.duration = self.reader.duration

        self.buffersize = self.reader.buffersize

        self.channels = self.reader.channels
        self.num_bytes = num_bytes

    def get_samples(self, time):

        return self.reader.get_samples(time)

    def close(self):
        if self.reader:
            self.reader.close()
            self.reader = None


def PlayAudio(audio, sample_rate, buffersize,
              audio_queue, video_flag, audio_flag, t=0):

    pg.mixer.quit()

    pg.mixer.pre_init(audio.sample_rate, size=(-8) *
                      audio.num_bytes, channels=audio.channels)
    pg.mixer.init()

    time_interval = buffersize / sample_rate
    # time_slices = np.arange(t, audio.duration, time_interval)

    sound_array = audio.get_samples(0)
    sound = pg.sndarray.make_sound(sound_array)

    audio_flag.set()
    video_flag.wait()

    channel = sound.play()
    skip = False

    print("audio.duration" + str(audio.duration))

    audio_time = time_interval

    while audio_time < audio.duration:

        # print("Audio thread time: " + str(audio_time))

        sound_array = audio.get_samples(audio_time)

        print(sound_array)

        sound = pg.sndarray.make_sound(sound_array)

        while channel.get_busy():

            time.sleep(0.003)

            if not video_flag.is_set():
                # pause audio

                channel.pause()
                video_flag.wait()
                channel.unpause()

            if not audio_queue.empty():

                response = audio_queue.get()

                if isinstance(response, float):
                    # response is time

                    audio_time = response
                    channel.stop()
                    skip = True

                elif not response:
                    # terminate audio

                    channel.stop()
                    del channel
                    return

        if skip:
            skip = False
            continue
        channel = sound.play()

        audio_time += time_interval
