from __future__ import print_function
import threading
import multiprocessing

import pyHook

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
        Initializes a new instance of the WindowsListener class. An object of type WindowsListener expects full use of
        the main application thread. If you have any other objects with this requirement (like a GUI) this class will
        have to be marshaled to another process. Otherwise, the blocking portion of this class will launch in a separate
        thread to ease use.
        """
        # TODO: Supposedly we can handle this much better using a metaclass. Should revisit once I understand them.
        if not self.__initialized:
            self.__initialized = True

            # Create the list of input listeners
            self.__listeners = []

            # Create the list that will pass information from the hook manager's
            # process to this process.
            manager = multiprocessing.Manager()
            self.__inputs_queue = manager.Queue()

            # Create the process that will listen for inputs from the user.
            self.__hook_manager_process = multiprocessing.Process(target=self.hook_manager_process,
                                                                  name='Hook Manager Process')
            self.__hook_manager_process.daemon = True
            self.__hook_manager_process.start()

            # Create the thread for listening for inputs and passing them to the listeners.
            self.__input_listener_thread = threading.Thread(target=self.__hook_listener, name='Input Listener Thread')
            self.__input_listener_thread.daemon = True
            self.__input_listener_thread.start()

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

    def __hook_listener(self):
        """
        This function is launched in a separate 'User Cancel Thread' thread which polls the output of the
        'Key Logger Worker Process' process to determine if the user has requested the playback to stop.
        """
        while True:
            event = self.__inputs_queue.get()
            if event is None:
                return

            if event.Type == constants.EventType.KEYBOARD:
                for x in self.__listeners:
                    x.on_keyboard_event(event)
            elif event.Type == constants.EventType.MOUSE:
                for x in self.__listeners:
                    x.on_mouse_event(event)

    def hook_manager_process(self):
        """
        Hook Manager process' logic responsible for receiving inputs from the keyboard and mouse.
        """

        # Save thread identifier
        # self.__main_thread_id = win32api.GetCurrentThreadId()

        # Create the hook manager
        hook_manager = pyHook.HookManager()

        # Register mouse and keyboard events globally
        hook_manager.MouseLeftDown = lambda event: WindowsListener.__on_mouse_event(self, event, is_left=True,
                                                                                    is_down=True)
        hook_manager.MouseLeftUp = lambda event: WindowsListener.__on_mouse_event(self, event, is_left=True, is_up=True)
        hook_manager.MouseRightDown = lambda event: WindowsListener.__on_mouse_event(self, event, is_right=True,
                                                                                     is_down=True)
        hook_manager.MouseRightUp = lambda event: WindowsListener.__on_mouse_event(self, event, is_right=True,
                                                                                   is_up=True)
        hook_manager.KeyDown = lambda event: WindowsListener.__on_keyboard_event(self, event, True)
        hook_manager.KeyUp = lambda event: WindowsListener.__on_keyboard_event(self, event, False)

        # Hook into the mouse and keyboard events
        hook_manager.HookMouse()
        hook_manager.HookKeyboard()

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
        event.Type = constants.EventType.MOUSE
        event.Is_Left = is_left
        event.Is_Right = is_right
        event.Is_Down = is_down
        event.Is_Up = is_up
        event.Is_Double = False

        # Notify listeners
        self.__inputs_queue.put(event)

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
        event.Type = constants.EventType.KEYBOARD
        event.Is_Down = is_down

        # Notify listeners
        self.__inputs_queue.put(event)

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
        self.__instance = None
        self.__initialized = False
        self.__inputs_queue.put(None)

        # These need to happen on inside of the hook manager process...but we don't care about
        # cleaning them up because we only clean up the hook manager's process when the program ends.
        # So for now we won't further complicate the code and take the path of apathy.
        # # win32api.PostThreadMessage(self.__main_thread_id, win32con.WM_QUIT, 0, 0)
        # # self.__hook_manager.UnhookMouse()
        # # self.__hook_manager.UnhookKeyboard()
