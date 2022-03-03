from typing import Optional

from starlette import status


class LimsError(Exception):
    """Base Error"""

    def __init__(self, message):
        self.message = message


class AtlasResponseFailedError(LimsError):
    """Raise when failing retrieve atlas response."""

    pass


class ArgumentError(LimsError):
    """Raise when failing retrieve atlas response."""

    pass


class QueueArtifactsError(LimsError):
    """Raise when failing to route artifacts."""

    pass


class MissingFileError(LimsError):
    pass


class DuplicateSampleError(LimsError):
    """Raise when you excpect one sample, but find more.
    Eg: Two pools in a run contain the same sample."""

    pass


class MissingArtifactError(LimsError):
    """Raise when searching for artifacts that don't exist.
    Eg: Found no artifact for sample X in process Y."""

    pass


class MissingProcessError(LimsError):
    """Raise when searching for process that don't exist.."""

    pass


class MissingSampleError(LimsError):
    """Raise when searching for samples that don't exist."""

    pass


class MissingUDFsError(LimsError):
    """Raise when searching for udfs that don't exist.
    Eg: Found no udf X on artifact Y."""

    pass


class ZeroReadsError(LimsError):
    """Raise when read count is unexpectedly zero."""

    pass


class LowAmountError(LimsError):
    """Raise when amount is low."""

    pass


class FailingQCError(LimsError):
    """Raise when qc fails"""

    pass


class MissingCgFieldError(LimsError):
    """Raise when field missing"""

    pass


class FileError(LimsError):
    """Raise when error with file"""

    pass


class MissingValueError(LimsError):
    """Raise when value missing"""

    pass


class InvalidValueError(LimsError):
    """Raise when a value is invalid"""

    pass


class CSVColumnError(LimsError):
    """Raise when handling errors with csv columns"""

    pass


class InsertError(LimsError):
    def __init__(self, message: str, code: Optional[int] = status.HTTP_405_METHOD_NOT_ALLOWED):
        self.message = message
        self.code = code
        super().__init__(message)


class HighConcentrationError(LimsError):
    """Raise when a value is invalid"""

    pass
