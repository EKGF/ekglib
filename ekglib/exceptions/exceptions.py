import sys


class Error(Exception):
    """Base class for other exceptions"""

    def __init__(self, message):
        self.message = message
        #
        # Don't use log_error here to avoid circular imports
        #
        print("\rERROR: {0}".format(message), file=sys.stderr)
        super().__init__(self.message)


class PrefixException(Error):
    pass


class CannotCapture(Error):
    pass


class PagingNotSupported(Error):
    pass
