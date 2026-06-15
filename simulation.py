"""Turn-based multi-drone simulation engine."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from dijkstra import dijkstra
from models import Connection, Drone, Hub, Sim


@dataclass
class Move:
    """Represents a drone's intended or confirmed action for a turn."""

    status: str  # "move", "wait", "in_transit", "arriving"
    next_hub: Optional[Hub] = None
    connection: Optional[Connection] = None


def _drone_location(drone: Drone) -> str:
    """Return the current location label for a drone.

    Returns the zone name the drone currently occupies, or the
    connection name if the drone is mid-transit toward a restricted
    zone.

    Args:
        drone: The drone to describe.

    Returns:
        A zone or connection name string.
    """
    if drone.current_zone is not None:
        return drone.current_zone.name
    if drone.current_connection is not None:
        return drone.current_connection.name
    return "?"


def all_delivered(drones: List[Drone]) -> bool:
    """Check if every drone has reached the end zone."""
    return all(drone.delivered for drone in drones)


def assign_paths(sim: Sim) -> bool:
    """Compute and assign a Dijkstra path to every drone.

    Each drone independently computes the shortest path from start to
    end (all drones use the same shortest path, since the graph is
    static — this is the simplest valid strategy and is recomputed per
    drone to satisfy the "each drone uses Dijkstra" requirement).

    Args:
        sim: The simulation graph.

    Returns:
        True if every drone got a valid path, False if no path exists.
    """
    for drone in sim.drones:
        path = dijkstra(sim, sim.start, sim.end)
        if path is None:
            return False
        drone.path = path
        drone.path_index = 0
    return True


def run_simulation(sim: Sim) -> Tuple[List[str], int]:
    """Run the drone routing simulation turn by turn.

    Args:
        sim: The simulation graph, with drones already assigned paths.

    Returns:
        A tuple (output_lines, total_turns), where output_lines
        contains one string per turn describing all movements.
    """
    drones = sim.drones

    # Place all drones at start
    for drone in drones:
        drone.current_zone = sim.start
        sim.start.current_drones.append(drone)

    simulation_output: List[str] = []

    # Initial placement: all drones begin at the start zone.
    initial_line = " ".join(f"D{drone.id}-{sim.start.name}" for drone in drones)
    if initial_line:
        simulation_output.append(initial_line)

    turn = 0

    # Safety cap to avoid infinite loops on unsolvable maps.
    max_turns = 10000

    while not all_delivered(drones) and turn < max_turns:
        turn += 1

        # --- PHASE 1: Determine intended moves ---
        intended_moves: Dict[Drone, Move] = {}

        for drone in drones:
            if drone.delivered:
                continue

            # Drone is mid-transit on a restricted connection
            if drone.turns_left_on_connection > 0:
                drone.turns_left_on_connection -= 1
                if drone.turns_left_on_connection == 0:
                    intended_moves[drone] = Move("arriving")
                else:
                    intended_moves[drone] = Move("in_transit")
                continue

            # Drone has no more moves left on its path
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
        outgoing_counts: Dict[str, int] = {}
        for drone, move in intended_moves.items():
            if move.status == "move" and drone.current_zone is not None:
                zname = drone.current_zone.name
                outgoing_counts[zname] = outgoing_counts.get(zname, 0) + 1

        # --- PHASE 3: Validate each move, allow or force wait ---
        # Moves are validated against a running tally so that several
        # drones competing for the same destination/connection in a
        # single turn collectively respect capacity limits.
        confirmed_moves: Dict[Drone, Move] = {}
        running_zone: Dict[str, int] = {}
        running_conn: Dict[str, int] = {}

        for drone, move in intended_moves.items():
            if move.status != "move":
                confirmed_moves[drone] = move
                continue

            next_hub_opt = move.next_hub
            connection_opt = move.connection
            assert next_hub_opt is not None
            assert connection_opt is not None
            next_hub = next_hub_opt
            connection = connection_opt

            zone_cap = (
                next_hub.max_drones
                - len(next_hub.current_drones)
                + outgoing_counts.get(next_hub.name, 0)
            )
            # Start and end zones have no occupancy restriction.
            if next_hub.name in (sim.end.name, sim.start.name):
                zone_cap = max(zone_cap, sim.nb_drones)

            conn_cap = (
                connection.max_link_capacity
                - len(connection.current_drones_in_transit)
            )

            used_zone = running_zone.get(next_hub.name, 0)
            used_conn = running_conn.get(connection.name, 0)

            if used_zone + 1 <= zone_cap and used_conn + 1 <= conn_cap:
                confirmed_moves[drone] = move
                running_zone[next_hub.name] = used_zone + 1
                running_conn[connection.name] = used_conn + 1
            else:
                confirmed_moves[drone] = Move("wait")

        # --- PHASE 4: Apply confirmed moves ---
        for drone in drones:
            conf_move = confirmed_moves.get(drone)
            if conf_move is None or conf_move.status != "move":
                continue

            next_hub_opt = conf_move.next_hub
            connection_opt = conf_move.connection
            assert next_hub_opt is not None
            assert connection_opt is not None
            next_hub = next_hub_opt
            connection = connection_opt

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

            next_idx = drone.path_index + 1
            if next_idx >= len(drone.path):
                continue

            arrival_hub = drone.path[next_idx]

            conn.current_drones_in_transit.remove(drone)
            drone.current_connection = None
            arrival_hub.current_drones.append(drone)
            drone.current_zone = arrival_hub
            drone.path_index += 1

            if arrival_hub.name == sim.end.name:
                drone.delivered = True

        snapshot_line = " ".join(
            f"D{drone.id}-{_drone_location(drone)}" for drone in drones
        )
        simulation_output.append(snapshot_line)

    return simulation_output, turn
