
class LimsError(Exception):
    def __init__(self, message):
        self.message = message

class QueueArtifactsError(LimsError):
    pass

class DuplicateSampleError(LimsError):
    pass

class MissingArtifactError(LimsError):
    pass

class WhatToCallThisError(LimsError):
    pass


