"""Dijkstra pathfinding and Yen's k-shortest paths for the Fly-in network."""

import heapq
import math
from typing import Dict, Set, List, Optional, Tuple

from models import ZONE_COST, Hub, Sim


def dijkstra(
    sim: Sim,
    start: Hub,
    end: Hub,
    blocked: Set[Tuple[str, str]] = set(),
) -> Optional[List[Hub]]:
    """Compute the shortest-cost path between two hubs."""

    dist: Dict[str, float] = {name: float("inf") for name in sim.hubs}
    prev: Dict[str, Optional[str]] = {name: None for name in sim.hubs}
    dist[start.name] = 0.0

    heap: List[Tuple[float, str]] = [(0.0, start.name)]
    visited: Set[str] = set()

    while heap:
        current_cost, current_name = heapq.heappop(heap)

        if current_name in visited:
            continue
        visited.add(current_name)

        if current_name == end.name:
            break

        current_hub = sim.hubs[current_name]

        for neighbor, _conn in sim.neighbors(current_hub):
            if neighbor.zone == "blocked":
                continue

            edge = (current_name, neighbor.name)
            edge_rev = (neighbor.name, current_name)
            if edge in blocked or edge_rev in blocked:
                continue

            move_cost = float(ZONE_COST.get(neighbor.zone, 999))
            new_cost = current_cost + move_cost

            if new_cost < dist[neighbor.name]:
                dist[neighbor.name] = new_cost
                prev[neighbor.name] = current_name
                heapq.heappush(heap, (new_cost, neighbor.name))

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
    return sum(float(ZONE_COST.get(h.zone, 999)) for h in path[1:])


def path_bottleneck(path: List[Hub]) -> int:
    interior = path[1:-1]
    if not interior:
        return 1
    return min(h.max_drones for h in interior)


def estimated_turns(path: List[Hub], n_drones: int) -> float:
    """Estimate turns to route n_drones along a single path.

    Models the pipeline: first drone takes path_cost turns, then each
    subsequent drone is delayed by 1/bottleneck turns due to queuing.

    Args:
        path: The route.
        n_drones: Number of drones assigned to this path.

    Returns:
        Estimated total turns (float for scoring).
    """
    if n_drones == 0:
        return 0.0
    cost = path_cost(path)
    bottleneck = max(path_bottleneck(path), 1)
    return cost + math.ceil((n_drones - 1) / bottleneck)


def yen_k_shortest_paths(
    sim: Sim,
    start: Hub,
    end: Hub,
    k: int,
) -> List[List[Hub]]:
    """Find up to k shortest loopless paths using Yen's algorithm.

    Args:
        sim: The simulation graph.
        start: Starting hub.
        end: Destination hub.
        k: Maximum number of paths to find.

    Returns:
        List of paths in order of increasing cost, possibly fewer than k.
    """
    first = dijkstra(sim, start, end)
    if first is None:
        return []

    # all efficient paths discovered
    paths: List[List[Hub]] = [first]
    # all cadidate paths to be determined
    candidates: List[Tuple[float, List[Hub]]] = []
    # path already discovere
    seen: Set[Tuple[str, ...]] = {tuple(h.name for h in first)}

    for i in range(1, k):
        # LOOPING FOR PATHS
        prev_path = paths[i - 1]

        # SPUR IS THE NODE WHICH WILL HAVE ITS CONNECTIONS CUT
        for spur_idx in range(len(prev_path) - 1):
            spur_node = prev_path[spur_idx]
            # ROOT PATH IS THE PATH THAT COMES BEFORE SPUR
            root_path = prev_path[:spur_idx]

            # REMOVE ANY
            removed: Set[Tuple[str, str]] = set()
            for p in paths:
                if p[:spur_idx] == root_path:
                    removed.add((p[spur_idx].name, p[spur_idx + 1].name))

            for hub in root_path:
                for neighbor, _ in sim.neighbors(hub):
                    removed.add((hub.name, neighbor.name))
                    removed.add((neighbor.name, hub.name))

            spur_path = dijkstra(sim, spur_node, end, set(removed))
            if spur_path is None:
                continue

            full_path = root_path + spur_path
            key = tuple(h.name for h in full_path)
            if key in seen:
                continue
            seen.add(key)

            cost = path_cost(full_path)
            heapq.heappush(candidates, (cost, full_path))

        if not candidates:
            break

        _, best = heapq.heappop(candidates)
        paths.append(best)

    return paths

def assign_drones_to_paths(
    drones: List["Drone"],  # type: ignore[name-defined]  # noqa: F821
    paths: List[List[Hub]],
) -> None:
    """Distribute drones across paths to minimise total simulation turns.

    Strategy:
    1. Find the minimum path cost (the fastest route).
    2. Keep only paths that share that minimum cost — longer paths are
       strictly dominated when the intake bottleneck is 1 drone/turn,
       because longer paths just delay the last drone without allowing
       any extra parallelism.
    3. Interleave drones strictly across the equal-cost paths in a
       round-robin pattern so consecutive drones on the same path are
       spaced apart, avoiding congestion at shared bottlenecks.

    Args:
        drones: All drones to assign (modified in place).
        paths: Candidate paths from Yen's algorithm (cheapest first).
    """
    n = len(drones)
    if not paths:
        return

    # Step 1: find minimum cost and keep only equal-cost paths.
    min_cost = path_cost(paths[0])
    equal_cost = [p for p in paths if path_cost(p) == min_cost]

    # Step 2: if only one distinct cost available, use all of them up to n.
    if not equal_cost:
        equal_cost = paths[:1]

    # Cap at a sensible number of lanes to avoid combinatorial explosion.
    lanes = equal_cost[: min(len(equal_cost), n)]

    for idx in range(n):
        drones[idx].path = lanes[idx % len(lanes)]
        drones[idx].path_index = 0
