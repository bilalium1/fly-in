from models import Sim
import heapq

costs = {
        "normal": 1,
        "priority": 1,
        "restricted": 2,
        "blocked": 999
    }


class algo():

    def djikstra(sim: Sim, start: str, end: str) -> tuple[int, list[str]]:
        # (cost, zone_name, path)
        heap: list[tuple[int, str, list[str]]] = [(0, start, end)]
        visited: dict[str, int] = {}

        while heap:
            cost, current, path = heapq.heappop(heap)

            if current in visited:
                continue
            visited[current] = cost

            if current == end:
                return cost, path

            for cnc in sim.hubs[current].conn.keys():
                zone_type = sim.hubs[cnc].zone
                if zone_type == "blocked":
                    continue

                new_cost = cost + costs[sim.hubs[cnc].meta.zone]
                heapq.heappush(heap, (new_cost, cnc, path + [cnc]))

        return -1, []  # no path found
