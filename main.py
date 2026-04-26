from parser import parse
from visualizer.pygame_vis import viz

def main():

    print("\n[B//] WELCOME TO FLY-IN\n")
    print("[+//] RUNNING PARSING TEST...\n")
    info = parse("maps/easy/02_simple_fork.txt")

    print(info)
    viz(info)

    

if __name__ == "__main__":
    main()
