from typing import cast, Iterator, Final
from boto3 import Session
from moto import mock_organizations, mock_sts, organizations
from pytest import fixture
from aws_org_graph import build_org_graph
import networkx as nx
from pytest_mock import MockerFixture
from mypy_boto3_organizations.type_defs import AccountTypeDef
from mypy_boto3_organizations.type_defs import OrganizationalUnitTypeDef


def _create_org(session: Session) -> None:
    org = session.client("organizations")
    org.create_organization(FeatureSet="ALL")


def _add_member_account(session: Session) -> AccountTypeDef:
    org = session.client("organizations")
    resp = org.create_account(Email="account@example.com", AccountName="Example")
    new_account_id = resp["CreateAccountStatus"]["AccountId"]
    member = org.describe_account(AccountId=new_account_id)["Account"]
    return member


def _add_unit(session: Session, parent_id: str) -> OrganizationalUnitTypeDef:
    org = session.client("organizations")
    resp = org.create_organizational_unit(ParentId=parent_id, Name="Example")
    unit = cast(OrganizationalUnitTypeDef, resp["OrganizationalUnit"])
    return unit


ROOT_ID: Final = "r-0001"
MANAGEMENT_ACCOUNT_ID: Final = organizations.utils.MASTER_ACCOUNT_ID

def draw(g: nx.Graph):
    """Draw the graph in the Pytest debugger."""
    import matplotlib.pyplot as plt
    nx.draw(g, with_labels=True)
    plt.show()


@fixture
def session(mocker: MockerFixture) -> Iterator[Session]:

    mocker.patch(
        "moto.organizations.utils.make_random_root_id",
        lambda: ROOT_ID
    )

    with mock_sts(), mock_organizations():
        yield Session()


def test_when_no_org_exists_returns_empty_graph(session: Session):
    g = build_org_graph(session)
    assert len(g) == 0


class Test_when_org_is_new:

    @fixture(autouse=True)
    def org(self, session: Session) -> None:
        _create_org(session)

    def test_graph_has_root(self, session: Session):
        g = build_org_graph(session)
        assert ROOT_ID in g

    def test_graph_has_management_account(self, session: Session):
        g = build_org_graph(session)
        assert MANAGEMENT_ACCOUNT_ID in g

    def test_graph_has_edge_between_root_and_management_account(self, session: Session):
        g = build_org_graph(session)
        assert (ROOT_ID, MANAGEMENT_ACCOUNT_ID) in g.edges


class Test_when_org_has_one_member:

    member: AccountTypeDef

    @fixture(autouse=True)
    def org(self, session: Session) -> None:
        _create_org(session)
        self.member = _add_member_account(session)

    def test_graph_contains_member(self, session: Session):
        g = build_org_graph(session)
        assert self.member["Id"] in g

    def test_graph_has_edge_from_member_to_root(self, session: Session):
        g = build_org_graph(session)
        assert (ROOT_ID, self.member["Id"]) in g.edges


class Test_when_org_has_empty_unit:

    unit: OrganizationalUnitTypeDef

    @fixture(autouse=True)
    def org(self, session: Session) -> None:
        _create_org(session)
        self.unit = _add_unit(session, parent_id=ROOT_ID)

    def test_graph_contains_unit(self, session: Session):
        g = build_org_graph(session)
        assert self.unit["Id"] in g

    def test_graph_has_edge_from_unit_to_root(self, session: Session):
        g = build_org_graph(session)
        assert (ROOT_ID, self.unit["Id"]) in g.edges
