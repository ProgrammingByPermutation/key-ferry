import os

import recording.recorder as recorder
import recording.constants as constants
import playback.playback as playback

EventType = constants.EventType

rec = recorder.WindowsRecorder()
while True:
    rec.start()
    os.system('notepad')
    rec.stop()

    print('Number of events: ' + str(len(rec.events)))
    print('Helds: ', end="")
    print(rec._WindowsRecorder__keys_held_down)

    # print('-' * 80)
    # for x in rec.events:
    #     if x.Type == EventType.MOUSE:
    #         print('Mouse: ' + str(x.Position) + ' Relative Time: ' + str(x.Time))
    #     elif x.Type == EventType.KEYBOARD:
    #         print('Keyboard: ' + str(x.KeyID) + ' Relative Time: ' + str(x.Time))
    #     else:
    #         print('Error with event' + x)

    play = playback.WindowsPlaybackManager(rec.events)
    play.start()
    os.system('notepad')
    play.stop()
    play.release()
    rec.events.clear()

    # TODO: Combine keyboard events together to save space
    # TODO: Fix special keys (shift, alt, ctrl) they're currently state swapping permanently

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
