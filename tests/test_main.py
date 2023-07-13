from unittest.mock import patch

from boto3.session import Session
from botocore.client import BaseClient
from botocore.exceptions import ClientError
import pytest

from aws_org_tree.aws_org_tree import OrgTree

from typing import Any, Callable, Iterable
from types import SimpleNamespace


@pytest.fixture()
def session() -> Iterable[Session]:
    yield Session(aws_access_key_id="None", aws_secret_access_key="None")


def service_error_factory(code: str, message: str="") -> Callable[..., Any]:

    # Don't know what type operation_model should be. Check botocove-stubs.
    def _raise(self: BaseClient, operation_model, *args, **kwargs) -> Any:  # type: ignore[no-untyped-def]
        http_response = SimpleNamespace(status_code=400)
        parsed_response = {"Error": {"Message": message, "Code": code}}
        return http_response, parsed_response

    return _raise


@patch(
    "botocore.client.BaseClient._make_request",
    service_error_factory("AWSOrganizationsNotInUseException"),
)
def test_not_in_use(session: Session) -> None:
    ot = OrgTree()
    with pytest.raises(ClientError) as excinfo:
        ot.build()
    assert excinfo.value.response["Error"]["Code"] == "AWSOrganizationsNotInUseException"


# Why not just use Moto? Because its Organizations implementation is incomplete. I can't use it to test the edge cases.

# Stubber gives me control of the edge cases but is inflexible. It forces an expected order of API operations on the implementation. There are many ways to describe an organization. I don't want to constrain the implementation, but I do know the output for a given organizational state.

# A long-term solution is to improve Moto's Organizations backend. Until then, I can maybe just patch the boto3 method. See link below for example.

# Use Snyk to search for use of Stubber. GitHub's own search for this is dire.
# https://snyk.io/advisor/python/botocore/functions/botocore.stub.Stubber

# Chalice uses Stubber as of 2023-07-13. Read the docs on testing and contributing for examples.
# https://github.com/aws/chalice/blob/79838b02dc330cfe549823899d2662ded0538015/docs/source/topics/testing.rst
# https://github.com/aws/chalice/blob/79838b02dc330cfe549823899d2662ded0538015/CONTRIBUTING.rst

# Cloudformation CLI used Stubber until 2019. It's unclear what it was replaced with.
# https://github.com/aws-cloudformation/cloudformation-cli/pull/217/
# 9711e4bc888c2254b441d42ea45d18671e39605a

# More uses of Stubber:
#
# * https://github.com/onicagroup/runway/blob/b60cc535e2eaa2a55a5c89c18cefd0662244967f/tests/cfngin/test_context.py#L406
# * https://github.com/mozilla/telemetry-analysis-service/blob/b4b0c8dab3ff9a11648eeb177952b64ecfe2ded4/tests/jobs/test_provisioners.py#L168
# * https://github.com/aws/aws-secretsmanager-caching-python/blob/46e1b585b089fc1a857a649031d3bb2cf4abeb3c/test/unit/test_decorators.py#L29
# * https://github.com/boto/botocore/blob/c2f18c15ca601d5cfdd6767535a96de9b13f1543/tests/unit/test_client.py#L1494
# * https://github.com/awslabs/aws-sam-cli/blob/4f2c345c5e415ec443cb55b82dd7cbb7b0ba2ad6/tests/unit/lib/bootstrap/test_bootstrap.py#L17
# * https://github.com/boto/botocore/blob/c2f18c15ca601d5cfdd6767535a96de9b13f1543/tests/unit/test_client.py#L1452
# * https://github.com/mozilla-iam/cis/blob/8d782ed7f6c96125df2d5a4033ad2027c9f4b5e5/python-modules/cis_identity_vault/cis_identity_vault/vault.py#L41

# Comparison of Moto, Stubber, and PySpark.
# https://github.com/paramraghavan/python-pytest

# Comparison of Moto, Stubber, and LocalStack.
# https://www.sanjaysiddhanti.com/2020/04/08/s3testing/

# An article showing how to use the Python package to record an AWS API conversation.
# Like VCR for Ruby and Python.
# https://xebia.com/blog/how-to-create-python-unit-tests-for-aws-using-the-botocore-stubber/
# https://pypi.org/project/botocore-stubber-recorder/
# https://github.com/binxio/botocore-stubber-recorder

# Example to patch _make_api_call
# https://stackoverflow.com/questions/37143597/mocking-boto3-s3-client-method-python
