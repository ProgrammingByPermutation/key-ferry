from __future__ import print_function

import datetime
import os
import win32process

import recording.exceptions as exceptions
import utilities.listeners as listeners

ArgumentError = exceptions.ArgumentError


class WindowsRecorder:
    """
    Hooks onto Windows keyboard and mouse events, storing a list of recorded events.
    """
    # Left Shift, Right Shift, Left Control, Right Control, Left Alt, Right Alt
    __HOLDABLE_KEYS = [160, 161, 162, 163, 164, 165]
    __CTRL_KEYS = [162, 163]
    __ALT_KEYS = [164, 165]
    __SHIFT_KEYS = [160, 161]
    __DEL = 46

    def __init__(self, events_collection, process_to_ignore):
        """
        Initializes a new instance of the WindowsRecorder class.
        :param events_collection: The list of events that have been recorded.
        :param process_to_ignore: If not set to None, the process that should be ignored when recording.
        """
        self.__listener = listeners.WindowsListener()
        self.__keys_held_down = []
        self.__recording_callbacks = []
        self.__process_to_ignore = process_to_ignore
        self.__shift_is_held = False
        self.__ctrl_is_held = False
        self.__alt_is_held = False

        if events_collection is not None:
            self.events_collection = events_collection
            self.__recording_callbacks.append(lambda event: self.events_collection.append(event))

        self.__time_since_last_command = datetime.datetime.now()

    def on_mouse_event(self, event):
        """
        Handles recording mouse events.
        :param event: The event that occurred.
        """
        # If this message is about something happening in our process, skip it
        if self.__process_to_ignore is not None:
            _, events_pid = win32process.GetWindowThreadProcessId(event.Window)
            if events_pid == os.getpid():
                return

        # Record the event
        self.__record_event(event)

    def on_keyboard_event(self, event):
        """
        Routes keyboard events.
        :param event: The event to route.
        """
        if event.Is_Down:
            self.on_key_down_event(event)
        else:
            self.on_key_up_event(event)

    def on_key_up_event(self, event):
        """
        Handles recording key up events. Only a subset of key up events are recorded.
        :param event: The event that occurred.
        """
        current_held_key = [key for key in self.__keys_held_down if key.KeyID == event.KeyID]

        if len(current_held_key) != 0:
            self.__keys_held_down.remove(current_held_key[0])
            self.__set_held_keys()
            self.__record_event(event)

    def on_key_down_event(self, event):
        """
        Handles recording key down events. Almost all keyboard recording is in the from of key down presses.
        :param event: The event that occurred.
        """
        # If it's a holdable key then wait for the key up
        if event.KeyID in WindowsRecorder.__HOLDABLE_KEYS:
            # If we already recorded this key, don't re-add it to the collection
            if any(key.KeyID == event.KeyID for key in self.__keys_held_down):
                return
            self.__keys_held_down.append(event)
            self.__set_held_keys()
            return

        # If this is delete, make sure they aren't holding CTRL + ALT. If they are then windows already stole focus
        # and choked our release keys. We need to record them ourselves so we don't get into a state.
        if event.KeyID == self.__DEL:
            ctrl_intersection = [event for event in self.__keys_held_down if event.KeyID in self.__CTRL_KEYS]
            alt_intersection = [event for event in self.__keys_held_down if event.KeyID in self.__ALT_KEYS]
            if len(ctrl_intersection) > 0 and len(alt_intersection) > 0:
                self.__ctrl_is_held = False
                self.__alt_is_held = False
            return

        # Record the event
        self.__record_event(event)

    def __set_held_keys(self):
        """
        Sets variables indicating if a modifier key is being held down.
        """
        keys_held = {key.KeyID for key in self.__keys_held_down}
        self.__alt_is_held = len(set(self.__ALT_KEYS) & keys_held) > 0
        self.__ctrl_is_held = len(set(self.__CTRL_KEYS) & keys_held) > 0
        self.__shift_is_held = len(set(self.__SHIFT_KEYS) & keys_held) > 0

    def __record_event(self, event):
        """
        Record the passed in event.
        :param event: The event to record.
        """
        # Set the time, must be done first since we're using the ill advised datetime.now call.
        # TODO: Learn more about the time since epoch. When exactly is epoch relative to?
        curr_time = datetime.datetime.now()
        event.Time = (curr_time - self.__time_since_last_command).total_seconds()
        self.__time_since_last_command = curr_time
        event.Is_Shift = self.__shift_is_held
        event.Is_Ctrl = self.__ctrl_is_held
        event.Is_Alt = self.__alt_is_held

        # Add to the events lists
        for func in self.__recording_callbacks:
            func(event)

    def start(self):
        """
        Starts recording keyboard and mouse events.
        """
        self.__listener.add_listener(self)

    def stop(self):
        """
        Stops recording keyboard and mouse events.
        """
        self.__listener.remove_listener(self)

    def release(self):
        """
        Releases the resources used by the current instance of the class.
        """
        if self.__listener is not None:
            self.stop()
            self.__listener = None

        if self.__time_since_last_command is not None:
            self.__time_since_last_command = None

        if self.__keys_held_down is not None:
            self.__keys_held_down.clear()
            self.__keys_held_down = None
