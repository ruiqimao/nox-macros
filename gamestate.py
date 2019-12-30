import util

from PIL import ImageDraw

import cv2
import colorsys
import numpy as np
import time

class HomeState:

    @staticmethod
    def identify(frame, data):
        return frame.has_template('downloads')

    @staticmethod
    def parse(frame, data, overlay):
        self = HomeState()

        self._downloads_loc = frame.match_template('downloads')[0]

        draw = ImageDraw.Draw(overlay)
        x, y = self._downloads_loc
        draw.ellipse((x-10,y-10,x+10,y+10), outline=(255,0,0,255), width=2)

        return self, overlay

    def click_downloads(self, scap):
        scap.mouse_click(self._downloads_loc)

class DefaultState:

    @staticmethod
    def identify(frame, data):
        return True

    @staticmethod
    def parse(frame, data, overlay):
        return DefaultState(), overlay

States = [HomeState,
          DefaultState]
