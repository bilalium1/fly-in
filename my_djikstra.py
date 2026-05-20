from models import Hub
from typing import Optional
import heapq


def djikstra(graph, start: Hub, end: Hub):

    dist: dict[Hub, float] = {h: 999 for h in graph.hubs.values()}
    prev: dict[Hub, Optional[Hub]] = {h: None for h in graph.hubs.values()}
    dist[Hub] = 0.0

    priority_queue = []
    counter: int = 0
    heapq.heappush(priority_queue, (0.0, counter, start))

    while len(priority_queue) > 0:
        print(priority_queue)
        current_cost, _, current_hub = heapq.heappop(priority_queue)

        if current_cost > dist[current_hub]:
            continue  # stale entry, skip

        if current_hub == end:
            break

        for neighbor, max_limit in current_hub.conn.items():
            neighbor = graph.hubs[neighbor]

            if neighbor.zone == "blocked":
                continue

            if neighbor.zone == "restricted":
                move_cost = 2
            elif neighbor.zone == "priority":
                move_cost = 0.9
            else:
                move_cost = 1

            new_cost = current_cost + move_cost

            if new_cost < dist[neighbor]:
                prev[neighbor] = current_hub
                dist[neighbor] = new_cost
                counter += 1
                heapq.heappush(priority_queue, (new_cost, counter, neighbor))

    path: list[Hub] = []
    current: Optional[Hub] = end
    while current is not None:
        path.insert(0, current)
        current = prev[current]

    if path[0] != start:
        return None

    return path
