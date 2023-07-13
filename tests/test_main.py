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


def service_error_factory(
    code: str, message: str="", status_code: int=400
) -> Callable[..., Any]:

    def respond_with_error(self: BaseClient, *args: Any, **kwargs: Any) -> Any:
        http_response = SimpleNamespace(status_code=status_code)
        parsed_response = {"Error": {"Message": message, "Code": code}}
        return http_response, parsed_response

    return respond_with_error


@patch(
    "botocore.client.BaseClient._make_request",
    service_error_factory("AWSOrganizationsNotInUseException"),
)
def test_not_in_use(session: Session) -> None:
    ot = OrgTree()
    with pytest.raises(ClientError) as excinfo:
        ot.build()
    assert excinfo.value.response["Error"]["Code"] == "AWSOrganizationsNotInUseException"
