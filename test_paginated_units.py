from boto3 import Session
from pytest import fixture, mark


def _create_org(session: Session) -> None:
    org = session.client("organizations")
    org.create_organization(FeatureSet="ALL")


def _create_unit(session: Session) -> None:
    org = session.client("organizations")
    root_id = org.list_roots()["Roots"][0]["Id"]
    org.create_organizational_unit(ParentId=root_id, Name="Example")


@fixture(autouse=True)
def org(session: Session) -> None:
    _create_org(session)
    _create_unit(session)
    _create_unit(session)


def test_without_pagination_list_returns_2_units(session: Session) -> None:
    org = session.client("organizations")
    root_id = org.list_roots()["Roots"][0]["Id"]
    units = org.list_organizational_units_for_parent(ParentId=root_id)[
        "OrganizationalUnits"
    ]
    assert len(units) == 2


@mark.usefixtures("paginated_units")
def test_with_pagination_list_returns_1_unit(session: Session) -> None:
    org = session.client("organizations")
    root_id = org.list_roots()["Roots"][0]["Id"]
    units = org.list_organizational_units_for_parent(ParentId=root_id)[
        "OrganizationalUnits"
    ]
    assert len(units) == 1


@mark.usefixtures("paginated_units")
def test_with_pagination_list_paginator_first_page_has_1_unit(session: Session) -> None:
    org = session.client("organizations")
    root_id = org.list_roots()["Roots"][0]["Id"]

    paginator = org.get_paginator("list_organizational_units_for_parent")
    units = next(iter(paginator.paginate(ParentId=root_id)))["OrganizationalUnits"]
    assert len(units) == 1


@mark.usefixtures("paginated_units")
def test_with_pagination_list_paginator_all_pages_have_1_unit(session: Session) -> None:
    org = session.client("organizations")
    root_id = org.list_roots()["Roots"][0]["Id"]

    paginator = org.get_paginator("list_organizational_units_for_parent")
    for page in paginator.paginate(ParentId=root_id):
        units = page["OrganizationalUnits"]
        assert len(units) == 1
