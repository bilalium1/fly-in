from parser import parse
from visualizer.pygame_vis import viz
from visualizer.menu_vis import menu_viz
from models.drones import Drone

maps = [
    "maps/easy/01"
]

def main():

    print("\n[B//] WELCOME TO FLY-IN\n")
    print("[+//] RUNNING PARSING TEST...\n")
    map = menu_viz()
    if map is None:
        print("[x//] No file was chosen.")
        return
    info = parse(map)

    drones = []
    for i in range(info["nb_drones"]):
        drones.append(Drone(info["hubs"]["start"]))

    print("drones : ", drones)
    viz(info)

if __name__ == "__main__":
    main()
