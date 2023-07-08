import json
from typing import Any, Final, Iterator

from boto3 import Session
from moto import mock_organizations  # type: ignore[import]
from moto.utilities.paginator import paginate  # type: ignore[import]
from pytest import fixture
from pytest_mock import MockerFixture

ROOT_ID: Final = "r-0001"


@fixture(autouse=True)
def known_root_id(mocker: MockerFixture) -> None:

    mocker.patch("moto.organizations.utils.make_random_root_id", lambda: ROOT_ID)


@fixture()
def session() -> Iterator[Session]:
    with mock_organizations():
        yield Session()


@fixture()
def paginated_accounts(mocker: MockerFixture) -> None:

    model = {
        "list_accounts_for_parent": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 1,
            "result_key": "Accounts",
            "unique_attribute": "JoinedTimestamp",
        }
    }

    @paginate(pagination_model=model)
    def list_accounts_for_parent(self: Any, **kwargs: Any) -> Any:
        parent_id = self.validate_parent_id(kwargs["ParentId"])
        return [
            account.describe()
            for account in self.accounts
            if account.parent_id == parent_id
        ]

    def response_list_accounts_for_parent(self: Any) -> Any:
        max_results = self._get_int_param("MaxResults")
        next_token = self._get_param("NextToken")
        parent_id = self._get_param("ParentId")
        accounts, next_token = self.organizations_backend.list_accounts_for_parent(
            max_results=max_results, next_token=next_token, ParentId=parent_id
        )
        response = {"Accounts": accounts}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    mocker.patch("moto.organizations.utils.PAGINATION_MODEL", model)

    # The mock name must match the key in the pagination model.
    mocker.patch(
        "moto.organizations.models.OrganizationsBackend.list_accounts_for_parent",
        list_accounts_for_parent,
    )
    mocker.patch(
        "moto.organizations.responses.OrganizationsResponse.list_accounts_for_parent",
        response_list_accounts_for_parent,
    )


@fixture()
def paginated_units(mocker: MockerFixture) -> None:

    model = {
        "list_organizational_units_for_parent": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 1,
            "result_key": "OrganizationalUnits",
            "unique_attribute": "Id",
        }
    }

    @paginate(pagination_model=model)
    def list_organizational_units_for_parent(self: Any, **kwargs: Any) -> Any:
        parent_id = self.validate_parent_id(kwargs["ParentId"])
        return [
            {"Id": ou.id, "Arn": ou.arn, "Name": ou.name}
            for ou in self.ou
            if ou.parent_id == parent_id
        ]

    def response_list_organizational_units_for_parent(self: Any) -> Any:
        max_results = self._get_int_param("MaxResults")
        next_token = self._get_param("NextToken")
        parent_id = self._get_param("ParentId")
        (
            units,
            next_token,
        ) = self.organizations_backend.list_organizational_units_for_parent(
            max_results=max_results, next_token=next_token, ParentId=parent_id
        )
        response = {"OrganizationalUnits": units}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    mocker.patch.dict("moto.organizations.utils.PAGINATION_MODEL", model)

    # The mock name must match the key in the pagination model.
    mocker.patch(
        "moto.organizations.models.OrganizationsBackend.list_organizational_units_for_parent",
        list_organizational_units_for_parent,
    )
    mocker.patch(
        "moto.organizations.responses.OrganizationsResponse.list_organizational_units_for_parent",
        response_list_organizational_units_for_parent,
    )
