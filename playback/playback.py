import os
import threading
import inspect
import multiprocessing
import win32api

import win32con

import python_executor
import recording.constants as constants
import recording.recorder as recorder


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
        manager = multiprocessing.Manager()
        self.__key_logger_process = None
        self.__key_logger_process_end_event = manager.Event()
        self.__key_logger_key_press_queue = manager.Queue()
        self.__recorded_script_process = None
        self.__user_cancel_thread = None
        self.__script_ended_thread = None
        self.__released = False
        self.__on_playback_started = on_playback_started
        self.__on_playback_ended = on_playback_ended
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

        # Process to listen for the user's keystrokes and mouse clicks
        self.__key_logger_process = multiprocessing.Process(target=self.key_logger_worker,
                                                            name='Key Logger Worker Process')
        self.__key_logger_process.daemon = True
        self.__key_logger_process.start()

        # Thread to listen to the output of the key logger process to see if the user pushed the exit key
        self.__user_cancel_thread = threading.Thread(target=self.user_cancel_thread_worker,
                                                     name='User Cancel Thread')
        self.__user_cancel_thread.daemon = True
        self.__user_cancel_thread.start()

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

    def script_ended_thread_worker(self):
        """
        This function is launched in a separate 'Script Ended Thread' thread which polls to see if the
        'Key Logger Worker Process' process has ended to clean up all of this classes resources.
        """
        self.__recorded_script_process.join()

        # Terminate the terminator thread
        self.release()

    def user_cancel_thread_worker(self):
        """
        This function is launched in a separate 'User Cancel Thread' thread which polls the output of the
        'Key Logger Worker Process' process to determine if the user has requested the playback to stop.
        """
        while True:
            ret = self.__key_logger_key_press_queue.get()
            if ret is None:
                return

            if ret.Type != constants.EventType.MOUSE and not ret.Injected and ret.KeyID == 123:
                self.release()
                return

    def key_logger_worker(self):
        """
        This function will be launched in a separate 'Key Logger Worker Process' process to allow the key/mouse logger
        to allow it full use of the process' application thread.
        """
        rec = recorder.WindowsRecorder(event_queue=self.__key_logger_key_press_queue)
        rec.start()
        self.__key_logger_process_end_event.wait()

    def stop(self):
        """
        Stops the playback of events. This causes the object to be disposed of, the playback cannot be restarted.
        """
        self.release()

    @staticmethod
    def key_press(key_id, is_down_only=False, is_up_only=False):
        """
        Static method that simulates a keyboard press.
        :param key_id: The key identifier to send to windows
        :param is_down_only: Indicates if the key press is pressing down and holding the key.
        :param is_up_only: Indicates if the key press is releasing a previously held down key.
        """
        if is_down_only:
            win32api.keybd_event(key_id, 0, win32con.KEYEVENTF_EXTENDEDKEY, 0)
        elif is_up_only:
            win32api.keybd_event(key_id, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)
        else:
            win32api.keybd_event(key_id, 0, 0, 0)

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

        code = None
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

        # Gather events in executable form
        for x in range(0, len(events)):
            event = curr = events[x]
            if event.Type == constants.EventType.MOUSE:
                event.Executable = 'WindowsPlaybackManager.mouse_click(%s, %s, %s, %s)' % (
                    event.Position[0], event.Position[1], event.Is_Down, event.Is_Left)

                length = len(event.Executable)
                if length > max_length:
                    max_length = length + 4
            elif event.Type == constants.EventType.KEYBOARD:
                event.Executable = 'WindowsPlaybackManager.key_press(%s, %s, %s)' % (
                    event.KeyID, event.Is_Held_Down, event.Is_Release)

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
                print('%-*s%s' % (max_length, event.Executable, "# Key: %s " % event.Key), file=file)

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

        # Give everyone a chance to clean up
        key_logger_process_end_event = self.__key_logger_process_end_event
        if key_logger_process_end_event is not None:
            key_logger_process_end_event.set()

        key_logger_key_press_queue = self.__key_logger_key_press_queue
        if key_logger_key_press_queue is not None:
            key_logger_key_press_queue.put(None)

        # Start releasing resources
        key_logger_process = self.__key_logger_process
        if key_logger_process is not None:
            if key_logger_process.is_alive():
                key_logger_process.join(WindowsPlaybackManager.DEFAULT_TIMEOUT)

                if key_logger_process.is_alive():
                    key_logger_process.terminate()
            self.__key_logger_process = None

        user_cancel_thread = self.__user_cancel_thread
        if user_cancel_thread is not None:
            if user_cancel_thread.is_alive():
                try:
                    # Will throw exception if user_cancel_thread is the one that called release
                    user_cancel_thread.join(WindowsPlaybackManager.DEFAULT_TIMEOUT)

                    if user_cancel_thread.is_alive():
                        print("[Error] User Cancel Thread didn't end during timeout of: " +
                              str(WindowsPlaybackManager.DEFAULT_TIMEOUT))
                except:
                    pass

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

        self.__key_logger_process_end_event = None
        self.__key_logger_key_press_queue = None
        self.__user_cancel_thread = None
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
