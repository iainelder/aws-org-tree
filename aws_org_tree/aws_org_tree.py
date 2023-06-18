import datetime
import json
import logging
from argparse import ArgumentParser, Namespace
from typing import Any, Dict, List, Mapping, Optional, Protocol, TypeVar, Union
from importlib.metadata import version

import anytree
import anytree.exporter
import logdecorator
from anytree import LevelOrderIter
from boto3.session import Session
from mypy_boto3_organizations.client import OrganizationsClient
from mypy_boto3_organizations.type_defs import (
    AccountTypeDef,
    OrganizationalUnitTypeDef,
    RootTypeDef,
)

# I need a global logger for the logdecorator functions.
# FIXME: Use the default behavior of the logger parameter.
logger: Optional[logging.Logger] = None

OrgThing = Union[RootTypeDef, AccountTypeDef, OrganizationalUnitTypeDef]


class OrgTreeArgParser(ArgumentParser):
    def __init__(self) -> None:
        super().__init__()
        self.add_argument(
            "--tree-format",
            default="text-tree",
            choices=["json-flat", "json-tree", "text-tree"],
        )
        self.add_argument("--node-name-format", default="{Name} ({Id})")
        self.add_argument("--log-level", default="WARNING")
        self.add_argument("--version", action="version", version=version("aws-org-tree"))


class OrgTreeArgs(Namespace):
    tree_format: str
    node_name_format: str
    log_level: str


def main() -> None:
    args = OrgTreeArgParser().parse_args(namespace=OrgTreeArgs())

    configure_logging(args.log_level)

    formatter: Formatter
    if args.tree_format == "json-flat":
        formatter = JsonFlatOutput()
    elif args.tree_format == "json-tree":
        formatter = JsonTreeOutput()
    elif args.tree_format == "text-tree":
        formatter = TextTreeOutput(args.node_name_format)
    else:
        raise AssertionError(args.tree_format)

    print(formatter.render(OrgTree().build()))


def configure_logging(log_level: str) -> None:
    """Set the log level on this module.

    Don't change the log level for boto3. Its DEBUG level floods the log.
    """

    global logger

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(log_level)


class OrgTree(object):
    def __init__(self, session: Optional[Session] = None) -> None:
        self._session = session if session is not None else Session()
        self._orgs: OrganizationsClient = self._session.client("organizations")
        self._root = None

    @logdecorator.log_on_start(logging.INFO, "Start building org tree", logger=logger)
    @logdecorator.log_on_end(logging.INFO, "Finish building org tree", logger=logger)
    def build(self) -> "OrgTree":
        root = self._get_root()
        self._root = self._build_tree(root, parent=None)
        return self

    def to_dict(self) -> Dict[Any, Any]:
        return anytree.exporter.DictExporter().export(self._root)  # type: ignore[no-any-return]

    def to_json(self) -> str:
        return anytree.exporter.JsonExporter(cls=ISODateJSONEncoder).export(self._root)  # type: ignore[no-any-return]

    def to_flat_dict(self) -> List[Dict[Any, Any]]:
        return [
            {
                **n.Properties,
                **{"Parent": n.parent.Properties["Id"] if n.parent else None},
            }
            for n in LevelOrderIter(self._root)
        ]

    def to_flat_json(self) -> str:
        return json.dumps(self.to_flat_dict(), cls=ISODateJSONEncoder)

    def render(self) -> anytree.RenderTree:
        return anytree.RenderTree(self._root)

    @logdecorator.log_on_start(logging.DEBUG, "Get org root", logger=logger)
    @logdecorator.log_on_end(
        logging.DEBUG, "Got org root {result[" "Id" "]}", logger=logger
    )
    def _get_root(self) -> RootTypeDef:
        root = self._orgs.list_roots()["Roots"][0]
        root["Type"] = "ROOT"  # type: ignore[typeddict-item]
        return root

    def _build_tree(
        self, org_thing: OrgThing, parent: Optional[OrgThing]
    ) -> anytree.Node:
        root: anytree.Node = self._build_node(org_thing, parent)

        if root.Properties["Type"] == "ACCOUNT":
            return root

        child_accounts = self._list_accounts_for_parent(root.Properties["Id"])
        child_ohyous = self._list_organizational_units_for_parent(root.Properties["Id"])

        for children in [child_accounts, child_ohyous]:
            for ch in children:
                self._build_tree(ch, parent=root)

        return root

    @logdecorator.log_on_end(logging.DEBUG, "Built node {result}", logger=logger)
    def _build_node(
        self, org_thing: OrgThing, parent: Optional[OrgThing]
    ) -> anytree.Node:
        # Properties was a sin committed to make the json-flat formatting easier.
        return anytree.Node(org_thing["Id"], Properties=org_thing, parent=parent)

    @logdecorator.log_on_start(
        logging.DEBUG, "Get accounts for parent={parent_id}", logger=logger
    )
    @logdecorator.log_on_end(
        logging.DEBUG,
        "Parent {parent_id} has accounts {result}",
        logger=logger,
    )
    def _list_accounts_for_parent(self, parent_id: str) -> List[AccountTypeDef]:
        pages = self._orgs.get_paginator("list_accounts_for_parent").paginate(
            ParentId=parent_id
        )
        accounts = [ac for page in pages for ac in page["Accounts"]]
        for ac in accounts:
            ac["Type"] = "ACCOUNT"  # type: ignore[typeddict-item]
        return accounts

    @logdecorator.log_on_start(
        logging.DEBUG, "Get organizational units for parent={parent_id}", logger=logger
    )
    @logdecorator.log_on_end(
        logging.DEBUG,
        "Parent {parent_id} has organizational units {result}",
        logger=logger,
    )
    def _list_organizational_units_for_parent(
        self, parent_id: str
    ) -> List[OrganizationalUnitTypeDef]:
        pages = self._orgs.get_paginator(
            "list_organizational_units_for_parent"
        ).paginate(ParentId=parent_id)
        organizational_units = [
            ou for page in pages for ou in page["OrganizationalUnits"]
        ]
        for ou in organizational_units:
            ou["Type"] = "ORGANIZATIONAL_UNIT"  # type: ignore[typeddict-item]
        return organizational_units


class ISODateJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)


class Formatter(Protocol):
    def render(self, org_tree: OrgTree) -> str:
        ...


class JsonTreeOutput:
    def render(self, org_tree: OrgTree) -> str:
        return org_tree.to_json()


class JsonFlatOutput:
    def render(self, org_tree: OrgTree) -> str:
        return org_tree.to_flat_json()


class Default(Dict[str, str]):
    def __missing__(self, key: str) -> str:
        return key


class TextTreeOutput:
    def __init__(self, node_name_format: str) -> None:
        self.node_name_format = node_name_format

    def render(self, org_tree: OrgTree) -> str:
        r = org_tree.render()
        return "".join([f"{pre}{self._format_name(node)}\n" for pre, _, node in r])

    def _format_name(self, node: anytree.Node) -> str:
        return self.node_name_format.format_map(Default(node.Properties))
