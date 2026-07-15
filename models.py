"""Domain models for the Fly-in simulation."""

from typing import Any, Dict, List, Optional, Tuple

ZONE_COST = {
    "normal": 1,
    "priority": 1,
    "restricted": 2,
    "blocked": 999,
}


class Connection:
    """A bidirectional connection (edge) between two hubs."""

    def __init__(
        self, name: str, hub_a: str, hub_b: str, max_link_capacity: int = 1
    ) -> None:
        """Initialize a connection.

        Args:
            name: Unique connection name (e.g. "a-b").
            hub_a: Name of the first hub.
            hub_b: Name of the second hub.
            max_link_capacity: Max drones allowed in transit simultaneously.
        """
        self.name = name
        self.hub_a = hub_a
        self.hub_b = hub_b
        self.max_link_capacity = max_link_capacity
        self.current_drones_in_transit: List["Drone"] = []

    def other(self, hub_name: str) -> str:
        """Return the hub on the other end of the connection."""
        if hub_name == self.hub_a:
            return self.hub_b
        return self.hub_a

    def __repr__(self) -> str:
        return f"Connection({self.name})"


class Hub:
    """A zone/hub in the network."""

    def __init__(
        self, name: str, x: int, y: int, zone: str, max_drones: int,
        color: str = "grey"
    ) -> None:
        """Initialize a hub.

        Args:
            name: Unique hub name.
            x: X coordinate.
            y: Y coordinate.
            zone: Zone type (normal, blocked, restricted, priority).
            max_drones: Maximum drones allowed simultaneously.
            color: Display color.
        """
        self.name = name
        self.x = x
        self.y = y
        self.zone = zone
        self.max_drones = max_drones
        self.color = color
        self.conn: Dict[str, str] = {}  # neighbor_name -> connection_name
        self.current_drones: List["Drone"] = []

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Hub):
            return NotImplemented
        return self.name == other.name

    def __lt__(self, other: "Hub") -> bool:
        return self.name < other.name


class Drone:
    """A drone moving through the network."""

    def __init__(self, drone_id: int, start: Hub) -> None:
        """Initialize a drone at the start hub.

        Args:
            drone_id: Numeric identifier (used as D<id>).
            start: The starting hub.
        """
        self.id = drone_id
        self.current_zone: Optional[Hub] = start
        self.current_connection: Optional[Connection] = None
        self.path: List[Hub] = []
        self.path_index: int = 0
        self.conn_turns: int = 0
        self.delivered: bool = False


class Sim:
    """Holds the full simulation graph state."""

    def __init__(self, info: Dict[str, Any]) -> None:
        """Build the simulation graph from parsed map info.

        Args:
            info: Dict produced by parser.parse().
        """
        self.nb_drones: int = info["nb_drones"]
        self.start_name: str = info["start"]
        self.end_name: str = info["end"]
        self.hubs: Dict[str, Hub] = {}
        self.connections: Dict[str, Connection] = {}
        self.drones: List[Drone] = []

        for name, nfo in info["hubs"].items():
            self.hubs[name] = Hub(
                name=name,
                x=nfo["x"],
                y=nfo["y"],
                zone=nfo["zone"],
                max_drones=nfo["max_drones"],
                color=nfo.get("color", "grey"),
            )

        for a, b, max_link in info["connections"]:
            conn_name = f"{a}-{b}"
            conn = Connection(conn_name, a, b, max_link)
            self.connections[conn_name] = conn
            self.hubs[a].conn[b] = conn_name
            self.hubs[b].conn[a] = conn_name

        self.start: Hub = self.hubs[self.start_name]
        self.end: Hub = self.hubs[self.end_name]

        for i in range(self.nb_drones):
            self.drones.append(Drone(i + 1, self.start))

    def get_connection(self, hub_a: Hub, hub_b: Hub) -> Optional[Connection]:
        """Return the connection between two hubs, if any."""
        name = hub_a.conn.get(hub_b.name)
        if name is None:
            return None
        return self.connections[name]

    def movement_cost(self, hub: Hub) -> int:
        """Return the turn cost to move into the given hub."""
        return ZONE_COST.get(hub.zone, 999)

    def neighbors(self, hub: Hub) -> List[Tuple[Hub, Connection]]:
        """Return list of (neighbor_hub, connection) pairs for a hub."""
        result = []
        for neighbor_name, conn_name in hub.conn.items():
            result.append(
                (self.hubs[neighbor_name], self.connections[conn_name]))
        return result
