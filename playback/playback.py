import threading
import win32api
import time
import os

import win32con

import recording.constants as constants
import recording.recorder as recorder
import utilities.collections as collections


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
        self.__events = collections.LinkedList(events)
        self.__curr_event_node = self.__events.head

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
        event = self.__curr_event_node.value
        if event.Type == constants.EventType.MOUSE:
            WindowsPlaybackManager.click(event.Position[0], event.Position[1])
        elif event.Type == constants.EventType.KEYBOARD:
            win32api.keybd_event(event.KeyID, 0, 0, 0)
        self.__increment_event()

    def __increment_event(self):
        """
        Increments to the next available event.
        """

        # If we've already exhausted the list, return
        if self.__curr_event_node is None:
            return

        # Increment to the next event
        self.__curr_event_node = self.__curr_event_node.next

        # Start a new timer
        self.__start_timer()

    def start(self):
        # Try to start the timer
        self.__start_timer()

    def __start_timer(self):
        # If we have exceeded our list, we're done here. The timer will not start itself again.
        # Otherwise, increment to the next event and reset the timer
        if self.__curr_event_node is not None:
            self.__timer = threading.Timer(self.__curr_event_node.value.Time, WindowsPlaybackManager.__on_timer_tick,
                                           args=(self,))
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
