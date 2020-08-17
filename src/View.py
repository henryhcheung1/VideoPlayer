import pygame as pg
import time


class View:

    def __init__(self, model):

        self.screen_width = 1280
        self.screen_height = 720

        self.button_width = 25
        self.button_height = 25

        self.padding = 10

        self.model = model

        self.screen = pg.display.set_mode(
            [self.screen_width, self.screen_height])

        # self.play_pause_button = pg.Rect(self.screen_width//2 - 0.5*self.button_width, self.screen_height - 1.5*self.button_height, self.button_width, self.button_height)
        # self.load_button = pg.Rect(self.screen_width//2 + self.button_width, self.screen_height - 1.5*self.button_height, self.button_width, self.button_height)
        # self.rewind_button = pg.Rect(self.screen_width//2 - 2*self.button_width, self.screen_height - 1.5*self.button_height, self.button_width, self.button_height)
        self.seek_bar = pg.Rect(
            self.padding,
            self.screen_height -
            2 *
            self.button_height,
            self.screen_width -
            2 *
            self.padding,
            1)

        self.play_pause_button = pg.Rect(
            self.screen_width //
            2 -
            1.5 *
            self.button_width,
            self.screen_height -
            1.5 *
            self.button_height,
            self.button_width,
            self.button_height)
        self.load_button = pg.Rect(
            self.screen_width //
            2 +
            0.5 *
            self.button_width,
            self.screen_height -
            1.5 *
            self.button_height,
            self.button_width,
            self.button_height)

    def Update(self):

        if self.model.playing:

            if not self.model.VideoDonePlaying():

                self.DisplayFrame()

        # draw buttons
        pg.draw.rect(self.screen, [0, 128, 255], self.play_pause_button)
        pg.draw.rect(self.screen, [255, 153, 51], self.load_button)
        pg.draw.rect(self.screen, [128, 128, 128], self.seek_bar)
        # pg.draw.rect(self.screen, [0,255,153], self.rewind_button)

        pg.display.flip()

    def GetUserInput(self, string):

        return input(string)

    def DisplayFrame(self):

        frame_time = self.model.frame_time

        current_time = self.model.Time()

        print("frame_time:  " + str(frame_time))
        # print("current_time:  " + str(current_time))

        if frame_time < (current_time - self.model.play_start_time):

            frame = self.model.GetFrame()

            a = pg.surfarray.make_surface(frame.swapaxes(0, 1))
            self.screen.blit(a, (0, 0))

    def ResizeWindow(self, w, h):

        print("ResizeWindow: " + str(w) + ", " + str(h))

        self.screen_width = w
        self.screen_height = h

        self.screen = pg.display.set_mode([w, h])

        # self.play_pause_button.center = (self.screen_width//2, self.screen_height - self.button_height)
        # self.load_button.center = (self.screen_width//2 + 1.5*self.button_width, self.screen_height - self.button_height)
        # self.rewind_button.center = (self.screen_width//2 - 1.5*self.button_width, self.screen_height - self.button_height)

        self.play_pause_button.center = (
            self.screen_width // 2,
            self.screen_height - self.button_height)
        self.load_button.center = (
            self.screen_width // 2 + 1.5 * self.button_width,
            self.screen_height - self.button_height)

        self.seek_bar.width = self.screen_width - 2 * self.padding
        self.seek_bar.center = (
            self.screen_width // 2,
            self.screen_height - 2 * self.button_height)

    def CalculateFrameTime(self, pos):

        return ((pos - self.seek_bar.left) / self.seek_bar.width) * \
            self.model.video.duration
