"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at http://opensource.org/licenses/MIT)
"""

from enum import Enum


class CommonError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class InvalidValueError(CommonError):
    def __init__(self, msg: str = None):
        message = CommonErrorMessages.INVALID_VALUE.value
        if msg:
            message = ": ".join([message, msg])
        super().__init__(message)


class InvalidTypeError(CommonError):
    def __init__(self, msg: str = None):
        message = CommonErrorMessages.INVALID_TYPE.value
        if msg:
            message = ": ".join([message, msg])
        super().__init__(message)


class InvalidStateError(CommonError):
    def __init__(self, msg: str = None):
        message = CommonErrorMessages.INVALID_STATE.value
        if msg:
            message = ": ".join([message, msg])
        super().__init__(message)


class LinkContentOversizeError(CommonError):
    def __init__(self, msg: str = None):
        message = CommonErrorMessages.LINK_OVERSIZE.value
        if msg:
            message = ": ".join([message, msg])
        super().__init__(message)


class CommonErrorMessages(Enum):
    INVALID_STATE = "Invalid state"
    INVALID_VALUE = "Invalid value"
    INVALID_TYPE = "Invalid type"
    MERGE_ERROR = "You can't merge two different syntax types"
    LINK_OVERSIZE = "Link content exceeds permitted value"
