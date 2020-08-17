import pygame as pg


class Controller:

    def __init__(self, model, view):

        self.model = model
        self.view = view

    def CheckEvents(self):

        for event in pg.event.get():
            if event.type == pg.QUIT:

                print("CloseAudio")

                self.model.CloseVideo()
                self.model.CloseAudio()

                return False

            if event.type == pg.MOUSEBUTTONUP:

                mouse_pos = pg.mouse.get_pos()

                if self.view.play_pause_button.collidepoint(mouse_pos):

                    if not self.model.playing:

                        print("play button pressed")

                        self.model.PlayVideo(self.model.frame_time)

                    elif self.model.playing:

                        print("pause button pressed")

                        self.model.PauseVideo()

                elif self.view.load_button.collidepoint(mouse_pos):

                    print("load button pressed")

                    self.model.PauseVideo()

                    filename = self.view.GetUserInput("Enter Filename: ")
                    self.model.LoadVideo(filename)

                    self.view.ResizeWindow(*self.model.video.size)

                elif self.model.video is not None:

                    # if self.view.rewind_button.collidepoint(mouse_pos):

                    #     print("rewind buttons pressed")

                    #     self.model.ReversePlayVideo()

                    if self.view.seek_bar.collidepoint(mouse_pos):

                        print("seek bar pressed")

                        print("mouse pos: " + str(mouse_pos))
                        print("left: " + str(self.view.seek_bar.left))
                        print("width: " + str(self.view.seek_bar.width))

                        self.model.SetFrameTime(
                            self.view.CalculateFrameTime(
                                mouse_pos[0]))

                        self.model.SeekAudioThread(self.model.frame_time)

        return True
