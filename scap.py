from ctypes import windll
from PIL import Image, ImageWin

import time
import win32api
import win32con
import win32gui
import win32process
import win32ui

import util

class ScreenCapture:

    def __init__(self):
        self._hwnd = None
        self._bounds = None
        self._valid = False
        self._mouse_pos = (0, 0)
        self._lparam = 0
        self._wparam = 0

        # Find the Nox window.
        self._find_nox()

    def valid(self):
        return self._valid

    def capture(self):
        # Get the display context.
        dc_handle = win32gui.GetWindowDC(self._hwnd)
        dc = win32ui.CreateDCFromHandle(dc_handle)

        # Copy the display context.
        w, h = util.CAP_SIZE
        cdc = dc.CreateCompatibleDC()
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(dc, w, h)
        cdc.SelectObject(bitmap)
        cdc.BitBlt((0,0), (w,h), dc, (0,0), win32con.SRCCOPY)

        # Create the image.
        bits = bitmap.GetBitmapBits(True)
        info = bitmap.GetInfo()
        img = Image.frombytes('RGBA', (info['bmWidth'], info['bmHeight']), bits, 'raw', 'BGRA')

        # Release resources.
        win32gui.DeleteObject(bitmap.GetHandle())
        cdc.DeleteDC()
        dc.DeleteDC()
        win32gui.ReleaseDC(self._hwnd, dc_handle)

        return img

    def get_mouse(self):
        return (self._mouse_pos[0], self._mouse_pos[1], self._wparam != 0)

    def mouse_move(self, pos):
        self._mouse_pos = pos
        self._lparam = win32api.MAKELONG(int(pos[0]), int(pos[1]))

        # Send the event to the window.
        win32api.SendMessage(self._hwnd, win32con.WM_MOUSEMOVE, self._wparam, self._lparam)

    def mouse_down(self):
        # Send the event to the window.
        self._wparam = win32con.MK_LBUTTON
        win32api.SendMessage(self._hwnd, win32con.WM_LBUTTONDOWN, self._wparam, self._lparam)

    def mouse_up(self):
        # Send the event to the window.
        self._wparam = 0
        win32api.SendMessage(self._hwnd, win32con.WM_LBUTTONUP, self._wparam, self._lparam)

    def mouse_click(self, pos=None):
        if pos is not None:
            self.mouse_move(pos)
        self.mouse_down()
        self.mouse_up()

        time.sleep(0.1)

    def mouse_drag(self, pos1, pos2, duration=0.5):
        delta = (pos2[0]-pos1[0], pos2[1]-pos1[1])

        # Move the mouse to the start location.
        self.mouse_move(pos1)
        self.mouse_down()

        # Drag.
        start = time.time()
        while True:
            # Determine what fraction of the duration has elapsed.
            now = time.time()
            frac = (now - start) / duration
            if frac >= 1.0:
                break

            # Set the mouse position.
            pos = (int(pos1[0]+frac*delta[0]), int(pos1[1]+frac*delta[1]))
            self.mouse_move(pos)
            time.sleep(0.001)

        # Move the mouse to the end location.
        self.mouse_move(pos2)
        self.mouse_up()

        time.sleep(0.1)

    def _find_nox(self):
        # Enumerate all windows.
        toplist, winlist = [], []
        def cb(hwnd, _):
            pid = win32process.GetWindowThreadProcessId(hwnd)

            try:
                handle = win32api.OpenProcess(
                    win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                    False,
                    pid[1])
                process_name = win32process.GetModuleFileNameEx(handle, 0)
                window_title = win32gui.GetWindowText(hwnd)
                winlist.append((hwnd, process_name, window_title))
            except:
                pass
        win32gui.EnumWindows(cb, toplist)

        # Find Nox.
        nox_windows = [(h,p,t) for h,p,t in winlist if 'nox.exe' in p.lower()]
        nox = None
        for window in nox_windows:
            if window[2] not in ['Dialog',
                                 'nox',
                                 'Nox',
                                 'Form',
                                 'QTrayIconMessageWindow',
                                 '__wglDummyWindowFodder',
                                 'NVOGLDC invisible',
                                 'MSCTFIME UI',
                                 'Default IME']:
                nox = window
                break
        if nox is None:
            # Nox not found.
            return

        # Find the child window that contains the screen.
        def handleChild(hwnd, lparam):
            title = win32gui.GetWindowText(hwnd)
            if title == 'ScreenBoardClassWindow':
                # Make sure the child window is the correct size.
                x, y, x2, y2 = win32gui.GetClientRect(hwnd)
                if x2 - x != util.CAP_SIZE[0] or y2 - y != util.CAP_SIZE[1]:
                    return

                self._hwnd = hwnd
                self._valid = True
        parent_hwnd = nox[0]
        win32gui.EnumChildWindows(parent_hwnd, handleChild, None)
