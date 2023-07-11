from importlib.metadata import version
from os import linesep

from cli_test_helpers import ArgvContext, shell
import pytest

from moto import mock_organizations, mock_sts

import aws_org_tree.aws_org_tree

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


@pytest.mark.xfail(
    raises=IndexError,
    reason="Moto doesn't behave like the real Organizations service.",
)
@mock_organizations()
@mock_sts()
def test_calls_main() -> None:
    with ArgvContext("aws-org-tree"), pytest.raises(SystemExit):
        aws_org_tree.aws_org_tree.main()
