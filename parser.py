
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

zones = [
    "normal",
    "blocked",
    "restricted",
    "priority"
]

def parse(file_name: str):

    info = {"nb_drones": 0,
            "hubs": dict(),
            "connections": []}

    with open(file_name, "r") as f:
        lines = f.readlines()
        for l in lines:
            print("line: ", l, end="")

            if l.startswith("#") or l.startswith("\n"):
                continue

            sp = l.split(":")
            if len(sp) != 2:
                continue

            if sp[0] not in ["nb_drones", "hub", "end_hub", "start_hub", "connection"]:
                continue

            if sp[0] == "nb_drones":
                info["nb_drones"] = int(sp[1])

            if sp[0].endswith("hub"):
                hub_sp = sp[1].strip().split(" ", 3)
                print(hub_sp)
                name = hub_sp[0]
                x = int(hub_sp[1])
                y = int(hub_sp[2])

                meta = {"color": 'grey', "zone": "normal", "max_drones": 1}
                meta_sp = hub_sp[3].strip("[]").split(" ")
                print(meta_sp)
                for m in meta_sp:
                    m_sp = m.split("=")
                    print(m_sp)
                    if m_sp[0] == "color":
                        meta.update({"color": m_sp[1]})
                    elif m_sp[0] == "zone":
                        if m_sp[1] not in zones:
                            m_sp[1] = "normal"
                        meta.update({"zone": m_sp[1]})
                    elif m_sp[0] == "max_drones":
                        print("HAAAA: ", m_sp[1])
                        meta.update({"max_drones": int(m_sp[1])})

                info["hubs"].update({name: (x, y, meta)})

            if sp[0] == "connection":
                con_sp = sp[1].strip().split(" ")[0].split('-')
                info["connections"].append((con_sp[0], con_sp[1]))

    return info

