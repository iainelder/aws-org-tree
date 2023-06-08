# type: ignore

import datetime
import json
import logging
import sys
from argparse import ArgumentParser, Namespace
from typing import Protocol

import anytree
import anytree.exporter
import boto3
import logdecorator
from anytree import LevelOrderIter

logger = None

class OrgTreeArgParser(ArgumentParser):
    def __init__(self):
        super().__init__()
        self.add_argument(
            "--tree-format",
            default="text-tree",
            choices=["json-flat", "json-tree", "text-tree"]
        )
        self.add_argument(
            "--node-name-format", default="{Id}"
        )


class OrgTreeArgs(Namespace):
    tree_format: str
    node_name_format: str


def main():

    configure_logging()

    args = OrgTreeArgParser().parse_args(namespace=OrgTreeArgs())

    formatter: Formatter = {
        "json-flat": JsonFlatExporter(),
        "json-tree": JsonTreeExporter(),
        "text-tree": TreeRenderer(args.node_name_format),
    }[args.tree_format]

    print(formatter.render(OrgTree().build()))


def configure_logging():

    global logger

    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # FIXME: Where is a better place for this?
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)


class OrgTree(object):
    def __init__(self, session=None):
        self._session = session if session is not None else boto3.Session()
        self._orgs = self._session.client("organizations")
        self._root = None

    @logdecorator.log_on_start(logging.INFO, "Start building org tree", logger=logger)
    @logdecorator.log_on_end(logging.INFO, "Finish building org tree", logger=logger)
    def build(self):

        root = self._get_root()
        self._root = self._build_tree(root, parent=None)
        return self

    def to_dict(self):

        return anytree.exporter.DictExporter().export(self._root)

    def to_json(self):

        return anytree.exporter.JsonExporter(cls=ISODateJSONEncoder).export(self._root)

    def to_flat_dict(self):

        return [
            {
                **n.Properties,
                **{"Parent": n.parent.Properties["Id"] if n.parent else None},
            }
            for n in LevelOrderIter(self._root)
        ]

    def to_flat_json(self):

        return json.dumps(self.to_flat_dict(), cls=ISODateJSONEncoder)

    def render(self):
        return anytree.RenderTree(self._root)

    @logdecorator.log_on_start(logging.DEBUG, "Get org root", logger=logger)
    @logdecorator.log_on_end(
        logging.DEBUG, "Got org root {result[" "Id" "]}", logger=logger
    )
    def _get_root(self):

        root = self._orgs.list_roots()["Roots"][0]
        root["Type"] = "ROOT"
        return root

    def _build_tree(self, org_thing, parent):

        root = self._build_node(org_thing, parent)

        if root.Properties["Type"] == "ACCOUNT":
            return root

        child_accounts = self._get_children(root.Properties["Id"], "ACCOUNT")
        child_ohyous = self._get_children(root.Properties["Id"], "ORGANIZATIONAL_UNIT")

        for children in [child_accounts, child_ohyous]:
            for ch in children:
                self._build_tree(ch, parent=root)

        return root

    @logdecorator.log_on_end(logging.DEBUG, "Built node {result}", logger=logger)
    def _build_node(self, org_thing, parent):
        # Properties was a sin committed to make the json-flat formatting easier.
        return anytree.Node(org_thing["Id"], Properties=org_thing, parent=parent)

    # TODO: refactor with proper (data?) classes for Root, Account, OrganizationalUnit
    @logdecorator.log_on_start(
        logging.DEBUG, "Get {child_type} children for parent={parent_id}", logger=logger
    )
    @logdecorator.log_on_end(
        logging.DEBUG,
        "Parent {parent_id} has {child_type} children {result}",
        logger=logger,
    )
    def _get_children(self, parent_id, child_type):

        if child_type == "ACCOUNT":
            return self._list_accounts_for_parent(parent_id)
        if child_type == "ORGANIZATIONAL_UNIT":
            return self._list_organizational_units_for_parent(parent_id)

    def _list_accounts_for_parent(self, parent_id):
        pages = self._orgs.get_paginator("list_accounts_for_parent").paginate(
            ParentId=parent_id
        )
        return [
            {**{"Type": "ACCOUNT"}, **account}
            for page in pages
            for account in page["Accounts"]
        ]

    def _list_organizational_units_for_parent(self, parent_id):
        pages = self._orgs.get_paginator(
            "list_organizational_units_for_parent"
        ).paginate(ParentId=parent_id)
        return [
            {**{"Type": "ORGANIZATIONAL_UNIT"}, **account}
            for page in pages
            for account in page["OrganizationalUnits"]
        ]


class ISODateJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super(self).default(obj)


class Formatter(Protocol):
    def render(self, org_tree):
        ...


class JsonFlatExporter:
    def render(self, org_tree):
        return org_tree.to_json()


class JsonTreeExporter:
    def render(self, org_tree):
        return org_tree.to_flat_json()


class TreeRenderer:
    def __init__(self, node_name_format):
        self.node_name_format = node_name_format

    def render(self, org_tree):
        r = org_tree.render()
        return "".join([f"{pre}{self._format_name(node)}\n" for pre, _, node in r])

    def _format_name(self, node):
        return self.node_name_format.format_map(node.Properties)
