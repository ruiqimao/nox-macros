from threading import Thread
from PIL import Image, ImageDraw

import cv2
import numpy as np
import time

import util

class GameDisplay(Thread):

    def __init__(self, scap, parser):
        super().__init__()

        self._running = True
        self._scap = scap
        self._parser = parser
        self._mouse_pos = (0, 0)
        self._mouse_down = False

    def run(self):
        cv2.namedWindow('game')
        cv2.setMouseCallback('game', self._cb_mouse)

        while self._running:
            # Capture a frame.
            frame = self._scap.capture()

            # Feed the frame to the parser.
            self._parser.feed(frame)

            # Get the overlay from the parser.
            overlay = self._parser.get_overlay().copy()

            # Show the current mouse coordinates.
            mouse_string = '%d, %d' % self._mouse_pos
            draw = ImageDraw.Draw(overlay)
            draw.rectangle((0,702,8+util.FONT.getsize(mouse_string)[0],720), fill=(0,0,0,200))
            draw.text((4,704),
                      mouse_string,
                      font=util.FONT,
                      fill=(255,255,255,255))

            # Show the capture mouse coordinates.
            cap_x, cap_y, cap_down = self._scap.get_mouse()
            outline_color = (255,0,0,255) if cap_down else (255,255,255,255)
            draw.ellipse((cap_x-7,cap_y-7,cap_x+7,cap_y+7),
                         outline=outline_color,
                         width=3)

            # Apply the overlay.
            frame = Image.alpha_composite(frame, overlay)

            # Display the frame.
            opencv_frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
            cv2.imshow('game', opencv_frame)

            cv2.waitKey(1)

    def stop(self):
        self._running = False

    def _cb_mouse(self, evt, x, y, flags, params):
        # Update the mouse position.
        self._mouse_pos = (x, y)
        if self._mouse_down:
            self._scap.mouse_move((x,y))

        # Handle mouse clicks.
        if evt == cv2.EVENT_LBUTTONDOWN:
            self._scap.mouse_move((x,y))
            self._scap.mouse_down()
            self._mouse_down = True
        if evt == cv2.EVENT_LBUTTONUP:
            self._scap.mouse_move((x,y))
            self._scap.mouse_up()
            self._mouse_down = False
