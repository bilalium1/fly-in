from parser import parse
from visualizer.pygame_vis import viz
from visualizer.menu_vis import menu_viz
from models.drones import Drone
import sys

def main():

    print("\n[B//] WELCOME TO FLY-IN\n")
    print("[+//] RUNNING PARSING TEST...\n")
    if len(sys.argv) == 1:
        print("[+//] Opening Menu...")
        map = menu_viz()
        info = parse(map)
    elif len(sys.argv) == 2:
        print(f"[+//] Loading file : {sys.argv[1]}")
        info = parse(sys.argv[1])

    if info is None:
            print("[x//] No file was chosen.")
            return
    
    drones = []
    for i in range(info["nb_drones"]):
        drones.append(Drone(info["hubs"]["start"]))

    print("drones : ", drones)
    viz(info)

if __name__ == "__main__":
    main()
