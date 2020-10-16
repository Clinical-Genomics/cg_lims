
class LimsError(Exception):
    """Base Error"""
    def __init__(self, message):
        self.message = message

class QueueArtifactsError(LimsError):
    """Raise when failing to route artifacts."""
    pass

class DuplicateSampleError(LimsError):
    """Raise when you excpect one sample, but find more. 
    Eg: Two pools in a run contain the same sample."""
    pass

class MissingArtifactError(LimsError):
    """Raise when searching for artifacts that don't exist.
    Eg: Found no artifact for sample X in process Y."""
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

