from frameparser import FrameParser

import util

from PIL import Image
from threading import Lock

import multiprocessing as mp
import time

PACKET_STOP  = 0
PACKET_FRAME = 1
PACKET_DATA  = 2

class GameParser:

    def __init__(self):
        self._overlay = Image.new('RGBA', util.CAP_SIZE, (0,0,0,0))
        self._state = None

        self._pipe, opipe = mp.Pipe()
        self._process = mp.Process(target=GameParser.run, args=(opipe,))
        self._process.start()
        self._busy = False
        self._wait_counter = 0
        self._lock = Lock()

    # Stop the parser.
    def stop(self):
        # Signal to the process to stop.
        self._pipe.send((PACKET_STOP, None))

        # Flush the input queue.
        while self._pipe.recv() is not None:
            continue

    # Feed a frame to the parser.
    def feed(self, frame):
        with self._lock:
            # Feed a frame to the process.
            if not self._busy:
                self._pipe.send((PACKET_FRAME, frame))
                self._busy = True
                if self._wait_counter == 2:
                    self._wait_counter = 1

            # Read the latest data.
            while self._pipe.poll():
                self._busy = False
                data = self._pipe.recv()

                self._state, self._overlay = data
                if self._wait_counter == 1:
                    self._wait_counter = 0

    # Set data for the parser.
    def set_data(self, data):
        self._pipe.send((PACKET_DATA, data))

    # Get an overlay to display.
    def get_overlay(self):
        with self._lock:
            return self._overlay

    # Get the current state.
    def get_state(self):
        with self._lock:
            return self._state

    # Wait for the frame parser to catch up.
    def wait(self):
        self._wait_counter = 2
        while not self._wait_counter == 0:
            time.sleep(0.1)

        return self.get_state()

    @staticmethod
    def run(pipe):
        cached = None, Image.new('RGBA', util.CAP_SIZE, (0,0,0,0))

        parser = FrameParser()

        while True:
            # Read the next packet.
            packet_type, packet_data = pipe.recv()

            if packet_type == PACKET_STOP:
                # Flush the input queue.
                while pipe.poll():
                    pipe.recv()

                # Signal that the input queue has been flushed.
                pipe.send(None)

                return

            if packet_type == PACKET_FRAME:
                data = parser.parse(packet_data)
                if data is not None:
                    cached = data
                    pipe.send(data)
                else:
                    pipe.send(cached)

            if packet_type == PACKET_DATA:
                parser.set_data(packet_data)
