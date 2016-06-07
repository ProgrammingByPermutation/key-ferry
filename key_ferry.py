import multiprocessing
import os
import tkinter
import tkinter.filedialog
import tkinter.messagebox

import gui.main_window as main_window
import playback.playback as playback
import recording.constants as constants
import recording.recorder as recorder
import utilities.listeners as listeners

EventType = constants.EventType


class GlobalInfo:
    """
    A global information class that holds all the global variables passed through the various
    threads and processes
    """

    def __init__(self):
        """
        Initializes a new instance of the GlobalInfo class.
        """
        self.window = None  # A reference to the main window
        self.recording = False  # Indicates if we're currently recording
        self.end_recording_event = None  # A reference to the event handle to end the recording process
        self.recorded_events = None  # A list of values outputted by the recording process
        self.playing_file = None  # The subprocess that is playing a file currently
        self.playing_back = False  # Indicates if we're currently playing back a file
        self.input_listener = listeners.WindowsListener()
        self.windows_recorder = None


def record_click():
    """
    Click event for the record button.
    """
    # Swap the recording flag to the opposite
    global_info.recording = not global_info.recording

    if global_info.recording:
        # Start the recording
        process_to_ignore = os.getpid() if global_info.window.should_ignore_own_window.get() else None
        global_info.windows_recorder = recorder.WindowsRecorder(global_info.recorded_events, process_to_ignore)
        global_info.windows_recorder.start()
        global_info.window.on_record_started()
    else:
        # Stop the recording
        if global_info.windows_recorder is not None:
            global_info.windows_recorder.release()
            global_info.windows_recorder = None

        # Open a save file dialog so the user can save their script
        file = tkinter.filedialog.asksaveasfile(mode='w', defaultextension=".py")

        # If the cancel button wasn't pressed, save the script
        if file is not None:
            playback.WindowsPlaybackManager.create_executable_playback_file(file, global_info.recorded_events)
            file.close()
        global_info.recorded_events = manager.list()
        global_info.window.on_record_ended()


def on_playback_started():
    """
    Wrapper for the Tkinter window's on_playback_started method. Required because of the pickling performed inside of
    the WindowsPlaybackManager class.
    """
    global_info.playing_back = True
    global_info.window.on_playback_started()


def on_playback_ended():
    """
    Wrapper for the Tkinter window's on_playback_ended method. Required because of the pickling performed inside of
    the WindowsPlaybackManager class.
    """
    global_info.playing_back = False
    global_info.window.on_playback_ended()


def play_file():
    """
    Click event for the play button.
    """

    if not global_info.playing_back:
        # Ask the user for the file
        file = tkinter.filedialog.askopenfilename()

        # If the user didn't push cancel launch a subprocess
        if file is not None and os.path.exists(file):
            global_info.playing_file = playback.WindowsPlaybackManager(file, [on_playback_started], [on_playback_ended])
            global_info.playing_file.start()
    else:
        # Stop the playback
        global_info.playing_file.stop()
        global_info.playing_file = None


if __name__ == '__main__':
    # Required to stop infinite execution when we freeze
    multiprocessing.freeze_support()

    # Create the global information object that holds all our data
    global_info = GlobalInfo()
    manager = multiprocessing.Manager()
    global_info.end_recording_event = manager.Event()
    global_info.recorded_events = manager.list()

    # Create our GUI
    global_info.window = main_window.MainWindow()
    global_info.window.record_button.config(command=lambda: record_click())
    global_info.window.play_button.config(command=lambda: play_file())
    global_info.window.show()

    if global_info.playing_file is not None:
        global_info.playing_file.stop()

    if global_info.input_listener is not None:
        global_info.input_listener.release()

        # TODO: Combine keyboard events together to save space
        # Text to speech that made me laugh
        # message = ""
        # for event in rec.events:
        #     if event.Type == constants.EventType.KEYBOARD:
        #         if (event.Ascii > 64 and event.Ascii < 91) or (event.Ascii > 96 and event.Ascii < 123):
        #             message += event.Key
        #         else:
        #             message += " "
        #
        # import gtts
        #
        # tts = gtts.gTTS(text=message, lang='en')
        # tts.save(r'computer.mp3')
        # os.system('start ' + r'computer.mp3')
