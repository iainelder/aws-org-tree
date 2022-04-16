from boto3 import Session
from networkx import Graph
from queue import SimpleQueue

def build_org_graph(session: Session) -> Graph:

    g = Graph()
    unit_queue = SimpleQueue()

    org = session.client("organizations")
    resp = org.list_roots()

    if resp["Roots"]:
        root = resp["Roots"][0]
        unit_queue.put(root)
    
    while not unit_queue.empty():
        parent = unit_queue.get(block=False)
        g.add_node(parent["Id"])

        child_accounts = org.list_accounts_for_parent(ParentId=parent["Id"])["Accounts"]
        for ac in child_accounts:
            g.add_edge(parent["Id"], ac["Id"])

        child_units = org.list_organizational_units_for_parent(ParentId=parent["Id"])["OrganizationalUnits"]
        for unit in child_units:
            g.add_edge(parent["Id"], unit["Id"])
            unit_queue.put(unit)

    return g
