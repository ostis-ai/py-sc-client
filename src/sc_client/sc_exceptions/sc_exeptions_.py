import abc

from sc_client.sc_exceptions.messages import ErrorDefaultMessages


class ScException(Exception, abc.ABC):
    default_message: str

    def __init__(self, note: str = None, *note_args) -> None:
        # pylint: disable=keyword-arg-before-vararg
        super().__init__(self.default_message if not note else f"{self.default_message}: {note.format(*note_args)}")


class ScServerError(ScException):
    default_message = ErrorDefaultMessages.SC_SERVER_ERROR


class PayloadMaxSizeError(ScServerError):
    default_message = ErrorDefaultMessages.PAYLOAD_MAX_SIZE


class ScEventError(ScServerError):
    default_message = ErrorDefaultMessages.EVENT_ERROR


class InvalidValueError(ScException):
    default_message = ErrorDefaultMessages.INVALID_VALUE


class InvalidTypeError(ScException):
    default_message = ErrorDefaultMessages.INVALID_TYPE


class LinkContentOversizeError(ScException):
    default_message = ErrorDefaultMessages.LINK_OVERSIZE
