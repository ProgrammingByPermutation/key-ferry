import os

import recording.recorder as recorder
import recording.constants as constants
import playback.playback as playback

EventType = constants.EventType

while True:
    rec = recorder.WindowsRecorder()
    os.system('notepad')
    rec.disconnect()

    print('Number of events: ' + str(len(rec.events)))

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
    rec.release()
    play.release()

    # TODO: Make WindowsRecorder a singleton, bad things are happening when more than one of them are alive
    # TODO: Fix special keys (shift, alt, ctrl) they're currently state swapping permanently
