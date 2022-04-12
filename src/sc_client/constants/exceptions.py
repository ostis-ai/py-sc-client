from enum import Enum


class CommonError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class InvalidValueError(CommonError):
    def __init__(self, msg: str = None):
        message = CommonErrorMessages.INVALID_VALUE.value
        if msg:
            message = ': '.join([message, msg])
        super().__init__(message)


class InvalidStateError(CommonError):
    def __init__(self, msg: str = None):
        message = CommonErrorMessages.INVALID_STATE.value
        if msg:
            message = ': '.join([message, msg])
        super().__init__(message)


class LinkContentOversizeError(CommonError):
    def __init__(self, msg: str = None):
        message = CommonErrorMessages.LINK_OVERSIZE.value
        if msg:
            message = ': '.join([message, msg])
        super().__init__(message)


class CommonErrorMessages(Enum):
    INVALID_STATE = "Invalid state"
    INVALID_VALUE = "Invalid value"
    MERGE_ERROR = "You can't merge two different syntax type"
    LINK_OVERSIZE = "Link content exceeds permissible value"
