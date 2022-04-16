from typing import Iterator, Final
from boto3 import Session
from moto import mock_organizations, mock_sts, organizations
from pytest import fixture, raises, mark, fail
from aws_org_graph import build_org_graph
import networkx as nx
from pytest_mock import MockerFixture


ROOT_ID: Final = "r-0001"
MANAGEMENT_ACCOUNT_ID: Final = organizations.utils.MASTER_ACCOUNT_ID

def draw(g: nx.Graph):
    """Draw the graph in the Pytest debugger."""
    import matplotlib.pyplot as plt
    nx.draw(g, with_labels=True)
    plt.show()


@fixture
def session() -> Iterator[Session]:
    with mock_sts(), mock_organizations():
        yield Session()


@fixture
def new_org(session: Session, mocker: MockerFixture):

    mocker.patch(
        "moto.organizations.utils.make_random_root_id",
        lambda: ROOT_ID
    )

    org = session.client("organizations")
    org.create_organization(FeatureSet="ALL")


def test_when_no_org_exists_returns_empty_graph(session: Session):
    empty = nx.Graph()
    g = build_org_graph(session)
    assert nx.utils.graphs_equal(empty, g)


@mark.usefixtures("new_org")
def test_when_org_is_new_graph_has_root(session: Session):
    g = build_org_graph(session)
    assert ROOT_ID in g


@mark.usefixtures("new_org")
def test_when_org_is_new_graph_has_management_account(session: Session):
    g = build_org_graph(session)
    assert MANAGEMENT_ACCOUNT_ID in g


@mark.usefixtures("new_org")
def test_when_org_is_new_graph_has_edge_between_root_and_management_account(session: Session):
    g = build_org_graph(session)
    assert (ROOT_ID, MANAGEMENT_ACCOUNT_ID) in g.edges
