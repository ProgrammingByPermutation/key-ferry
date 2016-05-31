import inspect
import multiprocessing
import os
import threading
import win32api

import win32com.client
import win32con

import python_executor
import recording.constants as constants
import utilities.converter as converter
import utilities.listeners as listeners


class WindowsPlaybackManager:
    """
    Manager class that plays back recorded files for Windows.
    """
    # TODO: Thread-safe object
    DEFAULT_TIMEOUT = 30

    def __init__(self, file, on_playback_started=None, on_playback_ended=None):
        """
        Initializes a new instance of the WindowsPlaybackManager class. This class only supports a single playback.
        If the playback ends, either because the user chose to or the file completed,
        :param file: The string filename to play.
        :param on_playback_started: The function to call when file playback starts. Should be a pickle-able iterable.
        :param on_playback_ended: The function to call when file playback ends. Should be a pickle-able iterable.
        """

        # Create the interprocess list that will record all our keystrokes and mouse clicks
        self.__key_logger = listeners.WindowsListener()
        self.__key_logger.add_listener(self)
        self.__recorded_script_process = None
        self.__script_ended_thread = None
        self.__released = False
        self.__on_playback_started = on_playback_started
        self.__on_playback_ended = on_playback_ended
        self.__shell = win32com.client.Dispatch("WScript.Shell")
        self.file = file

    def start(self):
        """
        Starts the playback of events. This can only be called once. New objects must be created to perform
        an additional playback.
        """
        # Notify everyone just before the playback is about to start
        if self.__on_playback_started is not None:
            for func in self.__on_playback_started:
                func()

        # Process that plays back the file
        self.__recorded_script_process = multiprocessing.Process(target=python_executor.execute_file,
                                                                 args=(self.file,),
                                                                 name='Executing Playback Process')
        self.__recorded_script_process.daemon = True
        self.__recorded_script_process.start()

        # Thread to wait for the script to end
        self.__script_ended_thread = threading.Thread(target=self.script_ended_thread_worker,
                                                      name='Script Ended Thread')
        self.__script_ended_thread.daemon = True
        self.__script_ended_thread.start()

    def on_mouse_event(self, event):
        """
        Handles recording mouse events.
        :param event: The event that occurred.
        """
        # Do nothing
        pass

    def on_keyboard_event(self, event):
        """
        Routes keyboard events.
        :param event: The event to route.
        """
        if event.Type == constants.EventType.KEYBOARD and not event.Injected and event.KeyID == 123:
            self.release()

    def script_ended_thread_worker(self):
        """
        This function is launched in a separate 'Script Ended Thread' thread which polls to see if the
        'Key Logger Worker Process' process has ended to clean up all of this classes resources.
        """
        self.__recorded_script_process.join()

        # Terminate the terminator thread
        self.release()

    def stop(self):
        """
        Stops the playback of events. This causes the object to be disposed of, the playback cannot be restarted.
        """
        self.release()

    @staticmethod
    def key_press(key):
        """
        Static method that simulates a keyboard press.
        :param key: The key identifier to send to windows
        """
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys(key)
        except Exception as e:
            e_msg = win32api.FormatMessage(e.excepinfo[5])
            print("Failure replaying the '", key, "' key with the following exception: ", e_msg, end='', sep='')

            # if is_down_only:
            #     win32api.keybd_event(key_id, 0, win32con.KEYEVENTF_EXTENDEDKEY, 0)
            # elif is_up_only:
            #     win32api.keybd_event(key_id, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)
            # else:
            #     win32api.keybd_event(key_id, 0, 0, 0)

    @staticmethod
    def mouse_click(x, y, down, left):
        """
        Static method that simulates a mouse click.
        :param x: The x-coordinate of the click.
        :param y: The y-coordinate of the click.
        :param down: Indicates if the click is a keypress down
        :param left: Indicates if the click is a left keypress
        """
        win32api.SetCursorPos((x, y))

        if down:
            if left:
                code = win32con.MOUSEEVENTF_LEFTDOWN
            else:
                code = win32con.MOUSEEVENTF_RIGHTDOWN
        else:
            if left:
                code = win32con.MOUSEEVENTF_LEFTUP
            else:
                code = win32con.MOUSEEVENTF_RIGHTUP

        win32api.mouse_event(code, x, y, 0, 0)

    @staticmethod
    def create_executable_playback_file(file, events):
        """
        Writes a list of events to an executable script for the user.
        :param file: The file to write to.
        :param events: The list of events to create a script from.
        """

        # Print header
        print('# Mandatory imports', file=file)
        print('import time', file=file)
        print('import sys', file=file)
        print('', file=file)
        print('', file=file)
        print("# Set Python's path", file=file)
        print('sys.path.append(r"%s%s")' % (os.path.dirname(inspect.getfile(WindowsPlaybackManager)), r'\..'),
              file=file)
        print('from playback.playback import WindowsPlaybackManager', file=file)
        print('', file=file)
        print('', file=file)

        # Find the longest string
        max_length = 0

        # Gather events in script form
        for x in range(0, len(events)):
            event = curr = events[x]
            if event.Type == constants.EventType.MOUSE:
                event.Executable = 'WindowsPlaybackManager.mouse_click(%s, %s, %s, %s)' % (
                    event.Position[0], event.Position[1], event.Is_Down, event.Is_Left)

                length = len(event.Executable)
                if length > max_length:
                    max_length = length + 4
            elif event.Type == constants.EventType.KEYBOARD:
                converted_key = converter.to_send_key(event.Key, event.Is_Ctrl, event.Is_Alt, event.Is_Shift)
                event.Executable = 'WindowsPlaybackManager.key_press("%s")' % (converted_key or event.Key)

                length = len(event.Executable)
                if length > max_length:
                    max_length = length + 4
            events[x] = curr

        # Print everything to the file
        for event in events:
            print("time.sleep(%s)" % event.Time, file=file)
            if event.Type == constants.EventType.MOUSE:
                print('%-*s%s' % (max_length, event.Executable, "# Window: %s" % event.WindowName), file=file)
            elif event.Type == constants.EventType.KEYBOARD:
                message = ''
                if event.Is_Shift:
                    message += "Shift + "
                if event.Is_Alt:
                    message += "Alt + "
                if event.Is_Ctrl:
                    message += "Ctrl + "

                print('%-*s%s' % (max_length, event.Executable, "# Key: %s%s " % (message, event.Key)), file=file)

    def release(self):
        """
        Releases the managed and un-managed resources associated with the instance.
        """
        if self.__released:
            return

        self.__released = True

        # End the playback violently
        recorded_script_process = self.__recorded_script_process
        if recorded_script_process is not None:
            recorded_script_process.terminate()
            self.__recorded_script_process = None

        # Stop listening for key presses
        if self.__key_logger is not None:
            self.__key_logger.remove_listener(self)
            self.__key_logger = None

        # Start releasing resources
        script_ended_thread = self.__script_ended_thread
        if script_ended_thread is not None:
            if script_ended_thread.is_alive():
                try:
                    # Will throw exception if script_ended_thread is the one that called release
                    script_ended_thread.join(WindowsPlaybackManager.DEFAULT_TIMEOUT)

                    if script_ended_thread.is_alive():
                        print("[Error] Script Ended Thread didn't end during timeout of: " +
                              str(WindowsPlaybackManager.DEFAULT_TIMEOUT))
                except:
                    pass
            self.__script_ended_thread = None

        self.file = None

        # Clear the listeners collections
        if self.__on_playback_started is not None:
            self.__on_playback_started.clear()
            self.__on_playback_started = None

        # Notify the listeners of the end of playback
        if self.__on_playback_ended is not None:
            for func in self.__on_playback_ended:
                func()
            self.__on_playback_ended.clear()
            self.__on_playback_ended = None
