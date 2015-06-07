import threading
import win32api
import time

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

        self.__listener = recorder.WindowsListener()
        self.__events = collections.LinkedList(events)
        self.__curr_event_node = self.__events.head
        self.__timer = None
        self.started = False

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
            self.stop()

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
        """
        Starts the playback of events. If the playback was previously started and stopped this method will resume
        where the previous playback left off.
        """
        # If we have exceeded our list, we're done here. The timer will not start itself again.
        # Otherwise, increment to the next event and reset the timer
        if self.__curr_event_node is not None:
            self.started = True
            self.__listener.add_listener(self)
            self.__start_timer()

    def stop(self):
        """
        Stops the playback of events. This does not dispose of any resources, playback can be re-started.
        """
        self.started = False
        self.__listener.remove_listener(self)
        self.__timer.cancel()

    def __start_timer(self):
        """
        Creates a timer object to play the next thing in the playlist.
        """
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
        if self.started:
            self.stop()

        if self.__timer is not None:
            self.__timer.cancel()
            self.__timer = None

        if self.__listener is not None:
            self.__listener = None

        if self.__events is not None:
            self.__events = None

        if self.__curr_event_node is not None:
            self.__curr_event_node = None
