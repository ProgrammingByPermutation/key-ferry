import multiprocessing
import subprocess
import os
import sys
import tkinter
import tkinter.messagebox
import tkinter.filedialog

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
        self.recording = False  # Indicates if we're currently recording
        self.record_button = None  # A reference to the record button
        self.play_button = None  # A reference to the playback button
        self.event = None  # A reference to the event handle to end the recording process
        self.values = None  # A list of values outputted by the recording process
        self.playing_process = None  # The subprocess that is playing a file currently


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
        process = multiprocessing.Process(target=logger_worker, args=(global_info.values, global_info.event),
                                          name='Recorder Process')
        process.start()

        # Swap the text for the user
        text = 'Stop Recording'
    else:
        # If we've stopped recording, set the event handle to end the other process we spawned.
        global_info.event.set()

        # Open a save file dialog so the user can save their script
        file = tkinter.filedialog.asksaveasfile(mode='w', defaultextension=".py")

        # If the cancel button wasn't pressed, save the script
        if file is not None:
            write_to_file(file, global_info.values)

        # Swap the text for the user
        text = 'Record'

    # Save the new text to the button
    global_info.record_button['text'] = text


def write_to_file(file, events):
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
    print('sys.path.append(r"%s")' % os.getcwd(), file=file)
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


def logger_worker(return_values, event):
    """
    This function will be launched in a separate process to allow the key/mouse logger to allow it full use of the
    process' application thread.
    :param return_values: The interprocess collection to store the output in.
    :param event: The event handle that will be signaled to tell the process to end.
    """
    rec = recorder.WindowsRecorder(return_values)
    rec.start()
    event.wait()


def play_file(global_info):
    # TODO: Fill out this method will recorder logic for canceling in the middle of a playback

    # Ask the user for the file
    file = tkinter.filedialog.askopenfilename()

    # If the user didn't push cancel launch a subprocess
    if file is not None:
        global_info.playing_process = subprocess.Popen(sys.executable + ' ' + file)


if __name__ == '__main__':
    # Create the global information object that holds all our data
    global_info = GlobalInfo()

    # Create the interprocess list that will record all our keystrokes and mouse clicks
    manager = multiprocessing.Manager()
    global_info.values = manager.list()

    # Create the event handle we'll use to signal the process to end
    global_info.event = manager.Event()

    # Create our GUI
    window = tkinter.Tk()
    global_info.record_button = tkinter.Button(window, text='Record', command=lambda: record_click(global_info))
    global_info.play_button = tkinter.Button(window, text='Play File', command=lambda: play_file(global_info))
    global_info.record_button.pack()
    global_info.play_button.pack()
    window.mainloop()

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
