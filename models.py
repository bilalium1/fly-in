from pydantic import BaseModel
from typing import Dict


class Hub(BaseModel):
    name: str
    x: int
    y: int
    zone: str
    max_drones: int
    conn: Dict[str, int]

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Hub):
            return NotImplemented
        return self.name == other.name


class Sim():
    """
    THIS IS THE MAIN CLASS THAT CONTROLS EVERYTHING WAA
    """
    def __init__(self, info):
        self.nb_drones = info["nb_drones"]
        self.hubs = {}
        self.drones = dict()
        self.turns = []
        # Each turn is an entry in which : (drone : Hub)

        for name, nfo in info["hubs"].items():
            # make dictionary of connections
            c = {}
            for con in info["connections"]:
                if con[0] == name:
                    c.update({con[1]: con[2]})

            # update dictionary of hub models
            self.hubs.update({name: Hub(
                name=name, x=nfo[0], y=nfo[1],
                zone=nfo[2]["zone"],
                max_drones=nfo[2]["max_drones"], conn=c)})

        for i in range(info["nb_drones"]):
            self.drones.update({"d_" + str(i + 1): self.hubs["start"]})

        self.turns.append(self.drones)

        print(self.drones)
        print(self.turns)

    def move_drone(self, id: int, hub: str) -> tuple:
        # check if hub is in connections
        drone = self.drones.get("d_" + str(id), None)

        if drone.conn.get(hub, None) is not None:
            return ("d_" + str(id), self.hubs[hub])
