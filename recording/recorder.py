from __future__ import print_function
import datetime
import threading
import win32api

import pyHook
import win32con
import pythoncom

import recording.constants as constants
import recording.exceptions as exceptions

ArgumentError = exceptions.ArgumentError


class WindowsListener:
    """
    Hooks onto Windows keyboard and mouse events, pushing callbacks to the subscribing class.
    """
    __instance = None

    def __init__(self):
        """
        Initializes a new instance of the WindowsListener class.
        """
        # TODO: Supposedly we can handle this much better use a metaclass. Should revisit once I understand them.
        if not self.__initialized:
            self.__initialized = True
            self.__listeners = []
            self.__connected = False
            self.__thread = threading.Thread(target=self.__start_thread)
            self.__thread.start()

    def __new__(cls, *args, **kwargs):
        """
        Creates a single instance of the WindowsListener class.
        :param cls: The class that is being "new"ed.
        :param args: The regular arguments.
        :param kwargs: The keyword arguments.
        :return: The singleton instance of the WindowsListener class.
        """
        if cls.__instance is None:
            cls.__instance = object.__new__(cls, *args)
            cls.__initialized = False
        return cls.__instance

    def __start_thread(self):
        """
        Starts a new thread that will wait for keyboard and mouse events to occur globally.
        """

        # Save thread identifier
        self.__main_thread_id = win32api.GetCurrentThreadId()

        # Create the hook manager
        self.__hook_manager = pyHook.HookManager()

        # Register mouse and keyboard events globally
        self.__hook_manager.MouseAllButtonsDown = lambda event: WindowsListener.__on_mouse_event(self, event)
        self.__hook_manager.KeyDown = lambda event: WindowsListener.__on_keyboard_event(self, event)

        # Hook into the mouse and keyboard events
        self.__hook_manager.HookMouse()
        self.__hook_manager.HookKeyboard()

        # Suspend the thread indefinitely waiting for callbacks
        pythoncom.PumpMessages()

    def __on_mouse_event(self, event):
        """
        Handles recording mouse events.
        :param event: The event that occurred.
        :return: True indicating the event should be passed to other event handlers.
        """
        # Notify listeners
        for x in self.__listeners:
            x.on_mouse_event(event)

        # print('MessageName:', event.MessageName)
        # print('Message:', event.Message)
        # print('Time:', event.Time)
        # print('Window:', event.Window)
        # print('WindowName:', event.WindowName)
        # print('Position:', event.Position)
        # print('Wheel:', event.Wheel)
        # print('Injected:', event.Injected)
        # print('---')

        # return True to pass the event to other handlers
        # return False to stop the event from propagating
        return True

    def __on_keyboard_event(self, event):
        """
        Handles recording keyboard events.
        :param event: The event that occurred.
        :return: True indicating the event should be passed to other event handlers.
        """
        # Notify listeners
        for x in self.__listeners:
            x.on_keyboard_event(event)

        # print('MessageName:', event.MessageName)
        # print('Message:', event.Message)
        # print('Time:', event.Time)
        # print('Window:', event.Window)
        # print('WindowName:', event.WindowName)
        # print('Ascii:', event.Ascii, chr(event.Ascii))
        # print('Key:', event.Key)
        # print('KeyID:', event.KeyID)
        # print('ScanCode:', event.ScanCode)
        # print('Extended:', event.Extended)
        # print('Injected:', event.Injected)
        # print('Alt', event.Alt)
        # print('Transition', event.Transition)
        # print('---')

        # return True to pass the event to other handlers
        # return False to stop the event from propagating
        return True

    def add_listener(self, listener):
        """
        Adds a listener to the listener list.
        :param listener: The listener to subscribe. Listeners should have a on_mouse_event(self, event) and
                         on_keyboard_event(self, event) method.
        :exception ValueError: Thrown if the listener is already subscribed.
        """
        if self in self.__listeners:
            raise ValueError("list.append(x): x already in list")

        x_methods = dir(listener)
        if 'on_mouse_event' not in x_methods:
            raise ArgumentError("listeners must define a on_mouse_event(event) method")
        elif 'on_keyboard_event' not in x_methods:
            raise ArgumentError("listeners must define a on_keyboard_event(event) method")
        self.__listeners.append(listener)

    def remove_listener(self, listener):
        """
        Removes a listener from the listener list.
        :param listener: The listener to un-subscribe.
        :exception ValueError: Thrown if the listener is not already subscribed.
        """
        self.__listeners.remove(listener)

    def release(self):
        """
        Releases the resources used by the current instance of the class.
        """
        self.__listeners.clear()
        win32api.PostThreadMessage(self.__main_thread_id, win32con.WM_QUIT, 0, 0)
        self.__hook_manager.UnhookMouse()
        self.__hook_manager.UnhookKeyboard()
        self.__thread.join()
        self.__instance = None


class WindowsRecorder:
    """
    Hooks onto Windows keyboard and mouse events, storing a list of recorded events.
    """

    def __init__(self):
        """
        Initializes a new instance of the WindowsRecorder class.

        Attributes:
            events: The list of events that have been recorded.
        """
        self.__listener = WindowsListener()
        self.events = []
        self.__time_since_last_command = datetime.datetime.now()

    def on_mouse_event(self, event):
        """
        Handles recording mouse events.
        :param event: The event that occurred.
        """
        # Set the type
        event.Type = constants.EventType.MOUSE

        # Record the event
        self.__record_event(event)

    def on_keyboard_event(self, event):
        """
        Handles recording keyboard events.
        :param event: The event that occurred.
        """
        # Set the type
        event.Type = constants.EventType.KEYBOARD

        # Record the event
        self.__record_event(event)

    def __record_event(self, event):
        """
        Record the passed in event.
        :param event: The event to record.
        """
        # Set the time
        curr_time = datetime.datetime.now()
        event.Time = (curr_time - self.__time_since_last_command).total_seconds()
        self.__time_since_last_command = curr_time

        # Add to the events list
        self.events.append(event)

    def start(self):
        """
        Starts recording keyboard and mouse events.
        """
        self.__listener.add_listener(self)

    def stop(self):
        """
        Stops recording keyboard and mouse events.
        """
        self.__listener.remove_listener(self)

    def release(self):
        """
        Releases the resources used by the current instance of the class.
        """
        if None != self.__listener:
            self.stop()
            self.__listener = None

        if None != self.events:
            self.events.clear()
            self.events = None

        if None != self.__time_since_last_command:
            self.__time_since_last_command = None
