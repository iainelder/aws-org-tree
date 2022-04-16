from boto3 import Session
import json
from typing import Final, Iterator
from pytest import fixture
from pytest_mock import MockerFixture
from moto.utilities.paginator import paginate
from moto import mock_organizations


ROOT_ID: Final = "r-0001"


@fixture(autouse=True)
def known_root_id(mocker: MockerFixture) -> None:

    mocker.patch(
        "moto.organizations.utils.make_random_root_id",
        lambda: ROOT_ID
    )


@fixture()
def session() -> Iterator[Session]:
    with mock_organizations():
        yield Session()


@fixture()
def paginated_moto(mocker: MockerFixture) -> Iterator[None]:

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
    def list_accounts_for_parent(self, **kwargs):
        parent_id = self.validate_parent_id(kwargs["ParentId"])
        return [
            account.describe()
            for account in self.accounts
            if account.parent_id == parent_id
        ]
    
    def response_list_accounts_for_parent(self):
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
        list_accounts_for_parent
    )
    mocker.patch(
        "moto.organizations.responses.OrganizationsResponse.list_accounts_for_parent",
        response_list_accounts_for_parent
    )


