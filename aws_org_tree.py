import json
import boto3
from boto_collator_client import CollatorClient
import anytree
from anytree import LevelOrderIter
import anytree.exporter
import logdecorator
import logging
import datetime
import sys

__VERSION__ = "0.2.0"

logger = None


def main():

    configure_logging()

    format = "text-tree" if len(sys.argv) == 1 else sys.argv[1]

    formatter = {
        "json-flat": export_org_flat,
        "json-tree": export_org_tree,
        "text-tree": render_org
    }[format]

    print(formatter())


def configure_logging():

    global logger

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    # FIXME: Where is a better place for this?
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)


def export_org_tree():

    return (
        OrgTree()
        .build()
        .to_json()
    )


def export_org_flat():

    return (
        OrgTree()
        .build()
        .to_flat_json()
    )


def render_org():
    r = (
        OrgTree()
        .build()
        .render()
    )

    return "".join([f"{pre}{node.name}\n" for pre, _, node in r])


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
                **{"Parent": n.parent.Properties["Id"] if n.parent else None}
            }
            for n in LevelOrderIter(self._root)
        ]


    def to_flat_json(self):

        return json.dumps(self.to_flat_dict(), cls=ISODateJSONEncoder)


    def render(self):
        return anytree.RenderTree(self._root)


    @logdecorator.log_on_start(logging.DEBUG, "Get org root", logger=logger)
    @logdecorator.log_on_end(logging.DEBUG, "Got org root {result[""Id""]}", logger=logger)
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
    @logdecorator.log_on_start(logging.DEBUG, "Get {child_type} children for parent={parent_id}", logger=logger)
    @logdecorator.log_on_end(logging.DEBUG, "Parent {parent_id} has {child_type} children {result}", logger=logger)
    def _get_children(self, parent_id, child_type):

        orgs = CollatorClient(self._orgs)

        children = orgs.list_children(ParentId=parent_id, ChildType=child_type)["Children"]

        details = {
            "ACCOUNT": orgs.list_accounts_for_parent(ParentId=parent_id)["Accounts"],
            "ORGANIZATIONAL_UNIT": orgs.list_organizational_units_for_parent(ParentId=parent_id)["OrganizationalUnits"]
        }[child_type]

        return [{**c, **d} for c, d in zip(children, details)]


class ISODateJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super(self).default(obj)
