from io import StringIO
from typing import Any, Dict, List
from unittest.mock import Mock, patch

import pytest
from cli_test_helpers import ArgvContext, shell  # type: ignore[import]


def test_cli_runs_as_command() -> None:
    result = shell("aws-org-tree --help")
    assert result.exit_code == 0


def test_cli_runs_as_module() -> None:
    result = shell("python -m aws_org_tree --help")
    assert result.exit_code == 0
