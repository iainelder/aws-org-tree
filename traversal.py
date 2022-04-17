from queue import Empty, Queue
from threading import Thread
from typing import Generic, Iterable, Optional, Protocol, TypeVar, Tuple

T = TypeVar("T")


class GetRoots(Protocol, Generic[T]):  # type: ignore[misc]
    def __call__(self) -> Iterable[T]:
        ...


class GetChildren(Protocol, Generic[T]):
    def __call__(self, node: T) -> Iterable[T]:
        ...


class NodeVisitor(Protocol, Generic[T]):  # type: ignore[misc]
    def __call__(self, node: T, parent: Optional[T]) -> None:
        ...

# I'm not sure whether I really like this or not. The type checker doesn't. It
# wants T to be contravariant and covariants at the same time. Is it too
# abstract a solution? Still it seems like a good idea to separate the traversal
# algorithm from the specifics of getting the roots and the nodes.
def concurrent_traversal(
    get_roots: GetRoots[T],
    get_children: GetChildren[T],
    visit: NodeVisitor[T],
    worker_count: int = 2,
) -> None:

    node_queue: Queue[Tuple[T, Optional[T]]] = Queue()
    things_left_to_do = True

    def process() -> None:
        while things_left_to_do:
            try:
                node, parent = node_queue.get(timeout=0.5)
                visit(node, parent)
            except Empty:
                continue
            for child in get_children(node):
                node_queue.put((child, node))
            node_queue.task_done()

    threads = [Thread(target=process) for _ in range(worker_count)]

    for t in threads:
        t.start()

    try:
        for node in get_roots():
            node_queue.put((node, None))

        node_queue.join()

    finally:
        things_left_to_do = False

    for t in threads:
        t.join()
