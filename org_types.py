from boto3 import Session
from typing import Callable, Iterable, Union, Mapping
from mypy_boto3_organizations.type_defs import (
    AccountTypeDef,
    OrganizationalUnitTypeDef,
    RootTypeDef,
    PolicySummaryTypeDef,
    TagTypeDef,
    PolicyTypeSummaryTypeDef,
    PolicyTypeDef,
    PolicyTargetSummaryTypeDef,
)


Root = RootTypeDef
OrgUnit = OrganizationalUnitTypeDef
RootOrOrgUnit = Union[Root, OrgUnit]
Account = AccountTypeDef

Policy = PolicySummaryTypeDef
PolType = PolicyTypeSummaryTypeDef
PolDoc = PolicyTypeDef
PolTarget = PolicyTargetSummaryTypeDef

Tag = TagTypeDef

OrgThing = Union[Root, OrgUnit, Account, Policy]


IterRoots = Callable[[Session], Iterable[Root]]

IterChildOrgUnits = Callable[[Session, RootOrOrgUnit], Iterable[OrgUnit]]

IterChildAccounts = Callable[[Session, RootOrOrgUnit], Iterable[Account]]

IterTags = Callable[[Session, OrgThing], Iterable[Tag]]

MapTags = Callable[[Iterable[Tag]], Mapping[str, str]]

IterPolicyTypes = Callable[[Session, Root], Iterable[PolType]]

IterPolicies = Callable[[Session, PolType], Iterable[Policy]]

IterPolicyTargets = Callable[[Session, Policy], Iterable[PolTarget]]

GetPolicyDocument = Callable[[Session, Policy], PolDoc]
