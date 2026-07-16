# Fly-in Drones

*This project has been created as part of the 42 curriculum by blemrabe.* -> that's me ;)

![tails_flying](misc/chrono.gif)

## Description
This project simulates a fleet of drones navigating through a network of hubs while optimizing the total number of turns required to reach their destinations.

The objective is to efficiently route multiple drones while minimizing congestion and improving overall performance through smart path distribution.

## Features
- Pathfinding using **Dijkstra’s algorithm**
- Dynamic distribution of drones across **multiple paths**
- **Blacklist system** for hubs and connections to force alternative routing
- Turn-based simulation engine
- Graphical visualization using **Pygame**
- UI design inspired by **Chrono Trigger**

## Algorithm & Strategy
The core of the project relies on **Dijkstra’s algorithm** to compute the shortest path between hubs.

However, using only the shortest path leads to congestion when multiple drones follow the same route. To solve this, a **blacklisting mechanism** is introduced:

- After assigning a path to a stack of drones, selected **hubs or connections are temporarily blacklisted**
- This prevents reuse of the same path in subsequent computations
- The algorithm is forced to explore **alternative routes**
- Each stack of drones is assigned a **different path**, improving parallelism

This approach reduces bottlenecks and significantly optimizes the **total number of turns** required.

## Visualization
The project includes a real-time graphical interface built with **Pygame**:
- Displays hubs and connections clearly
- Shows drone movement step-by-step
- Provides a turn-based visual simulation

The UI design is inspired by the classic game **Chrono Trigger**, focusing on a clean and retro aesthetic to enhance readability and user experience.

## Instructions

### Requirements
- Python 3.x
- Pygame

### Installation
```bash
make install
```
### Usage
```
make run
```
OR if you want to specify a file: 
```
python main.py <map_file>
```

### Performance

The implementation focuses on minimizing total turns by:

- Reducing congestion between drones
- Distributing drones across multiple optimized paths
- Forcing route diversity using the blacklist strategy

The solution aims to meet performance benchmarks defined in the subject for easy, medium, and hard maps.

### Resources
- Dijkstra’s Algorithm: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
- Pygame Documentation: https://www.pygame.org/docs/
- Chrono Trigger (UI inspiration)
Notes
- AI tools were used for brainstorming and structuring the documentation
- Core algorithm design, optimization strategy, and implementation were
- done manually

Thank you for reading!

![SONIC](misc/sonic_waiting.gif)

made by b11
