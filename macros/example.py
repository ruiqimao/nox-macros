import time

class Macro:

    def __init__(self, scap, parser):
        self._scap = scap
        self._parser = parser

        parser.set_data(dict())

    def run(self):
        scap = self._scap
        parser = self._parser

        # Wait for the home state to appear.
        state = self._wait_for_state('HomeState')

        # Click the downloads button.
        state.click_downloads(scap)

    def _wait_for_state(self, target_name, timeout=None):
        scap = self._scap
        parser = self._parser

        start = time.time()
        while True:
            # Get the most updated state.
            state = parser.wait()
            if state is None:
                continue
            state_name = type(state).__name__

            # Check if the target state has been reached.
            if state_name == target_name:
                return state

            if timeout is not None:
                now = time.time()
                if now - start >= timeout:
                    return None
