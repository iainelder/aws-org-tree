from argparse import ArgumentParser, Namespace
from importlib.metadata import version
import sys
from typing import IO
from orgtreepubsub import OrgCrawler, Parent, Child
from boto3 import Session

from anytree import Node, RenderTree
from anytree.search import find_by_attr  # type: ignore[import]

tree: Node | None = None

class AwsOrgTree:

    def __init__(self, session: Session) -> None:
        self.session = session

        self.crawler = OrgCrawler(session)
        self.crawler.on_root.connect(OrgCrawler.publish_orgunits_under_resource)
        self.crawler.on_root.connect(OrgCrawler.publish_accounts_under_resource)
        self.crawler.on_orgunit.connect(OrgCrawler.publish_orgunits_under_resource)
        self.crawler.on_orgunit.connect(OrgCrawler.publish_accounts_under_resource)

        self.crawler.init = self.crawler.publish_roots

        self.crawler.on_parentage.connect(self.add_edge)

        self.tree: Node | None = None

    def add_edge(self, crawler: OrgCrawler, child: Child, parent: Parent) -> None:
        print(f"{child=} {parent=}")
        if self.tree is None:
            self.tree = Node(name=parent.id, resource=parent)
            parent_node = self.tree
        else:
            parent_node: Node = find_by_attr(self.tree, parent.id)  # type: ignore[no-redef]
        Node(name=child.id, parent=parent_node, resource=child)

    def load(self) -> None:
        self.crawler.crawl()

    def write_tree(self, node_name_format:str, file: IO[str] = sys.stdout) -> None:
        for pre, _, node in RenderTree(self.tree):
            name = node_name_format.format_map(Default(node.resource))
            print(f"{pre}{name}", file=file)


class Default(dict[str, str]):
    def __missing__(self, key: str) -> str:
        return key


class OrgTreeArgParser(ArgumentParser):
    def __init__(self) -> None:
        super().__init__()
        self.add_argument("--node-name-format", default="{Name} ({Id})")
        self.add_argument(
            "--version", action="version", version=version("aws-org-tree")
        )


class OrgTreeArgs(Namespace):
    tree_format: str
    node_name_format: str
    log_level: str


def main() -> None:
    args = OrgTreeArgParser().parse_args(namespace=OrgTreeArgs())
    tree = AwsOrgTree(Session())
    tree.load()
    tree.write_tree(args.node_name_format)
