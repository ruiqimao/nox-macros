class Macro:

    def __init__(self, scap, parser):
        self._scap = scap
        self._parser = parser

        parser.set_data(dict())

    def run(self):
        pass
