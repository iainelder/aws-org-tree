from aws_org_graph import build_org_graph
from boto3 import Session
import networkx as nx  # type: ignore[import]
import matplotlib.pyplot as plt  # type: ignore[import]

def main() -> None:
    session = Session()
    graph = build_org_graph(session)
    draw(graph)


def draw(graph: nx.Graph) -> None:
    nx.draw(graph, with_labels=True)
    plt.show()


if __name__ == "__main__":
    main()
