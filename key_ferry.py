import multiprocessing
import os
import tkinter
import tkinter.messagebox

import tkinter.filedialog

import playback.playback as playback
import gui.main_window as main_window
import recording.recorder as recorder
import recording.constants as constants

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


def record_click():
    """
    Click event for the record button.
    """

    # Swap the recording flag to the opposite
    global_info.recording = not global_info.recording

    if global_info.recording:
        # If we're recording create a new process for the logger to run in, unfortunately the key logging technology
        # that we're using and the GUI technology BOTH need to be in full use of the main application thread at all
        # times. To get around a conflict, or some complex schema for hot swapping between them, we'll just launch
        # the logger in a new process where it can hog the application thread to it's heart's content.
        global_info.end_recording_event.clear()
        process = multiprocessing.Process(target=logger_worker,
                                          args=(global_info.end_recording_event, global_info.recorded_events),
                                          name='Recorder Process')
        process.start()

        global_info.window.on_record_started()
    else:
        # If we've stopped recording, set the event handle to end the other process we spawned.
        global_info.end_recording_event.set()

        # Open a save file dialog so the user can save their script
        file = tkinter.filedialog.asksaveasfile(mode='w', defaultextension=".py")

        # If the cancel button wasn't pressed, save the script
        if file is not None:
            playback.WindowsPlaybackManager.create_executable_playback_file(file, global_info.recorded_events)

        global_info.window.on_record_ended()


def logger_worker(event, recording_list=None, callback_queue=None):
    """
    This function will be launched in a separate process to allow the key/mouse logger to allow it full use of the
    process' application thread.
    :param event: The event handle that will be signaled to tell the process to end.
    :param recording_list: The interprocess collection to store the output in.
    :param callback_queue: The queue to call when an input occurs.
    """
    rec = recorder.WindowsRecorder(recording_list, callback_queue)
    rec.start()
    event.wait()


def on_playback_started():
    """
    Wrapper for the Tkinter window's on_playback_started method. Required because of the pickling performed inside of
    the WindowsPlaybackManager class.
    """
    global_info.window.on_playback_started()


def on_playback_ended():
    """
    Wrapper for the Tkinter window's on_playback_ended method. Required because of the pickling performed inside of
    the WindowsPlaybackManager class.
    """
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
            global_info.playing_back = not global_info.playing_back
    else:
        # Stop the playback
        global_info.playing_file.stop()
        global_info.playing_file = None
        global_info.playing_back = not global_info.playing_back


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
    global_info.window.record_button['command'] = lambda: record_click()
    global_info.window.play_button['command'] = lambda: play_file()
    global_info.window.show()

    if global_info.playing_file is not None:
        global_info.playing_file.stop()

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
