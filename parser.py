from pygame.color import THECOLORS

zones = [
    "normal",
    "blocked",
    "restricted",
    "priority"
]


def parse(file_name: str):

    info = {"nb_drones": 0,
            "hubs": dict(),
            "connections": set(),
            "map_path": file_name}

    with open(file_name, "r") as f:
        lines = f.readlines()
        for i, l in enumerate(lines):
            try:
                # IGNORE HASHTAGS OR EMPTY LINES
                if l.startswith("#") or l.strip() == "":
                    continue

                # SPLIT LINE WITH ":"
                sp = l.split(":")
                if len(sp) != 2:
                    raise ValueError("Invalid Entry")
                    continue

                # CHECK KEY IS VALID
                keys = ["nb_drones",
                        "hub", "end_hub", "start_hub", "connection"]
                if sp[0] not in keys:
                    raise ValueError("Invalid entry (", sp[0], ")")
                    continue

                # LOG NUMBER OF DRONES
                if sp[0] == "nb_drones":
                    info["nb_drones"] = int(sp[1])
                    if int(sp[1]) < 1:
                        raise ValueError("Invalid Number of Drones")

                    # CHECK IF ITS THE FIRST ARG
                    if len(info["hubs"]) > 0 or len(info["connections"]) > 0:
                        raise ValueError("nb_drones MUST be the first.")

                # PARSE HUBS
                if sp[0].endswith("hub"):
                    hub_sp = sp[1].strip().split(" ", 3)
                    if len(hub_sp) != 4:
                        raise ValueError("Invalid Hub Data")
                    name = hub_sp[0]

                    # CHECK NAME VALIDITY
                    if not isinstance(name, str) or "-" in name:
                        raise ValueError("Invalid characters in name:", name)

                    # CHECK NAME IN DICT
                    if info["hubs"].get(name, None) is not None:
                        raise ValueError("Duplicate Hubs detected:", name)

                    x = int(hub_sp[1])
                    y = int(hub_sp[2])

                    for hub_info in info["hubs"].values():
                        if hub_info[0] == x and hub_info[1] == y:
                            raise ValueError(
                                "Hubs with the same position:", name, x, y)

                    if not (hub_sp[3].startswith("[") and
                            hub_sp[3].endswith("]")):
                        raise ValueError("Inavlid Hub Metadata:", hub_sp[3])

                    meta = {"color": 'grey', "zone": "normal", "max_drones": 1}
                    meta_sp = hub_sp[3].strip("[]").split(" ")
                    for m in meta_sp:
                        m_sp = m.split("=")
                        if m_sp[0] not in ["color", "zone", "max_drones"]:
                            raise ValueError("Invalid Metadata:", m_sp[0])
                        if m_sp[0] == "color":
                            clrs = set(THECOLORS.keys()).union({"rainbow"})
                            if m_sp[1] not in clrs:
                                raise ValueError(
                                    "Color doesn't exist:", m_sp[1])

                            meta.update({"color": m_sp[1]})
                        elif m_sp[0] == "zone":
                            if m_sp[1] not in zones:
                                raise ValueError("Invalid Zone Type", m_sp[1])
                            meta.update({"zone": m_sp[1]})
                        elif m_sp[0] == "max_drones":
                            meta.update({"max_drones": int(m_sp[1])})
                            if int(m_sp[1]) < 1:
                                raise ValueError(
                                    "Invalid Max Drones (Greater than 1)")

                    info["hubs"].update({name: (x, y, meta)})

                # PARSE CONNECTIONS
                if sp[0] == "connection":
                    cn_sp = sp[1].strip().split(" ")
                    if (len(cn_sp) < 1 or len(cn_sp) > 2):
                        raise ValueError("Invalid Connection")
                    con_sp = cn_sp[0].split('-')
                    if (len(cn_sp) == 2):
                        max_sp = cn_sp[1]
                        max_link = max_sp.split("=")[1].strip("]")
                    else:
                        max_link = 1
                    if len(con_sp) != 2:
                        raise ValueError("Invalid Connection")
                    if con_sp[0] not in info["hubs"].keys() or \
                            con_sp[1] not in info["hubs"].keys():
                        raise ValueError("Connected Hub doesn't exist")
                    info["connections"].add((con_sp[0], con_sp[1], max_link))
            except Exception as e:
                print(f"Error on line {i + 1} :", e)
                return None

    return info
