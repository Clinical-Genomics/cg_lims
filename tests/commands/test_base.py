import pytest
from click import CliRunner
from commands.base import cli
from pathlib import Path

def test_cli_existing_log_file(existing_log_file_path: Path, process: str):
    #GIVEN existing file path
    
    # Ensure file path exists
    Path(existing_log_file).touch(exists_ok=True)
    
    # WHEN running command
    result = CliRunner.invoke(cli, args=[log, process])
    
    #THEN
    assert result.exit_code == 0
    
    
