from queue import SimpleQueue
from typing import Iterable, Protocol

from boto3 import Session
from mypy_boto3_organizations.type_defs import AccountTypeDef, OrganizationalUnitTypeDef, RootTypeDef
from networkx import Graph, freeze  # type: ignore[import]


def build_org_graph(session: Session) -> Graph:

    g = Graph()

    class GraphWriter:
        def visit_root(self, root: RootTypeDef) -> None:
            g.add_node(root["Id"])

        def visit_account(self, account: AccountTypeDef, parent: OrganizationalUnitTypeDef) -> None:
            g.add_edge(account["Id"], parent["Id"])

        def visit_organizational_unit(self, unit: OrganizationalUnitTypeDef, parent: OrganizationalUnitTypeDef) -> None:
            g.add_edge(unit["Id"], parent["Id"])

    _traverse_org(Session(), GraphWriter())

    return freeze(g)


class Visitor(Protocol):

    def visit_root(self, root: RootTypeDef) -> None:
        ...

    def visit_organizational_unit(
        self, unit: OrganizationalUnitTypeDef, parent: OrganizationalUnitTypeDef
    ) -> None:
        ...

    def visit_account(self, account: AccountTypeDef, parent: OrganizationalUnitTypeDef) -> None:
        ...


def _traverse_org(session: Session, visitor: Visitor) -> None:

    org = session.client("organizations")

    unit_queue: SimpleQueue[OrganizationalUnitTypeDef] = SimpleQueue()

    resp = org.list_roots()

    for root in resp["Roots"]:
        visitor.visit_root(root)
        unit_queue.put(root)

    while not unit_queue.empty():
        parent = unit_queue.get()

        child_accounts = _iter_accounts(session, parent["Id"])
        for account in child_accounts:
            visitor.visit_account(account, parent)

        child_units = _iter_units(session, parent["Id"])
        for unit in child_units:
            visitor.visit_organizational_unit(unit, parent)
            unit_queue.put(unit)


def _iter_accounts(session: Session, parent_id: str) -> Iterable[AccountTypeDef]:
    org = session.client("organizations")
    paginator = org.get_paginator("list_accounts_for_parent")
    for page in paginator.paginate(ParentId=parent_id):
        for account in page["Accounts"]:
            yield account


def _iter_units(
    session: Session, parent_id: str
) -> Iterable[OrganizationalUnitTypeDef]:
    org = session.client("organizations")
    paginator = org.get_paginator("list_organizational_units_for_parent")
    for page in paginator.paginate(ParentId=parent_id):
        for unit in page["OrganizationalUnits"]:
            yield unit
