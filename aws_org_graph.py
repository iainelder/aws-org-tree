from typing import Iterable
from mypy_boto3_organizations.type_defs import AccountTypeDef
from boto3 import Session
from networkx import Graph, freeze
from queue import SimpleQueue

def build_org_graph(session: Session) -> Graph:

    g = Graph()
    unit_queue = SimpleQueue()

    org = session.client("organizations")
    resp = org.list_roots()

    if resp["Roots"]:
        root = resp["Roots"][0]
        unit_queue.put(root)
    
    while not unit_queue.empty():
        parent = unit_queue.get()
        g.add_node(parent["Id"])

        child_accounts = _iter_accounts(session, parent["Id"])
        for ac in child_accounts:
            g.add_edge(parent["Id"], ac["Id"])

        child_units = _iter_units(session, parent["Id"])
        for unit in child_units:
            g.add_edge(parent["Id"], unit["Id"])
            unit_queue.put(unit)

    return freeze(g)


def _iter_accounts(session: Session, parent_id: str) -> Iterable[AccountTypeDef]:
    org = session.client("organizations")
    paginator = org.get_paginator("list_accounts_for_parent")
    for page in paginator.paginate(ParentId=parent_id):
        for account in page["Accounts"]:
            yield account


def _iter_units(session: Session, parent_id: str) -> Iterable[AccountTypeDef]:
    org = session.client("organizations")
    paginator = org.get_paginator("list_organizational_units_for_parent")
    for page in paginator.paginate(ParentId=parent_id):
        for unit in page["OrganizationalUnits"]:
            yield unit
