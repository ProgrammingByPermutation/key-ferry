from __future__ import print_function
import recording.constants as constants


class WindowsRecorder:
    """
    Hooks onto Windows keyboard and mouse events.
    """

    def __init__(self):
        """
        Initializes a new instance of the WindowsRecorder class.

        Attributes:
            events: The list of events that have been recorded.
        """
        import threading

        self.__thread = threading.Thread(target=self.__start_thread)
        self.__thread.start()
        self.events = []

    def __start_thread(self):
        """
        Starts a new thread that will wait for keyboard and mouse events to occur globally.
        """
        import pyHook
        import pythoncom

        # Create the hook manager
        self.__hook_manager = pyHook.HookManager()

        # Register mouse and keyboard events globally
        self.__hook_manager.MouseAllButtonsDown = lambda event: WindowsRecorder.__on_mouse_event(self, event)
        self.__hook_manager.KeyDown = lambda event: WindowsRecorder.__on_keyboard_event(self, event)

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
        event.Type = constants.EventType.MOUSE
        self.events.append(event)
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
        event.Type = constants.EventType.KEYBOARD
        self.events.append(event)
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
