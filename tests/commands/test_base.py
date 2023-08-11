from pathlib import Path

from click.testing import CliRunner

from cg_lims.commands.base import cli


def test_cli_existing_log_file(config):
    # GIVEN existing log file path
    file_path = "some_file_path"
    file = Path(file_path)
    file.touch()

    # WHEN running cli base command
    runner = CliRunner()
    result = runner.invoke(cli, ["-c", config, "epps", "-l", file_path, "-p", "some_process_id"])
    file.unlink()

    # THEN assert no error
    assert result.exit_code == 0


def test_cli_not_existing_log_file(config):
    # GIVEN no existing file
    file_path = "no_file_path"

    # WHEN running cli base command
    runner = CliRunner()
    result = runner.invoke(cli, ["-c", config, "epps", "-l", file_path, "-p", "some_process_id"])

    # THEN assert no error
    assert result.exit_code == 0
