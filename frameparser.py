from frame import Frame
from gamestate import States
from tmatcher import TemplateMatcher

import util

from PIL import Image, ImageDraw

import cv2
import numpy as np
import traceback

class FrameParser:

    def __init__(self):
        # Initiate blob detector.
        blob_detector_params = cv2.SimpleBlobDetector_Params()
        blob_detector_params.filterByColor = False
        blob_detector_params.filterByArea = False
        blob_detector_params.filterByCircularity = False
        blob_detector_params.filterByConvexity = False
        blob_detector_params.filterByInertia = False
        self._blob_detector = cv2.SimpleBlobDetector_create(blob_detector_params)

        # Initialize template matcher.
        self._template_matcher = TemplateMatcher()

        # Initialize parser data.
        self._data = dict()

    def parse(self, img):
        # Convert the frame to OpenCV.
        cvframe = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # Create a frame.
        frame = self.create_frame(cvframe)

        # Create an overlay.
        overlay = Image.new('RGBA', util.CAP_SIZE, (0,0,0,0))
        draw = ImageDraw.Draw(overlay)

        # Determine the state.
        state = None
        try:
            for candidate in States:
                if candidate.identify(frame, self._data):
                    state, overlay = candidate.parse(frame, self._data, overlay)

                    # Display the name of the state.
                    draw.rectangle((0,0,1280,18), fill=(0,0,0,200))
                    draw.text((4,2), candidate.__name__, font=util.FONT, fill=(255,255,255,255))
                    break

            if state is not None:
                # Return the state.
                return state, overlay
        except Exception as e:
            print(traceback.format_exc())

        return None

    def set_data(self, data):
        self._data = data

    def count_blobs(self, img):
        return len(self._blob_detector.detect(img))

    def match_template(self, img, template_name, channel=None, asynchronous=False):
        return self._template_matcher.match(img, template_name, channel, asynchronous)

    def create_frame(self, img):
        return Frame(img, self)
