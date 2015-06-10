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
        # TODO: Supposedly we can handle this much better using a metaclass. Should revisit once I understand them.
        if not self.__initialized:
            self.__initialized = True
            self.__listeners = []
            self.__connected = False
            self.__thread = threading.Thread(target=self.__thread_target, name='Hook Manager\'s Thread')
            self.__thread.start()
            self.__keys_held_down = []

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

    def __thread_target(self):
        """
        Hook Manager thread's logic responsible for receiving inputs from the keyboard and mouse.
        """

        # Save thread identifier
        self.__main_thread_id = win32api.GetCurrentThreadId()

        # Create the hook manager
        self.__hook_manager = pyHook.HookManager()

        # Register mouse and keyboard events globally
        self.__hook_manager.MouseLeftDown = lambda event: WindowsListener.__on_mouse_event(self, event,
                                                                                           is_left=True, is_down=True)
        self.__hook_manager.MouseLeftUp = lambda event: WindowsListener.__on_mouse_event(self, event,
                                                                                         is_left=True, is_up=True)
        self.__hook_manager.MouseRightDown = lambda event: WindowsListener.__on_mouse_event(self, event,
                                                                                            is_right=True, is_down=True)
        self.__hook_manager.MouseRightUp = lambda event: WindowsListener.__on_mouse_event(self, event,
                                                                                          is_right=True, is_up=True)
        self.__hook_manager.KeyDown = lambda event: WindowsListener.__on_keyboard_event(self, event, True)
        self.__hook_manager.KeyUp = lambda event: WindowsListener.__on_keyboard_event(self, event, False)

        # Hook into the mouse and keyboard events
        self.__hook_manager.HookMouse()
        self.__hook_manager.HookKeyboard()

        # Suspend the thread indefinitely waiting for callbacks
        pythoncom.PumpMessages()

    def __on_mouse_event(self, event, is_left=False, is_right=False, is_down=False, is_up=False):
        """
        Handles recording mouse events.
        :param event: The event that occurred.
        :param is_left: The left button was clicked.
        :param is_right: The right button was clicked.
        :param is_down: The button was pressed down.
        :param is_up: The button was released.
        :return: True indicating the event should be passed to other event handlers.
        """
        event.Is_Left = is_left
        event.Is_Right = is_right
        event.Is_Down = is_down
        event.Is_Up = is_up
        event.Is_Double = False

        # Notify listeners
        for x in self.__listeners:
            x.on_mouse_event(event)

        # print('Is_Left', event.Is_Left)
        # print('Is_Right', event.Is_Right)
        # print('Is_Down', event.Is_Down)
        # print('Is_Up', event.Is_Up)
        # print('Is_Double', event.Is_Double)
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

    def __on_keyboard_event(self, event, is_down):
        """
        Handles recording keyboard events.
        :param event: The event that occurred.
        :param is_down: The key press was down.
        :return: True indicating the event should be passed to other event handlers.
        """
        event.Is_Down = is_down

        # Notify listeners
        for x in self.__listeners:
            x.on_keyboard_event(event)

        # print('Is_Down:', event.Is_Down)
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
    __HOLDABLE_KEYS = [160, 161, 162, 163, 164, 165]
    __CTRL_KEYS = [162, 163]
    __ALT_KEYS = [164, 165]
    __DEL = 46

    def __init__(self):
        """
        Initializes a new instance of the WindowsRecorder class.

        Attributes:
            events: The list of events that have been recorded.
        """
        self.__listener = WindowsListener()
        self.__keys_held_down = []
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
        Routes keyboard events.
        :param event: The event to route.
        """
        if event.Is_Down:
            self.on_key_down_event(event)
        else:
            self.on_key_up_event(event)

    def on_key_up_event(self, event):
        """
        Handles recording key up events. Only a subset of key up events are recorded.
        :param event: The event that occurred.
        """
        current_held_key = [key for key in self.__keys_held_down if key.KeyID == event.KeyID]

        if len(current_held_key) != 0:
            self.__keys_held_down.remove(current_held_key[0])

            # Set the type
            event.Type = constants.EventType.KEYBOARD
            event.Is_Held_Down = False
            event.Is_Release = True

            # Record event
            self.__record_event(event)

    def on_key_down_event(self, event):
        """
        Handles recording key down events. Almost all keyboard recording is in the from of key down presses.
        :param event: The event that occurred.
        """
        # Set the type
        event.Type = constants.EventType.KEYBOARD
        event.Is_Held_Down = False
        event.Is_Release = False

        # If it's a holdable key then wait for the key up
        if event.KeyID in WindowsRecorder.__HOLDABLE_KEYS:
            # If we already recorded this key, don't re-add it to the collection
            if any(key.KeyID == event.KeyID for key in self.__keys_held_down):
                return
            event.Is_Held_Down = True
            self.__keys_held_down.append(event)

        # If this is delete, make sure they aren't holding CTRL + ALT. If they are then windows already stole focus
        # and choked our release keys. We need to record them ourselves so we don't get into a state.
        if event.KeyID == self.__DEL:
            ctrl_intersection = [event for event in self.__keys_held_down if event.KeyID in self.__CTRL_KEYS]
            alt_intersection = [event for event in self.__keys_held_down if event.KeyID in self.__ALT_KEYS]
            if len(ctrl_intersection) > 0 and len(alt_intersection) > 0:
                [self.on_key_up_event(ctrl_event) for ctrl_event in ctrl_intersection]
                [self.on_key_up_event(alt_event) for alt_event in alt_intersection]
            return

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

        if None != self.__keys_held_down:
            self.__keys_held_down.clear()
            self.__keys_held_down = None
