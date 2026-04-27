from parser import parse
from visualizer.pygame_vis import viz
from visualizer.menu_vis import menu_viz

maps = [
    "maps/easy/01"
]

def main():

    print("\n[B//] WELCOME TO FLY-IN\n")
    print("[+//] RUNNING PARSING TEST...\n")
    map = menu_viz()
    info = parse(map)
    viz(info)
    print(info)

    

if __name__ == "__main__":
    main()
