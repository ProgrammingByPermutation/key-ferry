import recording.exceptions

ReadOnlyError = recording.exceptions.ReadOnlyError


class EventType:
    """
    The event type enumeration contain the constants to identify the type of event that was recorded.

    Attributes:
        MOUSE: A mouse event.
        KEYBOARD: A keyboard event.
    """
    MOUSE = 0
    KEYBOARD = 1
