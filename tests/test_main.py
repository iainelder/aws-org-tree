import re
from unittest.mock import patch

from boto3.session import Session
from botocore.client import BaseClient
from botocore.exceptions import ClientError
import pytest

from aws_org_tree.aws_org_tree import OrgTree

from typing import Any, Callable, Iterable
from types import SimpleNamespace
from moto import mock_organizations,  mock_sts

@pytest.fixture()
def session() -> Iterable[Session]:
    with mock_sts(), mock_organizations():
        yield Session(aws_access_key_id="None", aws_secret_access_key="None")


@pytest.fixture()
def new_organization(session: Session) -> None:
    session.client("organizations").create_organization(FeatureSet="ALL")


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
def test_raise_exception_when_org_not_in_use(session: Session) -> None:
    with pytest.raises(ClientError) as excinfo:
        OrgTree(session).build().to_dict()
    assert excinfo.value.response["Error"]["Code"] == "AWSOrganizationsNotInUseException"

@pytest.mark.usefixtures("new_organization")
def test_tree_has_root_when_org_is_new(session: Session) -> None:
    tree = OrgTree(session).build().to_dict()
    assert re.fullmatch(r"r-[a-z0-9]{4}", tree["name"])
