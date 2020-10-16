from genologics.entities import Process, Artifact, Sample
from genologics.config import BASEURI
from genologics.lims import Lims

from operator import attrgetter
import sys
import pathlib
from typing import List


def get_lims_log_file(lims: Lims, file_id: str) -> pathlib.Path:
    """Searching for a log Artifact with file_id. 
    
    If the artifact is found, returning the path to the attached file. 
    Otherwise returning the file_id."""

    log_artifact = Artifact(lims, id=file_id)

    try:
        files = log_artifact.files
    except:
        files = None

    if files:
        file.chmod(0o775)
        server_adress = BASEURI.split(":")[1]
        file_path = files[0].content_location.split(server_adress)[1]
        file = pathlib.Path(file_path)
    else:
        file = pathlib.Path(file_id)

    return file
