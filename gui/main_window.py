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
        # self.record_button.pack(side="left")
        # self.play_button.pack(side="left")

    def show(self):
        """
        Shows the window.
        """
        self.window.mainloop()
