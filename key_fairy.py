import multiprocessing
import subprocess
import threading
import sys
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
        self.playing_process = None  # The subprocess that is playing a file currently
        self.interprocess_queue = None  # A queue used to listen for stopping a playback


def record_click(global_info):
    """
    Click event for the record button
    :param global_info: The global information object to access and mutate
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

        # Swap the text for the user
        text = 'Stop Recording'
    else:
        # If we've stopped recording, set the event handle to end the other process we spawned.
        global_info.end_recording_event.set()

        # Open a save file dialog so the user can save their script
        file = tkinter.filedialog.asksaveasfile(mode='w', defaultextension=".py")

        # If the cancel button wasn't pressed, save the script
        if file is not None:
            playback.WindowsPlaybackManager.create_executable_playback_file(file, global_info.recorded_events)

        # Swap the text for the user
        text = 'Record'

    # Save the new text to the button
    global_info.window.record_button['text'] = text


def logger_worker(event, recording_list=None, callback_queue=None):
    """
    This function will be launched in a separate process to allow the key/mouse logger to allow it full use of the
    process' application thread.
    :param event: The event handle that will be signaled to tell the process to end.
    :param recording_list: The interprocess collection to store the output in.
    :param callback_queue: The queue to call when an input occurs.
    :return:
    """
    rec = recorder.WindowsRecorder(recording_list, callback_queue)
    rec.start()
    event.wait()


def terminate_playback_thread(global_info):
    # TODO: Move logic to playback class
    while True:
        ret = global_info.interprocess_queue.get()
        if ret is None:
            return

        if ret.KeyID == 123:
            # Terminate the listening process
            global_info.end_recording_event.set()

            # Terminate the playback
            global_info.playing_process.terminate()
            return


def playback_finished_thread(global_info):
    # TODO: Move logic to playback class
    # Wait for playback
    global_info.playing_process.wait()

    # Terminate the terminator thread
    global_info.interprocess_queue.put(None)

    # Terminate the listening process
    global_info.end_recording_event.set()


def play_file(global_info):
    # TODO: Move logic to playback class

    # Ask the user for the file
    file = tkinter.filedialog.askopenfilename()

    # If the user didn't push cancel launch a subprocess
    if file is not None:
        global_info.end_recording_event.clear()
        process = multiprocessing.Process(target=logger_worker,
                                          args=(global_info.end_recording_event, None, global_info.interprocess_queue),
                                          name='Playback Listener Process')
        process.start()

        global_info.playing_process = subprocess.Popen(sys.executable + ' ' + file)

        thread = threading.Thread(target=terminate_playback_thread, name='Terminate Playback Thread',
                                  args=(global_info,))
        thread.daemon = True
        thread.start()

        thread = threading.Thread(target=terminate_playback_thread, name='Process Finished Thread', args=(global_info,))
        thread.daemon = True
        thread.start()


if __name__ == '__main__':
    # Create the global information object that holds all our data
    global_info = GlobalInfo()

    # Create the interprocess list that will record all our keystrokes and mouse clicks
    manager = multiprocessing.Manager()
    global_info.recorded_events = manager.list()

    # Create the event handle we'll use to signal the process to end
    global_info.end_recording_event = manager.Event()

    # Create the queue we'll use to listen for the user telling us to stop a playback
    global_info.interprocess_queue = manager.Queue()

    # Create our GUI
    global_info.window = main_window.MainWindow()
    global_info.window.record_button['command'] = lambda: record_click(global_info)
    global_info.window.play_button['command'] = lambda: play_file(global_info)
    global_info.window.show()

    if global_info.playing_process is not None:
        global_info.playing_process.terminate()

        # rec = recorder.WindowsRecorder()
        # while True:
        #     rec.start()
        #     os.system('notepad')
        #     rec.stop()
        #
        #     print('Number of events: ' + str(len(rec.events)))
        #     print('Helds: ', end="")
        #     print(rec._WindowsRecorder__keys_held_down)
        #
        #     play = playback.WindowsPlaybackManager(rec.events)
        #     play.start()
        #     os.system('notepad')
        #     play.stop()
        #     play.release()
        #     rec.events.clear()
        #
        #     # TODO: Combine keyboard events together to save space
        #
        #     # Text to speech that made me laugh
        #     # message = ""
        #     # for event in rec.events:
        #     #     if event.Type == constants.EventType.KEYBOARD:
        #     #         if (event.Ascii > 64 and event.Ascii < 91) or (event.Ascii > 96 and event.Ascii < 123):
        #     #             message += event.Key
        #     #         else:
        #     #             message += " "
        #     #
        #     # import gtts
        #     #
        #     # tts = gtts.gTTS(text=message, lang='en')
        #     # tts.save(r'computer.mp3')
        #     # os.system('start ' + r'computer.mp3')
