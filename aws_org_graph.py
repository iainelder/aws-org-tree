from boto3 import Session
from networkx import Graph
from queue import SimpleQueue, Empty

def build_org_graph(session: Session) -> Graph:

    g = Graph()
    ouq = SimpleQueue()

    org = session.client("organizations")
    resp = org.list_roots()

    if resp["Roots"]:
        root = resp["Roots"][0]
        ouq.put(root)
    
    while True:
        try:
            ou = ouq.get(block=False)
            child_accounts = org.list_accounts_for_parent(ParentId=ou["Id"])["Accounts"]
            for ac in child_accounts:
                g.add_edge(ou["Id"], ac["Id"])
        except Empty:
            break

    return g
