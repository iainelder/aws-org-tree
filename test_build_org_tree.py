from typing import List

import matplotlib.pyplot as plt  # type: ignore[import]
import networkx as nx  # type: ignore[import]
from boto3 import Session
from moto.organizations.utils import MASTER_ACCOUNT_ID  # type: ignore[import]
from mypy_boto3_organizations.type_defs import AccountTypeDef, OrganizationalUnitTypeDef
from pytest import fixture, mark

from aws_org_graph import build_org_graph
from conftest import ROOT_ID


def _create_org(session: Session) -> None:
    org = session.client("organizations")
    org.create_organization(FeatureSet="ALL")


def _create_member(session: Session, parent_id: str) -> AccountTypeDef:
    org = session.client("organizations")
    resp = org.create_account(Email="account@example.com", AccountName="Example")
    new_account_id = resp["CreateAccountStatus"]["AccountId"]
    member = org.describe_account(AccountId=new_account_id)["Account"]
    org.move_account(
        AccountId=member["Id"], SourceParentId=ROOT_ID, DestinationParentId=parent_id
    )
    return member


def _create_unit(session: Session, parent_id: str) -> OrganizationalUnitTypeDef:
    org = session.client("organizations")
    resp = org.create_organizational_unit(ParentId=parent_id, Name="Example")
    return resp["OrganizationalUnit"]


def draw(g: nx.Graph) -> None:
    """Draw the graph in the Pytest debugger."""
    nx.draw(g, with_labels=True)
    plt.show()


@mark.usefixtures("paginated_accounts", "paginated_units")
class Postconditions:
    def test_graph_is_frozen(self, session: Session) -> None:
        g = build_org_graph(session)
        assert nx.is_frozen(g)


class NonEmptyPostconditions(Postconditions):
    @mark.usefixtures("known_root_id")
    def test_graph_has_root(self, session: Session) -> None:
        g = build_org_graph(session)
        assert ROOT_ID in g

    def test_graph_has_management_account(self, session: Session) -> None:
        g = build_org_graph(session)
        assert MASTER_ACCOUNT_ID in g


class Test_when_no_org_exists(Postconditions):
    def test_graph_is_empty(self, session: Session) -> None:
        g = build_org_graph(session)
        assert len(g) == 0


class Test_when_org_is_new(NonEmptyPostconditions):
    @fixture(autouse=True)
    def org(self, session: Session) -> None:
        _create_org(session)

    def test_graph_has_edge_between_root_and_management_account(
        self, session: Session
    ) -> None:
        g = build_org_graph(session)
        assert (ROOT_ID, MASTER_ACCOUNT_ID) in g.edges


class Test_when_org_has_one_member(NonEmptyPostconditions):

    member: AccountTypeDef

    @fixture(autouse=True)
    def org(self, session: Session) -> None:
        _create_org(session)
        self.member = _create_member(session, parent_id=ROOT_ID)

    def test_graph_contains_member(self, session: Session) -> None:
        g = build_org_graph(session)
        assert self.member["Id"] in g

    def test_graph_has_edge_from_member_to_root(self, session: Session) -> None:
        g = build_org_graph(session)
        assert (ROOT_ID, self.member["Id"]) in g.edges


class Test_when_org_has_empty_unit(NonEmptyPostconditions):

    unit: OrganizationalUnitTypeDef

    @fixture(autouse=True)
    def org(self, session: Session) -> None:
        _create_org(session)
        self.unit = _create_unit(session, parent_id=ROOT_ID)

    def test_graph_contains_unit(self, session: Session) -> None:
        g = build_org_graph(session)
        assert self.unit["Id"] in g

    def test_graph_has_edge_from_unit_to_root(self, session: Session) -> None:
        g = build_org_graph(session)
        assert (ROOT_ID, self.unit["Id"]) in g.edges


class Test_when_org_has_member_in_unit(NonEmptyPostconditions):

    unit: OrganizationalUnitTypeDef
    member: AccountTypeDef

    @fixture(autouse=True)
    def org(self, session: Session) -> None:
        _create_org(session)
        self.unit = _create_unit(session, parent_id=ROOT_ID)
        self.member = _create_member(session, parent_id=self.unit["Id"])

    def test_graph_contains_member(self, session: Session) -> None:
        g = build_org_graph(session)
        assert self.member["Id"] in g

    def test_graph_has_edge_from_unit_to_member(self, session: Session) -> None:
        g = build_org_graph(session)
        assert (self.unit["Id"], self.member["Id"]) in g.edges


class Test_when_org_has_20_members_in_root(NonEmptyPostconditions):
    """The Organizations APIs return pages of 20 accounts. Including the
    management account there will be 21 accounts in the root OU. The
    implementation needs to iterate the pages."""

    members: List[AccountTypeDef]

    @fixture(autouse=True)
    def org(self, session: Session) -> None:
        _create_org(session)
        self.members = [_create_member(session, ROOT_ID) for _ in range(20)]

    def test_graph_has_all_members(self, session: Session) -> None:
        g = build_org_graph(session)
        for m in self.members:
            assert m["Id"] in g


class Test_when_org_has_20_units_in_root(NonEmptyPostconditions):
    """The Organizations APIs return pages of 20 accounts. Including the
    management account there will be 21 accounts in the root OU. The
    implementation needs to iterate the pages."""

    members: List[OrganizationalUnitTypeDef]

    @fixture(autouse=True)
    def org(self, session: Session) -> None:
        _create_org(session)
        self.units = [_create_unit(session, ROOT_ID) for _ in range(20)]

    def test_graph_has_all_members(self, session: Session) -> None:
        g = build_org_graph(session)
        for u in self.units:
            assert u["Id"] in g
