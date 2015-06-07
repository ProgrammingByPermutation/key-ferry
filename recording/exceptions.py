class ReadOnlyError(RuntimeError):
    """
    Exception to indicate that a readonly value was modified.
    """
    pass


class ArgumentError(RuntimeError):
    """
    Exception to indicate that the incorrect arguments were passed in.
    """
    pass
