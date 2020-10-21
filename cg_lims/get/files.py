from genologics.entities import Process, Artifact, Sample
from genologics.config import BASEURI
from genologics.lims import Lims

from operator import attrgetter
import sys
import pathlib
from typing import List


def get_log_content(lims: Lims, file_id: str) -> str:
    """Searching for a log Artifact with file_id. 
    
    If the artifact is found, returning the the file content."""

    log_artifact = Artifact(lims, id=file_id)

    try:
        files = log_artifact.files
    except:
        files = None

    if files:
        server_adress = BASEURI.split(":")[1]
        file_path = files[0].content_location.split(server_adress)[1]
        old_log = pathlib.Path(file_path)
        old_log_content = old_log.read_text()
    else:
        old_log_content = ''

    return old_log_content
