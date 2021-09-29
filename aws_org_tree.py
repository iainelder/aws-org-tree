import boto3
import anytree
import logdecorator
import logging

logger = None

def main():
    configure_logging()
    ot = OrgTree()
    ot.build()
    print(ot.render())


def configure_logging():

    global logger

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

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

        orgs = self._session.client("organizations")
        root = orgs.list_roots()["Roots"][0]
        self._root = self._build_tree(root, parent=None)

    def render(self):
        return anytree.RenderTree(self._root)


    @logdecorator.log_on_end(logging.DEBUG, "Built node {result}", logger=logger)
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

        if org_thing["Id"].startswith("r-"):
            org_thing["Type"] = "ROOT"

        return anytree.AnyNode(**org_thing, parent=parent)


    @logdecorator.log_on_start(logging.DEBUG, "Get {child_type} children for parent={parent_id}", logger=logger)
    @logdecorator.log_on_end(logging.DEBUG, "Parent {parent_id} has {child_type} children {result}", logger=logger)
    def _get_children(self, parent_id, child_type):
        return (
            self._orgs.get_paginator("list_children")
            .paginate(ParentId=parent_id, ChildType=child_type)
            .build_full_result()
            ["Children"]
        )

    # TODO: use these functions that return more metadata in a single call.
    @logdecorator.log_on_start(logging.INFO, "Get organizational units for parent={parent_id}", logger=logger)
    @logdecorator.log_on_end(logging.INFO, "Parent {parent_id} has organizational units {result}", logger=logger)
    def _get_organizational_units_for_parent(self, parent_id):
        return self._orgs.list_organizational_units_for_parent(ParentId=parent_id)["OrganizationalUnits"]
