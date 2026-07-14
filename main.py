"""Entry point for the Fly-in drone routing simulation."""

import sys

import pygame

from models import Sim
from parser import parse
from simulation import assign_paths, run_simulation
from visualizer.menu_vis import MenuViz
from visualizer.sim_vis import SimVis


def run_map(file_name: str) -> str:
    """Parse, simulate and visualise one map.

    Args:
        file_name: Path to the map file.

    Returns:
        "menu" to go back to the map selector, "quit" to exit.
    """
    info = parse(file_name)
    if info is None:
        print("[x//] Failed to parse map.")
        return "menu"

    sim = Sim(info)

    if not assign_paths(sim):
        print("[x//] No path found from start to end.")
        return "menu"

    output, total_turns = run_simulation(sim)

    for line in output:
        print(line)
    print(f"\nTotal turns: {total_turns}")

    sim_visual = SimVis(info, output)
    return sim_visual.run()


def main() -> None:
    """Run the simulation, looping back to menu until the user quits."""

    print("\n[B//] WELCOME TO FLY-IN\n")

    # Handle a map passed directly on the command line (skip menu).
    if len(sys.argv) == 2:
        pygame.init()
        result = run_map(sys.argv[1])
        if result != "menu":
            pygame.quit()
            return
        # Fall through to the menu loop if the user pressed BACKSPACE.

    elif len(sys.argv) > 2:
        print("Usage: python main.py [map_file]")
        return

    # Main application loop: menu → simulation → menu → ...
    pygame.init()
    while True:
        menu = MenuViz()
        file_name = menu.run()

        if not file_name:
            # User pressed Q / closed the window.
            break

        result = run_map(file_name)

        if result == "quit":
            break
        # result == "menu": loop back and show the menu again.

    pygame.quit()


if __name__ == "__main__":
    main()
