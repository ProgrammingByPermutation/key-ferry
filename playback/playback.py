import threading
import recording.constants as constants
import win32api
import win32con
import time
import recording.recorder as recorder
import os


class WindowsPlaybackManager:
    """
    Manager class that plays back recorded files for Windows.
    """

    def __init__(self, events):
        """
        Initializes a new instance of the WindowsPlaybackManager class.
        :param events: The list of events to playback
        """
        if len(events) <= 0:
            return

        self.__listener = recorder.WindowsListener([self])
        self.__events = list(events)
        self.__index = -1
        self.__increment_event()

    def on_mouse_event(self, event):
        """
        Does nothing, just here to satisfy the interface.
        """
        pass

    def on_keyboard_event(self, event):
        """
        Quits the application if the ESC key is pressed.
        """
        if not event.Injected and event.Ascii == 27:
            self.release()
            os._exit(-1)

    def __on_timer_tick(self):
        """
        Handles executing the current action and incrementing to the next event.
        """
        if self.__curr_event.Type == constants.EventType.MOUSE:
            WindowsPlaybackManager.click(self.__curr_event.Position[0], self.__curr_event.Position[1])
        elif self.__curr_event.Type == constants.EventType.KEYBOARD:
            win32api.keybd_event(self.__curr_event.KeyID, 0, 0, 0)
        self.__increment_event()

    def __increment_event(self):
        """
        Increments to the next available event.
        """

        # Increment the index by 1
        self.__index += 1

        # If our index exceed our list, we're done here. The timer will not start itself again.
        # Otherwise, increment to the next event and reset the timer
        if len(self.__events) > self.__index:
            self.__curr_event = self.__events[self.__index]
            self.__timer = threading.Timer(self.__curr_event.Time, WindowsPlaybackManager.__on_timer_tick, args=(self,))
            self.__timer.start()

    @staticmethod
    def click(x, y):
        """
        Static method that simulates a mouse click.
        :param x: The x-coordinate of the click.
        :param y: The y-coordinate of the click.
        """
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    def release(self):
        """
        Releases the managed and un-managed resources associated with the instance.
        """
        self.__listener.release()
