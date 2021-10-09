import boto3
from boto_collator_client import CollatorClient
import anytree
import anytree.exporter
import logdecorator
import logging
import datetime


logger = None


def main():

    configure_logging()
    print(export_org_tree())


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

        def isoformat(obj):

            if isinstance(obj, (datetime.datetime)):
                return obj.isoformat()

            raise TypeError(f"Type {type(obj)} is not serializable")

        return anytree.exporter.JsonExporter(default=isoformat).export(self._root)


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

        if root.Type == "ACCOUNT":
            return root
        
        child_accounts = self._get_children(root.Id, "ACCOUNT")
        child_ohyous = self._get_children(root.Id, "ORGANIZATIONAL_UNIT")

        for children in [child_accounts, child_ohyous]:
            for ch in children:
                self._build_tree(ch, parent=root)

        return root


    @logdecorator.log_on_end(logging.DEBUG, "Built node {result}", logger=logger)
    def _build_node(self, org_thing, parent):
        return anytree.Node(org_thing["Id"], **org_thing, parent=parent)


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
