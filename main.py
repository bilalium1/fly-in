from parser import parse
from visualizer.pygame_vis import viz
from visualizer.menu_vis import menu_viz
from models import Sim
from my_djikstra import djikstra
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

    s = Sim(info)

    dj = djikstra(s, s.hubs["start"], s.hubs["goal"])

    print("path", dj)
    viz(info)


if __name__ == "__main__":
    main()
