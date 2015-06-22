import tkinter
import tkinter.messagebox
import tkinter.filedialog

import recording.constants as constants

EventType = constants.EventType


class MainWindow:
    def __init__(self):
        """
        Creates the window and its controls.
        """
        self.window = tkinter.Tk()
        self.window.title("Key Ferry")
        self.record_button = tkinter.Button(self.window, text='Record')
        self.play_button = tkinter.Button(self.window, text='Play File')
        self.record_button.grid(column="0", row="0", padx="15")
        self.play_button.grid(column="1", row="0", padx="15")

    def show(self):
        """
        Shows the window.
        """
        self.window.mainloop()

    def on_playback_started(self):
        """
        Handles logic related to the playback of a file starting.
        """
        self.record_button['state'] = tkinter.DISABLED
        self.play_button['text'] = 'Stop Playback'

    def on_playback_ended(self):
        """
        Handles logic related to the playback of a file ending.
        """
        self.record_button['state'] = tkinter.NORMAL
        self.play_button['text'] = 'Play File'

    def on_record_started(self):
        """
        Handles logic related to the playback of a file starting.
        """
        self.play_button['state'] = tkinter.DISABLED
        self.record_button['text'] = 'Stop Recording'

    def on_record_ended(self):
        """
        Handles logic related to the playback of a file ending.
        """
        self.play_button['state'] = tkinter.NORMAL
        self.record_button['text'] = 'Record'
