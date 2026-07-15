"""Turn-based multi-drone simulation engine."""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from dijkstra import assign_drones_to_paths, yen_k_shortest_paths
from models import Connection, Drone, Hub, Sim


@dataclass
class Move:
    """Represents a drone's intended or confirmed action for a turn."""

    status: str  # "move", "wait", "in_transit", "arriving"
    next_hub: Optional[Hub] = None
    connection: Optional[Connection] = None


def _drone_location(drone: Drone) -> str:
    """Return the hub or connection name the drone currently occupies."""
    if drone.current_zone is not None:
        return drone.current_zone.name
    if drone.current_connection is not None:
        return drone.current_connection.name
    return "?"


def all_delivered(drones: List[Drone]) -> bool:
    """Check if every drone has reached the end zone."""
    return all(drone.delivered for drone in drones)


def assign_paths(sim: Sim) -> bool:
    """Find up to k paths and distribute drones across them.

    Args:
        sim: The simulation graph.

    Returns:
        True if at least one valid path exists, False otherwise.
    """
    k = max(sim.nb_drones, 10)
    paths = yen_k_shortest_paths(sim, sim.start, sim.end, k)
    if not paths:
        return False
    assign_drones_to_paths(sim.drones, paths)
    return True


def run_simulation(sim: Sim) -> Tuple[List[str], int]:
    """Run the drone routing simulation turn by turn.

    Args:
        sim: The simulation graph with drones already assigned paths.

    Returns:
        A tuple (output_lines, total_turns) where output_lines contains
        one snapshot string per turn showing every drone's position.
    """
    drones = sim.drones

    for drone in drones:
        drone.current_zone = sim.start
        sim.start.current_drones.append(drone)

    simulation_output: List[str] = [
        " ".join(f"D{d.id}-{sim.start.name}" for d in drones)
    ]

    turn = 0

    while not all_delivered(drones) and turn < 10000:
        turn += 1

        # --- PHASE 1: Determine intended moves ---
        intended_moves: Dict[Drone, Move] = {}

        for drone in drones:
            if drone.delivered:
                continue

            if drone.turns_left_on_connection > 0:
                drone.turns_left_on_connection -= 1
                status = "arriving" if drone.turns_left_on_connection == 0 else "in_transit"
                intended_moves[drone] = Move(status)
                continue

            if drone.path_index + 1 >= len(drone.path):
                intended_moves[drone] = Move("wait")
                continue

            next_hub = drone.path[drone.path_index + 1]
            assert drone.current_zone is not None
            connection = sim.get_connection(drone.current_zone, next_hub)

            if connection is None:
                intended_moves[drone] = Move("wait")
                continue

            intended_moves[drone] = Move("move", next_hub, connection)

        # --- PHASE 2: Count outgoing drones per zone ---
        outgoing_counts: Dict[str, int] = defaultdict(int)
        for drone, move in intended_moves.items():
            if move.status == "move" and drone.current_zone is not None:
                outgoing_counts[drone.current_zone.name] += 1

        # --- PHASE 3: Validate each move against capacity ---
        confirmed_moves: Dict[Drone, Move] = {}
        running_zone: Dict[str, int] = defaultdict(int)
        running_conn: Dict[str, int] = defaultdict(int)

        for drone, move in intended_moves.items():
            if move.status != "move":
                confirmed_moves[drone] = move
                continue

            assert move.next_hub is not None
            assert move.connection is not None
            next_hub = move.next_hub
            connection = move.connection

            zone_cap = (
                next_hub.max_drones
                - len(next_hub.current_drones)
                + outgoing_counts[next_hub.name]
            )
            if next_hub.name in (sim.end.name, sim.start.name):
                zone_cap = max(zone_cap, sim.nb_drones)

            conn_cap = (
                connection.max_link_capacity
                - len(connection.current_drones_in_transit)
            )

            if running_zone[next_hub.name] + 1 <= zone_cap \
                    and running_conn[connection.name] + 1 <= conn_cap:
                confirmed_moves[drone] = move
                running_zone[next_hub.name] += 1
                running_conn[connection.name] += 1
            else:
                confirmed_moves[drone] = Move("wait")

        # --- PHASE 4: Apply confirmed moves ---
        for drone in drones:
            conf_move = confirmed_moves.get(drone)
            if conf_move is None or conf_move.status != "move":
                continue

            assert conf_move.next_hub is not None
            assert conf_move.connection is not None
            next_hub = conf_move.next_hub
            connection = conf_move.connection

            if drone.current_zone is not None:
                drone.current_zone.current_drones.remove(drone)

            if next_hub.zone == "restricted":
                connection.current_drones_in_transit.append(drone)
                drone.current_connection = connection
                drone.current_zone = None
                drone.turns_left_on_connection = 1
            else:
                next_hub.current_drones.append(drone)
                drone.current_zone = next_hub
                drone.path_index += 1
                if next_hub.name == sim.end.name:
                    drone.delivered = True

        # --- PHASE 5: Complete restricted zone arrivals ---
        for drone in drones:
            conf_move = confirmed_moves.get(drone)
            if conf_move is None or conf_move.status != "arriving":
                continue

            conn = drone.current_connection
            if conn is None:
                continue

            if drone.path_index + 1 >= len(drone.path):
                continue

            arrival_hub = drone.path[drone.path_index + 1]

            conn.current_drones_in_transit.remove(drone)
            drone.current_connection = None
            arrival_hub.current_drones.append(drone)
            drone.current_zone = arrival_hub
            drone.path_index += 1

            if arrival_hub.name == sim.end.name:
                drone.delivered = True

        simulation_output.append(
            " ".join(f"D{drone.id}-{_drone_location(drone)}" for drone in drones)
        )

    return simulation_output, turn
