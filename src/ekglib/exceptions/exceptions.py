class Error(Exception):
    """Base class for other exceptions"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class PrefixException(Error):
    pass


class CannotCapture(Error):
    pass


class PagingNotSupported(Error):
    pass
