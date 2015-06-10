import tkinter
import tkinter.messagebox
import tkinter.filedialog

import recording.recorder as recorder
import recording.constants as constants

EventType = constants.EventType


class GlobalInfo:
    def __init__(self):
        self.recording = False
        self.button = None
        self.rec = None


def reply(args):
    args.recording = not args.recording

    if args.recording:
        args.rec.start()
        text = 'Stop Recording'
    else:
        args.rec.stop()
        file = tkinter.filedialog.asksaveasfile(mode='w', defaultextension=".py")
        if file is not None:
            write_to_file(file)
        text = 'Record'
    args.recording = args.recording
    args.button['text'] = text


def write_to_file(file):
    pass

# TODO: tkinter and pyhook are not getting along...time for some interprocess communication: http://pymotw.com/2/multiprocessing/communication.html

global_info = GlobalInfo()
global_info.rec = recorder.WindowsRecorder()
global_info.recording = False
window = tkinter.Tk()
global_info.button = tkinter.Button(window, text='Record', command=lambda: reply(global_info))
global_info.button.pack()
window.mainloop()

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
