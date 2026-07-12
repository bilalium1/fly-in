"""Dijkstra pathfinding and Yen's k-shortest paths for the Fly-in network."""

import heapq
import math
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

from models import ZONE_COST, Hub, Sim


def dijkstra(
    sim: Sim,
    start: Hub,
    end: Hub,
    removed_edges: Optional[FrozenSet[Tuple[str, str]]] = None,
) -> Optional[List[Hub]]:
    """Compute the shortest-cost path between two hubs.

    Cost is based on destination zone type:
    normal/priority=1, restricted=2, blocked=unreachable.

    Args:
        sim: The simulation graph.
        start: Starting hub.
        end: Destination hub.
        removed_edges: Edges to treat as absent (used by Yen's algorithm).

    Returns:
        List of hubs from start to end inclusive, or None if unreachable.
    """
    blocked: FrozenSet[Tuple[str, str]] = removed_edges or frozenset()

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

    paths: List[List[Hub]] = [first]
    candidates: List[Tuple[float, int, List[Hub]]] = []
    seen: Set[Tuple[str, ...]] = {tuple(h.name for h in first)}
    tie: int = 0

    for i in range(1, k):
        prev_path = paths[i - 1]

        for spur_idx in range(len(prev_path) - 1):
            spur_node = prev_path[spur_idx]
            root_path = prev_path[:spur_idx]

            removed: Set[Tuple[str, str]] = set()
            for p in paths:
                if p[:spur_idx] == root_path:
                    removed.add((p[spur_idx].name, p[spur_idx + 1].name))

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


def _score_assignment(
    paths: List[List[Hub]],
    counts: List[int],
) -> float:
    """Return the maximum estimated turns across all path groups.

    The simulation ends when the slowest path finishes, so we minimise
    the maximum (makespan).

    Args:
        paths: List of candidate paths.
        counts: Number of drones assigned to each path.

    Returns:
        Makespan as a float.
    """
    return max(
        (
            estimated_turns(paths[i], counts[i])
            for i in range(len(paths))
            if counts[i] > 0
        ),
        default=0.0,
    )


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
    4. If hill-climbing on the remaining paths can further reduce the
       makespan, apply it.

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

    # Step 3: strict interleaved round-robin assignment.
    # Drone 0 → lane 0, Drone 1 → lane 1, ..., Drone k → lane k%len(lanes)
    counts: List[int] = [0] * len(lanes)
    for idx in range(n):
        counts[idx % len(lanes)] += 1

    # Step 4: hill-climbing refinement against makespan.
    improved = True
    while improved:
        improved = False
        current = _score_assignment(lanes, counts)
        best_delta = 0.0
        best_i, best_j = -1, -1

        for i in range(len(lanes)):
            if counts[i] == 0:
                continue
            for j in range(len(lanes)):
                if i == j:
                    continue
                counts[i] -= 1
                counts[j] += 1
                score = _score_assignment(lanes, counts)
                delta = current - score
                if delta > best_delta:
                    best_delta = delta
                    best_i, best_j = i, j
                counts[i] += 1
                counts[j] -= 1

        if best_i != -1:
            counts[best_i] -= 1
            counts[best_j] += 1
            improved = True

    # Step 5: apply, interleaving across lanes so consecutive drones
    # on the same lane are spread apart (minimises head-of-line blocking).
    assignment: List[int] = []
    lane_queues = [counts[i] for i in range(len(lanes))]
    while sum(lane_queues) > 0:
        for lane_idx in range(len(lanes)):
            if lane_queues[lane_idx] > 0:
                assignment.append(lane_idx)
                lane_queues[lane_idx] -= 1

    for drone_idx, lane_idx in enumerate(assignment):
        if drone_idx < n:
            drones[drone_idx].path = lanes[lane_idx]
            drones[drone_idx].path_index = 0
