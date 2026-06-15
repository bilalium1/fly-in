"""Dijkstra pathfinding for the Fly-in network."""

import heapq
from typing import Dict, List, Optional

from models import Hub, Sim, ZONE_COST


def dijkstra(sim: Sim, start: Hub, end: Hub) -> Optional[List[Hub]]:
    """Compute the shortest-cost path between two hubs.

    Cost of entering a hub depends on its zone type:
    normal/priority = 1, restricted = 2, blocked = unreachable.

    Args:
        sim: The simulation graph.
        start: Starting hub.
        end: Destination hub.

    Returns:
        List of hubs from start to end (inclusive), or None if
        no path exists.
    """
    dist: Dict[str, float] = {name: float("inf") for name in sim.hubs}
    prev: Dict[str, Optional[str]] = {name: None for name in sim.hubs}
    dist[start.name] = 0.0

    counter = 0
    heap: List[tuple] = [(0.0, counter, start.name)]
    visited: Dict[str, bool] = {}

    while heap:
        current_cost, _, current_name = heapq.heappop(heap)

        if visited.get(current_name):
            continue
        visited[current_name] = True

        if current_name == end.name:
            break

        current_hub = sim.hubs[current_name]

        for neighbor, _conn in sim.neighbors(current_hub):
            if neighbor.zone == "blocked":
                continue

            move_cost = ZONE_COST.get(neighbor.zone, 999)
            new_cost = current_cost + move_cost

            if new_cost < dist[neighbor.name]:
                dist[neighbor.name] = new_cost
                prev[neighbor.name] = current_name
                counter += 1
                heapq.heappush(heap, (new_cost, counter, neighbor.name))

    if dist[end.name] == float("inf"):
        return None

    path_names: List[str] = []
    cur: Optional[str] = end.name
    while cur is not None:
        path_names.insert(0, cur)
        cur = prev[cur]

    if path_names[0] != start.name:
        return None

    return [sim.hubs[name] for name in path_names]
