
# this is for parsing the map files:

# Easy Level 1: Simple linear path
# nb_drones: 2
# 
# start_hub: start 0 0 [color=green]
# hub: waypoint1 1 0 [color=blue]
# hub: waypoint2 2 0 [color=blue]
# end_hub: goal 3 0 [color=red]
# 
# connection: start-waypoint1
# connection: waypoint1-waypoint2
# connection: waypoint2-goal

# normal: 1 turn (default)
# restricted: 2 turns
# priority: 1 turn (but should be preferred in pathfinding algorithms)
# blocked: Inaccessible — cannot be entered

zones = [
    "normal",
    "blocked",
    "restricted",
    "priority"
]

def parse(file_name: str):

    info = {"nb_drones": 0,
            "hubs": dict(),
            "connections": [],
            "map_path": file_name}

    with open(file_name, "r") as f:
        lines = f.readlines()
        for i, l in enumerate(lines):
            try:
                if l.startswith("#") or l.strip() == "":
                    continue

                sp = l.split(":")
                if len(sp) != 2:
                    raise ValueError("Invalid colon Identation")
                    continue

                if sp[0] not in ["nb_drones", "hub", "end_hub", "start_hub", "connection"]:
                    raise ValueError("Invalid entry (", sp[0], ")")
                    continue

                if sp[0] == "nb_drones":
                    info["nb_drones"] = int(sp[1])
                    if int(sp[1]) < 1:
                        raise ValueError("Invalid Number of Drones ( At least 1 Drone )")

                if sp[0].endswith("hub"):
                    hub_sp = sp[1].strip().split(" ", 3)
                    if len(hub_sp) != 4:
                        raise ValueError("Invalid Hub Data")
                    name = hub_sp[0]
                    if " " in name or "-" in name:
                        raise ValueError("Invalid characters in name")
                    x = int(hub_sp[1])
                    y = int(hub_sp[2])
                    if x < 0 or y < 0:
                        raise ValueError("Negative Coodinates.")

                    meta = {"color": 'grey', "zone": "normal", "max_drones": 1}
                    meta_sp = hub_sp[3].strip("[]").split(" ")
                    for m in meta_sp:
                        m_sp = m.split("=")
                        if m_sp[0] not in ["color", "zone", "max_drones"]:
                            raise ValueError("Invalid Metadata:", m_sp[0])
                        if m_sp[0] == "color":
                            meta.update({"color": m_sp[1]})
                        elif m_sp[0] == "zone":
                            if m_sp[1] not in zones:
                                raise ValueError("Invalid Zone Type", m_sp[1])
                            meta.update({"zone": m_sp[1]})
                        elif m_sp[0] == "max_drones":
                            meta.update({"max_drones": int(m_sp[1])})
                            if int(m_sp[1]) < 1:
                                raise ValueError("Invalid Max Drones (Greater than 1)")

                    info["hubs"].update({name: (x, y, meta)})

                if sp[0] == "connection":
                    con_sp = sp[1].strip().split(" ")[0].split('-')
                    if len(con_sp) != 2:
                        raise ValueError("Invalid Connection")
                    info["connections"].append((con_sp[0], con_sp[1]))
            except Exception as e:
                print(f"Error on line {i + 1} :", e)
                return None

    return info

