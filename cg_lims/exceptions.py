from typing import Optional

from starlette import status


class LimsError(Exception):
    """Base Error"""

    def __init__(self, message):
        self.message = message


class AtlasResponseFailedError(LimsError):
    """Raise when failing retrieve atlas response."""



class ArgumentError(LimsError):
    """Raise when failing retrieve atlas response."""



class QueueArtifactsError(LimsError):
    """Raise when failing to route artifacts."""



class MissingFileError(LimsError):
    pass


class DuplicateSampleError(LimsError):
    """Raise when you excpect one sample, but find more.
    Eg: Two pools in a run contain the same sample."""



class MissingArtifactError(LimsError):
    """Raise when searching for artifacts that don't exist.
    Eg: Found no artifact for sample X in process Y."""



class MissingProcessError(LimsError):
    """Raise when searching for process that don't exist.."""



class MissingSampleError(LimsError):
    """Raise when searching for samples that don't exist."""



class MissingUDFsError(LimsError):
    """Raise when searching for udfs that don't exist.
    Eg: Found no udf X on artifact Y."""



class ZeroReadsError(LimsError):
    """Raise when read count is unexpectedly zero."""



class LowAmountError(LimsError):
    """Raise when amount is low."""



class FailingQCError(LimsError):
    """Raise when qc fails"""



class MissingCgFieldError(LimsError):
    """Raise when field missing"""



class FileError(LimsError):
    """Raise when error with file"""



class MissingValueError(LimsError):
    """Raise when value missing"""



class InvalidValueError(LimsError):
    """Raise when a value is invalid"""



class CSVColumnError(LimsError):
    """Raise when handling errors with csv columns"""



class InsertError(LimsError):
    def __init__(self, message: str, code: Optional[int] = status.HTTP_405_METHOD_NOT_ALLOWED):
        self.message = message
        self.code = code
        super().__init__(message)


class HighConcentrationError(LimsError):
    """Raise when a value is invalid"""

