import pygame as pg
from Model import Model
from View import View
from Controller import Controller


def main():

    pg.init()

    model = Model()
    view = View(model)
    controller = Controller(model, view)

    running = True
    while running:

        if not controller.CheckEvents():
            running = False

        view.Update()


if __name__ == '__main__':

    main()
