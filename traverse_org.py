from typing import Iterable

from boto3 import Session
from mypy_boto3_organizations.type_defs import OrganizationalUnitTypeDef as OrgUnit

from traversal import concurrent_traversal


def main() -> None:
    concurrent_traversal(get_roots, get_children, print_node)  # type: ignore[arg-type]


def get_roots() -> Iterable[OrgUnit]:
    return _iter_roots(Session())


def get_children(parent: OrgUnit) -> Iterable[OrgUnit]:
    return _iter_child_orgunits(Session(), parent)


def print_node(node: OrgUnit, parent: OrgUnit) -> None:
    print(f"{node=} {parent=}")


def _iter_roots(session: Session) -> Iterable[OrgUnit]:
    org = session.client("organizations")
    paginator = org.get_paginator("list_roots")
    for page in paginator.paginate():
        for root in page["Roots"]:
            yield root


def _iter_child_orgunits(session: Session, parent: OrgUnit) -> Iterable[OrgUnit]:
    org = session.client("organizations")
    paginator = org.get_paginator("list_organizational_units_for_parent")
    for page in paginator.paginate(ParentId=parent["Id"]):
        for unit in page["OrganizationalUnits"]:
            yield unit


if __name__ == "__main__":
    main()
