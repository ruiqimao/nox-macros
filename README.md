# Advanced Nox Macros

Advanced Nox Macros is a stencil for interacting with arbitrary Android programs on a Nox emulator.

## Dependencies

The program only works on Windows. It will not run on macOS or Linux.

The program requires Python 3.6.x to run.

Additionally, the following packages, which can be installed using pip, are also needed:

* pillow

* opencv-python

* pywin32

## Running

The program assumes that the game is running on a Nox instance at 1280x720 resolution. It will fail to recognize any Nox instances running at any other resolutions.

To start the macro program, simply run `python3 main.py` in a terminal or run the included `run.bat` file.

## Example Macro

There is an example macro included. This macro simply waits until the Downloads icon is visible on screen, then clicks it.

The noteworthy files to examine are:

* `gamestate.py`: This file is where all custom states for your application go.

* `tmatcher.py`: This file contains all the definitions for templates that the built in template matcher will use.

* `templates/downloads.png`: This is the example template file that is used to look for the Downloads button.

* `macros/example.py`: This file is where the macro-specific code goes.

## Additional Features

The library contains many features not covered in the example macro. However, as I am too lazy to document all of it... **Good luck**.
