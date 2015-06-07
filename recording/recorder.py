from __future__ import print_function
import recording.constants as constants
import datetime
import threading
import pyHook
import pythoncom
import recording.exceptions as exceptions

ArgumentError = exceptions.ArgumentError


class WindowsListener:
    """
    Hooks onto Windows keyboard and mouse events, pushing callbacks to the subscribing class.
    """

    def __init__(self, listeners):
        """
        Initializes a new instance of the WindowsListener class.
        :param listeners: A list of listeners to call when keyboard or mouse event occur. Listeners must implement an
        on_mouse_event(event) method and an on_keyboard_event(event) method.
        """

        # Check that we received listeners
        if None == listeners or 0 == len(listeners):
            raise (ArgumentError, "listeners cannot be None")

        # Check that listeners have the correct contract
        for x in listeners:
            x_methods = dir(x)
            if 'on_mouse_event' not in x_methods:
                raise (ArgumentError, "listeners must define a on_mouse_event(event) method")
            elif 'on_keyboard_event' not in x_methods:
                raise (ArgumentError, "listeners must define a on_keyboard_event(event) method")

        self.__listeners = listeners
        self.__thread = threading.Thread(target=self.__start_thread)
        self.__thread.start()

    def __start_thread(self):
        """
        Starts a new thread that will wait for keyboard and mouse events to occur globally.
        """

        # Create the hook manager
        self.__hook_manager = pyHook.HookManager()

        # Register mouse and keyboard events globally
        self.__hook_manager.MouseAllButtonsDown = lambda event: WindowsListener.__on_mouse_event(self, event)
        self.__hook_manager.KeyDown = lambda event: WindowsListener.__on_keyboard_event(self, event)

        # Hook into the mouse and keyboard events
        self.connect()

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

    def connect(self):
        """
        Connects to the Windows hooks to receive callbacks about mouse and keyboard events.
        """
        self.__hook_manager.HookMouse()
        self.__hook_manager.HookKeyboard()

    def disconnect(self):
        """
        Disconnects from the Windows hooks to receive callbacks about mouse and keyboard events.
        """
        self.__hook_manager.UnhookMouse()
        self.__hook_manager.UnhookKeyboard()

    def release(self):
        """
        Releases the resources used by the current instance of the class.
        """
        self.__hook_manager.UnhookMouse()
        self.__hook_manager.UnhookKeyboard()


class WindowsRecorder(WindowsListener):
    """
    Hooks onto Windows keyboard and mouse events, storing a list of recorded events.
    """

    def __init__(self):
        """
        Initializes a new instance of the WindowsRecorder class.

        Attributes:
            events: The list of events that have been recorded.
        """
        WindowsListener.__init__(self, [self])
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

    def release(self):
        """
        Releases the resources used by the current instance of the class.
        """
        WindowsListener.release(self)

        if None != self.events:
            self.events.clear()
