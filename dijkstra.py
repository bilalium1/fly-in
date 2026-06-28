"""Dijkstra pathfinding and Yen's k-shortest paths for the Fly-in network."""

import heapq
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

from models import ZONE_COST, Hub, Sim


def dijkstra(
    sim: Sim,
    start: Hub,
    end: Hub,
    removed_edges: Optional[FrozenSet[Tuple[str, str]]] = None,
) -> Optional[List[Hub]]:
    """Compute the shortest-cost path between two hubs.

    Cost of entering a hub depends on its zone type:
    normal/priority = 1, restricted = 2, blocked = unreachable.

    Args:
        sim: The simulation graph.
        start: Starting hub.
        end: Destination hub.
        removed_edges: Optional set of (hub_a_name, hub_b_name) pairs
            to treat as absent during this search (used by Yen's algorithm).

    Returns:
        List of hubs from start to end (inclusive), or None if no path exists.
    """
    # set of blocked links, meaning current path can't use this.
    blocked: FrozenSet[Tuple[str, str]] = removed_edges or frozenset()

    # dist {hub_name : cost} includes every hub and its distance from start
    # start with {start : 0 , <everything else> : inf}
    dist: Dict[str, float] = {name: float("inf") for name in sim.hubs}

    # prev {hub_name : previous hub} to rebuild path
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

        # if current hub has already been visted, skip.
        if current_name in visited:
            continue
        visited.add(current_name)

        # if the current hub is the end, stop.
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

    if dist[end.name] == float("inf"):
        return None

    path_names: List[str] = []
    cur: Optional[str] = end.name
    while cur is not None:
        path_names.insert(0, cur)
        cur = prev[cur]

    if not path_names or path_names[0] != start.name:
        return None

    return [sim.hubs[name] for name in path_names]


def path_cost(path: List[Hub]) -> float:
    """Compute the total movement cost of a path (cost on destination hubs).

    Args:
        path: Ordered list of hubs representing the route.

    Returns:
        Total float cost of traversing the path.
    """
    return sum(float(ZONE_COST.get(h.zone, 999)) for h in path[1:])


def path_bottleneck(path: List[Hub]) -> int:
    """Return the minimum max_drones capacity along a path (excluding start).

    Args:
        path: Ordered list of hubs representing the route.

    Returns:
        Minimum hub capacity encountered, or 1 if path has only start.
    """
    if len(path) <= 1:
        return 1
    return min(h.max_drones for h in path[1:])


def yen_k_shortest_paths(
    sim: Sim,
    start: Hub,
    end: Hub,
    k: int,
) -> List[List[Hub]]:
    """Find up to k shortest paths using Yen's algorithm.

    Paths are loopless and listed in order of increasing cost.
    Blocked zones are automatically excluded.

    Args:
        sim: The simulation graph.
        start: Starting hub.
        end: Destination hub.
        k: Maximum number of distinct paths to find.

    Returns:
        List of paths (each a list of hubs), possibly fewer than k
        if the graph has fewer distinct routes.
    """
    first = dijkstra(sim, start, end)
    if first is None:
        return []

    paths: List[List[Hub]] = [first]
    # Heap of (cost, tie_breaker, path)
    candidates: List[Tuple[float, int, List[Hub]]] = []
    seen: Set[Tuple[str, ...]] = {tuple(h.name for h in first)}
    tie: int = 0

    for i in range(1, k):
        prev_path = paths[i - 1]

        for spur_idx in range(len(prev_path) - 1):
            spur_node = prev_path[spur_idx]
            root_path = prev_path[:spur_idx]

            # Collect edges to remove: edges used by any known path
            # that shares the same root, to force a deviation.
            removed: Set[Tuple[str, str]] = set()
            for p in paths:
                if p[:spur_idx] == root_path:
                    removed.add((p[spur_idx].name, p[spur_idx + 1].name))

            # Also block all root-path nodes from being re-entered
            # (except the spur node itself) to avoid loops.
            root_names: Set[str] = {h.name for h in root_path}
            for rname in root_names:
                for neighbor, _ in sim.neighbors(sim.hubs[rname]):
                    removed.add((rname, neighbor.name))
                    removed.add((neighbor.name, rname))

            spur_path = dijkstra(sim, spur_node, end, frozenset(removed))
            if spur_path is None:
                continue

            full_path = root_path + spur_path
            key = tuple(h.name for h in full_path)
            if key in seen:
                continue
            seen.add(key)

            cost = path_cost(full_path)
            tie += 1
            heapq.heappush(candidates, (cost, tie, full_path))

        if not candidates:
            break

        _, _, best = heapq.heappop(candidates)
        paths.append(best)

    return paths


def assign_drones_to_paths(
    drones: List["Drone"],  # type: ignore[name-defined]  # noqa: F821
    paths: List[List[Hub]],
) -> None:
    """Distribute drones across available paths to minimise total turns.

    Scoring: lower cost and higher bottleneck capacity = better path.
    Drones are assigned round-robin across paths sorted by score, so
    paths with wider/faster throughput get proportionally more drones.

    Args:
        drones: All drones to assign.
        paths: Candidate paths from Yen's algorithm.
    """
    scored: List[Tuple[float, List[Hub]]] = []
    for p in paths:
        cost = path_cost(p)
        bottleneck = max(path_bottleneck(p), 1)
        # Lower score = better: cheap paths with wide capacity win.
        score = cost / bottleneck
        scored.append((score, p))

    scored.sort(key=lambda x: x[0])

    for idx, drone in enumerate(drones):
        _, chosen = scored[idx % len(scored)]
        drone.path = chosen
        drone.path_index = 0
