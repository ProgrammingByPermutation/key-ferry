import recording.recorder as recorder
import time

test = recorder.WindowsRecorder()

while True:
    time.sleep(3)
    [print(x) for x in test.events]

# import win32api
# win32api.keybd_event(100, 0, 0, 0)
