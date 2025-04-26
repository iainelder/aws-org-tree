# aws-org-tree

Prints a text tree representation of an AWS organization.

```bash
aws-org-tree
```

```text
Root (r-p74l)
├── isme-root-zcskbx (039444814027)
├── Sandbox (ou-p74l-a2llanp8)
└── Security (ou-p74l-094nw8v7)
    ├── Log Archive (386884128156)
    └── Audit (466721047587)
```

## Installation


Prerequisite: Python 3.12 at least.

Recommended: [uv](https://docs.astral.sh/uv/), which installs the tool in an islated virtualenv and is faster than pipx. (You can also use it to install Python 3.12. Not shown here.)

```bash
uv tool --python 3.12 aws-org-tree
```

Recommended: [pipx](https://pipxproject.github.io/pipx/), which installs the tool in an isolated virtualenv while linking the script you need.

Install using [pipx](https://pipxproject.github.io/pipx/) (recommended because it uses an isolated virtualenv to avoid dependency conflicts with other Python things you may have).

```bash
pipx install aws-org-tree
```

Or install using pip.

```bash
pip install --user aws-org-tree
```

Learn to use it.

```bash
aws-org-tree --help
```

## Development

Install Python 3.12.

Install [Poetry](https://python-poetry.org/) via [Pipx](https://pypa.github.io/pipx/).

Clone the repo.

Run `poetry install`.

Hack away.

Run quality checks with `poetry run pre-commit run --all-files`.

Install quality checks as [pre-commit checks](https://pre-commit.com/) with `poetry run pre-commit install`.

Read the [testing README](/tests/README.md).

## Continuous integration and deployment

Push to any branch to run the tests on every commit via GitHub Actions.

Push an annotated tag of the form `x.y.z` (semantic version) to publish a GitHub release and publish the package distributions to PyPI if the tests pass. It may work on any branch but please only do it on the main branch.
