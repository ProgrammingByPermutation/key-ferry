import tkinter
import tkinter.messagebox
import tkinter.filedialog
import os

import recording.constants as constants

EventType = constants.EventType


class MainWindow:
    def __init__(self):
        """
        Creates the window and its controls.
        """
        self.window = tkinter.Tk()
        self.window.title("Key Ferry")

        # TODO: If the frozen binary is executed from any working directory other than the one that key_ferry.py is
        # currently located in, this call fails.
        if os.path.isfile('keyboard-space.ico'):
            self.window.iconbitmap('keyboard-space.ico')

        # Variables
        self.should_ignore_own_window = tkinter.IntVar(value=1)

        # GUI Elements
        self.record_button = tkinter.Button(self.window, text='Record')
        self.play_button = tkinter.Button(self.window, text='Play File')
        self.recording_options_group = tkinter.LabelFrame(self.window, text="Recording Options", padx=5, pady=5)
        self.recording_options_record_own_window_checkbutton = tkinter.Checkbutton(self.recording_options_group,
                                                                                   text="Ignore this Process",
                                                                                   variable=self.should_ignore_own_window)
        self.record_button.grid(column="0", row="0", padx="15")
        self.play_button.grid(column="1", row="0", padx="15")
        self.recording_options_group.grid(column="0", row="1", columnspan="2")
        self.recording_options_record_own_window_checkbutton.grid(column="0", row="0")

    def show(self):
        """
        Shows the window.
        """
        self.window.mainloop()

    def on_playback_started(self):
        """
        Handles logic related to the playback of a file starting.
        """
        self.record_button.config(state=tkinter.DISABLED)
        self.play_button.config(text='Stop Playback')

    def on_playback_ended(self):
        """
        Handles logic related to the playback of a file ending.
        """
        self.record_button.config(state=tkinter.NORMAL)
        self.play_button.config(text='Play File')

    def on_record_started(self):
        """
        Handles logic related to the playback of a file starting.
        """
        self.play_button.config(state=tkinter.DISABLED)
        self.recording_options_record_own_window_checkbutton.config(state=tkinter.DISABLED)
        self.record_button.config(text='Stop Recording')

    def on_record_ended(self):
        """
        Handles logic related to the playback of a file ending.
        """
        self.play_button.config(state=tkinter.NORMAL)
        self.recording_options_record_own_window_checkbutton.config(state=tkinter.NORMAL)
        self.record_button.config(text='Record')
