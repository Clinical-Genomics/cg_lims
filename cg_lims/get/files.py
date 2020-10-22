from genologics.entities import Artifact
from genologics.config import BASEURI
from genologics.lims import Lims

import pathlib
from typing import List


def get_log_content(lims: Lims, file_id: str) -> str:
    """Searching for a log file Artifact with file_id. 
    
    If the artifact is found, returning its file content."""

    log_artifact = Artifact(lims, id=file_id)

    try:
        files = log_artifact.files
    except:
        files = None

    if files:
        server_adress = BASEURI.split(":")[1]
        file_path = files[0].content_location.split(server_adress)[1]
        log_file = pathlib.Path(file_path)
        log_file_content = log_file.read_text()
    else:
        log_file_content = ''

    return log_file_content
