from importlib.metadata import version
from os import linesep

from cli_test_helpers import shell

def test_runs_as_command() -> None:
    result = shell("aws-org-tree --help")
    assert result.exit_code == 0


def test_runs_as_module() -> None:
    result = shell("python -m aws_org_tree --help")
    assert result.exit_code == 0


def test_version_option_is_present() -> None:
    expected_version = version("aws-org-tree")
    result = shell("aws-org-tree --version")
    assert result.exit_code == 0

def test_version_option_gives_version() -> None:
    expected_version = version("aws-org-tree")
    result = shell("aws-org-tree --version")
    assert result.stdout == f"{expected_version}{linesep}"
