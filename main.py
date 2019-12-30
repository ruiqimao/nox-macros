from gamedisplay import GameDisplay
from gameparser import GameParser
from macros.example import Macro
from scap import ScreenCapture

import traceback

def main():
    # Initiate screen capture.
    scap = ScreenCapture()
    if not scap.valid():
        print('A suitable Nox instance could not be found')
        return

    # Create a parser.
    parser = GameParser()

    # Initialize the game display.
    display = GameDisplay(scap, parser)
    display.start()

    # Initialize the macro.
    macro = Macro(scap, parser)

    # Run the macro.
    input('Press <ENTER> to start the macro\n')
    try:
        macro.run()
    except Exception as e:
        print(traceback.format_exc())

    input('Press <ENTER> to quit\n')

    display.stop()
    parser.stop()

if __name__ == '__main__':
    main()
