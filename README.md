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

Use the `--node-name-format` option to print different properties of the resources. This part doesn't work well yet because different resources have different properties. If the property is missing the property name is used as a placeholder.

```bash
poetry run aws-org-tree --node-name-format "{Type} {Email}"
```

```text
ROOT Email
├── ACCOUNT iain+awsroot+zcskbx@isme.es
├── ORGANIZATIONAL_UNIT Email
└── ORGANIZATIONAL_UNIT Email
    ├── ACCOUNT iain+awsroot+zcskbx+log-archive@isme.es
    └── ACCOUNT iain+awsroot+zcskbx+audit@isme.es
```

## Installation


Prerequisite: Python 3.8 at least.

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

## Other output formats

I removed the JSON tree (`json-tree`) and flat JSON formats (`json-flat`) formats Use [version `0.2.0`](https://github.com/iainelder/aws-org-tree/tree/0.2.0) if you need those.

## Development

Install Python 3.8.

Install [Poetry](https://python-poetry.org/) via [Pipx](https://pypa.github.io/pipx/).

Clone the repo.

Run `poetry install`.

Hack away.

Run quality checks with `poetry run pre-commit run --all-files`.

Install quality checks as [pre-commit checks](https://pre-commit.com/) with `poetry run pre-commit install`.

Read the [testing README](/tests/README.md).

## Continuous integration and deployment

Push to the main branch to run the tests on every commit via GitHub Actions.

Push an annotated tag of the form `x.y.z` (semantic version) to publish a GitHub release and publish the package distributions to PyPI if the tests pass.
