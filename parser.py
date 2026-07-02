"""Parser for the Fly-in map file format."""

from typing import Any, Dict, List, Optional, Tuple

ZONES = ["normal", "blocked", "restricted", "priority"]
COLORS = {
    "grey",
    "gray",
    "red",
    "green",
    "blue",
    "yellow",
    "black",
    "white",
    "orange",
    "purple",
    "cyan",
    "magenta",
    "rainbow",
}


def parse(file_name: str) -> Optional[Dict[str, Any]]:
    """Parse a Fly-in map file.

    Args:
        file_name: Path to the map file.

    Returns:
        A dict describing the simulation, or None on error.
    """
    info: Dict[str, Any] = {
        "nb_drones": 0,
        "hubs": {},
        "connections": [],
        "start": None,
        "end": None,
        "map_path": file_name,
    }

    try:
        with open(file_name, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as exc:
        print(f"Error opening file: {exc}")
        return None

    for i, line in enumerate(lines):
        try:
            stripped = line.strip()
            if stripped.startswith("#") or stripped == "":
                continue

            sp = stripped.split(":", 1)
            if len(sp) != 2:
                raise ValueError("Invalid Entry")

            key = sp[0].strip()
            keys = ["nb_drones", "hub", "end_hub", "start_hub", "connection"]
            if key not in keys:
                raise ValueError(f"Invalid entry ({key})")

            if key == "nb_drones":
                _parse_nb_drones(info, sp[1])
                continue

            if key.endswith("hub"):
                _parse_hub(info, key, sp[1])
                continue

            if key == "connection":
                _parse_connection(info, sp[1])
                continue

        except Exception as exc:
            print(f"Error on line {i + 1} : {exc}")
            return None

    if info["start"] is None or info["end"] is None:
        print("Error: missing start_hub or end_hub")
        return None

    return info


def _parse_nb_drones(info: Dict[str, Any], value: str) -> None:
    """Parse and validate the nb_drones field."""
    n = int(value.strip())
    if n < 1:
        raise ValueError("Invalid Number of Drones")
    if len(info["hubs"]) > 0 or len(info["connections"]) > 0:
        raise ValueError("nb_drones MUST be the first.")
    info["nb_drones"] = n


def _parse_hub(info: Dict[str, Any], key: str, value: str) -> None:
    """Parse a hub/start_hub/end_hub line."""
    hub_sp = value.strip().split(" ", 3)
    if len(hub_sp) < 3:
        raise ValueError("Invalid Hub Data")

    name = hub_sp[0]
    if "-" in name or " " in name:
        raise ValueError(f"Invalid characters in name: {name}")

    if name in info["hubs"]:
        raise ValueError(f"Duplicate Hubs detected: {name}")

    x = int(hub_sp[1])
    y = int(hub_sp[2])

    for hub_info in info["hubs"].values():
        if hub_info["x"] == x and hub_info["y"] == y:
            raise ValueError(f"Hubs with the same position: {name} {x} {y}")

    meta = {"color": "grey", "zone": "normal", "max_drones": 1}
    if len(hub_sp) == 4:
        meta_str = hub_sp[3].strip()
        if not (meta_str.startswith("[") and meta_str.endswith("]")):
            raise ValueError(f"Invalid Hub Metadata: {meta_str}")
        meta_sp = meta_str.strip("[]").split(" ")
        for m in meta_sp:
            if m == "":
                continue
            m_sp = m.split("=")
            if len(m_sp) != 2:
                raise ValueError(f"Invalid Metadata token: {m}")
            mk, mv = m_sp[0], m_sp[1]
            if mk not in ("color", "zone", "max_drones"):
                raise ValueError(f"Invalid Metadata: {mk}")
            if mk == "color":
                meta["color"] = mv
            elif mk == "zone":
                if mv not in ZONES:
                    raise ValueError(f"Invalid Zone Type {mv}")
                meta["zone"] = mv
            elif mk == "max_drones":
                mdv = int(mv)
                if mdv < 1:
                    raise ValueError("Invalid Max Drones (Greater than 1)")
                meta["max_drones"] = mdv

    info["hubs"][name] = {"name": name, "x": x, "y": y, **meta}

    if key == "start_hub":
        if info["start"] is not None:
            raise ValueError("Multiple start_hub entries")
        info["start"] = name
    elif key == "end_hub":
        if info["end"] is not None:
            raise ValueError("Multiple end_hub entries")
        info["end"] = name


def _parse_connection(info: Dict[str, Any], value: str) -> None:
    """Parse a connection line."""
    cn_sp = value.strip().split(" ")
    if len(cn_sp) < 1 or len(cn_sp) > 2:
        raise ValueError("Invalid Connection")

    con_sp = cn_sp[0].split("-")
    if len(con_sp) != 2:
        raise ValueError("Invalid Connection")

    a, b = con_sp[0], con_sp[1]

    if a not in info["hubs"] or b not in info["hubs"]:
        raise ValueError("Connected Hub doesn't exist")

    max_link = 1
    if len(cn_sp) == 2:
        meta_str = cn_sp[1].strip()
        if not (meta_str.startswith("[") and meta_str.endswith("]")):
            raise ValueError(f"Invalid Connection Metadata: {meta_str}")
        meta_sp = meta_str.strip("[]").split(" ")
        for m in meta_sp:
            if m == "":
                continue
            m_sp = m.split("=")
            if len(m_sp) != 2 or m_sp[0] != "max_link_capacity":
                raise ValueError(f"Invalid Connection Metadata: {m}")
            max_link = int(m_sp[1])
            if max_link < 1:
                raise ValueError("Invalid max_link_capacity")

    existing: List[Tuple[str, str, int]] = info["connections"]
    for ea, eb, _ in existing:
        if {ea, eb} == {a, b}:
            raise ValueError("Duplicate connection")

    info["connections"].append((a, b, max_link))
