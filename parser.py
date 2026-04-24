
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

def parse(file_name: str):

    info = {"nb_drones": 0,
            "hubs": dict(),
            "connections": dict()}

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
                print("hh")
                hub_sp = sp[1].strip().split(" ")
                print(hub_sp)
                name = hub_sp[0]
                x = hub_sp[1]
                y = hub_sp[2]
                color = hub_sp[3].split("=")[1].replace("]", "")
                info["hubs"].update({name: (x, y, color)})

            if sp[0] == "connection":
                con_sp = sp[1].strip().split("-")
                info["connections"].update({con_sp[0]:con_sp[1]})

    return info

