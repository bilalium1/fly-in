"""Entry point for the Fly-in drone routing simulation."""

import sys

from models import Sim
from parser import parse
from simulation import assign_paths, run_simulation

from visualizer.menu_vis import menu_viz
from visualizer.pygame_vis import viz

def main() -> None:
    """Run the simulation on the map given as a command-line argument."""
    file_name = ""
    if len(sys.argv) == 1:
        file_name = menu_viz()
        print("Map Assigned : ", file_name)
    elif len(sys.argv) == 2:
        file_name = sys.argv[1]
    else:
        print("Invalid Arguments.")
        return

    info = parse(file_name)
    if info is None:
        print("[x//] Failed to parse map.")
        return

    sim = Sim(info)

    if not assign_paths(sim):
        print("[x//] No path found from start to end.")
        return

    output, total_turns = run_simulation(sim)

    print(info)

    viz(info, output)

    for line in output:
        print(line)

    print(f"\nTotal turns: {total_turns}")


if __name__ == "__main__":
    main()
