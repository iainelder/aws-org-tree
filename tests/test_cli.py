from cli_test_helpers import shell


def test_runs_as_command() -> None:
    result = shell("aws-org-tree --help")
    assert result.exit_code == 0


def test_runs_as_module() -> None:
    result = shell("python -m aws_org_tree --help")
    assert result.exit_code == 0
