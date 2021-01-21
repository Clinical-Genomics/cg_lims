from genologics.entities import Artifact, Process
from genologics.config import BASEURI
from genologics.lims import Lims
from typing import Optional
import pathlib
from cg_lims.exceptions import FileError
from pathlib import Path

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


def get_result_file(process:Process, file_path: Optional[str]=None, file_name: Optional[str]=None):
    """Reads file from args if present. Otherwise searches for file in outarts with
     name <file_name>"""

    if file_path and Path(file_path).is_file():
         file_path = file_path
    else:
        files = list(filter(lambda a: a.name in [file_name], process.all_outputs()))
        if len(files)>1:
            raise FileError(f'more than one file named {file_name}')
        else:
            file_path = files[0].files[0].content_location.split('scilifelab.se')[1]

    return file_path