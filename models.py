from pydantic import BaseModel
from typing import List

class Sim():
    def __init__(self, info):
        self.nb_drones = info["nb_drones"]
        self.hubs = info["hubs"]
        self.cons = info["connections"]
        self.drones = []
        self.turns = dict()
        # Each turn is an entry in which : (drone : Hub)

class Drone():
    def __init__(self, start_hub : Hub):
        self.moves = 0
        self.hub = start_hub


class Hub():
    def __init__(self, name: str, zone: str, md : int):
        self.name = name
        self.zone = zone
        self.max_drones = md
        self.connections = []
        self.drones = []

