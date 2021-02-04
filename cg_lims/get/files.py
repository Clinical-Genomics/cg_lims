import pathlib
from pathlib import Path
from typing import Optional

from genologics.config import BASEURI
from genologics.entities import Artifact, Process
from genologics.lims import Lims

from cg_lims.exceptions import FileError


def get_log_content(lims: Lims, file_id: str) -> str:
    """Searching for a log file Artifact with file_id.

    If the artifact is found, returning its file content."""

    log_artifact = Artifact(lims, id=file_id)
    file_path = get_file_path(log_artifact)

    if file_path:
        log_file = pathlib.Path(file_path)
        log_file_content = log_file.read_text()
    else:
        log_file_content = ""

    return log_file_content


def get_file_path(file_artifact: Artifact) -> Optional[str]:
    """getting the file path from a artifacts content location"""

    try:
        files = file_artifact.files
    except:
        files = None

    if files:
        server_adress = BASEURI.split(":")[1]
        file_path = files[0].content_location.split(server_adress)[1]
        return file_path
    else:
        return None
