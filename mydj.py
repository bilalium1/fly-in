import heapq
from optparse import Option
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

from models import ZONE_COST, Hub, Sim


def dijkstra(
    sim: Sim,
    start: Hub,
    end: Hub,
    removed_edges: Optional[FrozenSet[Tuple[str, str]]] = None,
) -> Optional[List[Hub]]:
    """
    Get the shortest path from start to end.

    Cost of enetering a hub depends on zonetype:
        normal/priority = 1, restricted = 2, blocked = unreachable.

        Args:
            sim: The simulation graph.
            start: Starting Hub.
            end: Destination Hub.
            removed_edges: Optional set of (hub_a_name, hub_b_name) pairs
            to ignore in order to create another path.

        Returns:
            List of hubs from start to end (inclusive), or None if no path exists.
    """
    # set of blocked links if there are any
    blocked: FrozenSet[Tuple[str, str]] = removed_edges or frozenset()

    # dist {hub_name : cost} includes every hub and its distance form start
    # start with {start : 0, <everything else>: inf}
    dist: Dict[str, float] = {name: float("inf") for name in sim.hubs}

    # prev {hub_name : previous_hub} to rebuild path
    prev: Dict[str, Optional[str]] = {name: None for name in sim.hubs}

    dist[start.name] = 0.0

    counter = 0  # used as tie-breaker for priority heap

    # priority heap, lowest cost is popped first
    heap: List[Tuple[float, int, str]] = [(0.0, counter, start.name)]
    visited: Set[str] = set()

    # while heap not empty loop
    while heap:
        # pop first element in heap
        current_cost, _, current_name = heapq.heappop(heap)

        # if current hub has already been visited, skip.
        if current_name in visited:
            continue
        visited.add(current_name)

        # if current hub is the end, stop.
        if current_name == end.name:
            break

        # get current hub as OBJECT
        current_hub = sim.hubs[current_name]

        for neighbor, _conn in sim.neighbors(current_hub):
            if neighbor.zone == "blocked":
                continue

            # check if current edge has been used already/ blocked / in blacklist
            edge = (current_name, neighbor.name)
            edge_rev = (neighbor.name, current_name)
            if edge in blocked or edge_rev in blocked:
                continue

            # get move cost, if not available return 999
            move_cost = float(ZONE_COST.get(neighbor.zone, 999))
            new_cost = current_cost + move_cost

            # if current calculated cost is smaller than already established, replace it
            if new_cost < dist[neighbor.name]:
                dist[neighbor.name] = new_cost
                prev[neighbor.name] = current_name
                counter += 1
                heapq.heappush(heap, (new_cost, counter, neighbor.name))

    # no path was found
    if dist[end.name] == float("inf"):
        return None

    path_names: List[str] = []
    cur: Optional[str] = end.name
