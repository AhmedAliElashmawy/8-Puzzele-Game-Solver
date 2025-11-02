# 8-Puzzle Game Solver

A comprehensive 8-puzzle solver implementation featuring multiple search algorithms with detailed performance metrics including search depth analysis.

## Features

- **Multiple Search Algorithms**: BFS, DFS, IDS, A* (Manhattan & Euclidean)
- **Search Depth Tracking**: All algorithms compute and report search depth
- **Modular Design**: Each algorithm in a separate file for easy maintenance
- **Unified Interface**: Run and compare all algorithms simultaneously
- **GUI**: Interactive graphical interface for visual solving
- **Performance Metrics**: Track cost, depth, nodes expanded, and execution time
- **Results Export**: Save results to text files for analysis

## Project Structure

```
8-Puzzele-Game-Solver/
├── BFS.py                  # Breadth-First Search algorithm
├── DFS.py                  # Depth-First Search algorithm
├── IDS.py                  # Iterative Deepening Search algorithm
├── AStar.py                # A* Search with Manhattan & Euclidean heuristics
├── algorithm_interface.py  # Unified interface to run all algorithms
├── puzzle_gui.py          # PyQt6 graphical user interface
├── puzzle_solver.py       # Wrapper functions for GUI integration
├── interface.py           # Legacy interface file
├── results/               # Directory for saved algorithm results
└── saved_states/          # Directory for saved puzzle states
```

## Installation

### Prerequisites

- Python 3.7 or higher
- PyQt6 (for GUI only)

### Setup

```bash
# Clone the repository
git clone https://github.com/AhmedAliElashmawy/8-Puzzele-Game-Solver.git
cd 8-Puzzele-Game-Solver

# Install dependencies (for GUI)
pip install PyQt6
```

## Usage

### Command-Line Interface

Run all algorithms and compare their performance:

```bash
python3 algorithm_interface.py
```

This will:
- Run all algorithms on example puzzles
- Display detailed results including search depth
- Save results to the `results/` directory
- Provide an interactive mode for custom puzzles

### Run Individual Algorithms

```bash
# Test BFS
python3 BFS.py

# Test DFS
python3 DFS.py

# Test IDS
python3 IDS.py

# Test A*
python3 AStar.py
```

### Graphical User Interface

```bash
python3 puzzle_gui.py
```

## Algorithms Overview

### Breadth-First Search (BFS)
- **Completeness**: Yes
- **Optimality**: Yes (for uniform cost)
- **Time Complexity**: O(b^d)
- **Space Complexity**: O(b^d)
- **Best For**: Finding shortest paths in unweighted graphs

### Depth-First Search (DFS)
- **Completeness**: No (with cycle detection)
- **Optimality**: No
- **Time Complexity**: O(b^m)
- **Space Complexity**: O(bm)
- **Best For**: Memory-constrained scenarios
- **Note**: Uses depth limit to prevent infinite loops

### Iterative Deepening Search (IDS)
- **Completeness**: Yes
- **Optimality**: Yes
- **Time Complexity**: O(b^d)
- **Space Complexity**: O(bd)
- **Best For**: Combining BFS optimality with DFS space efficiency

### A* Search
- **Completeness**: Yes (with admissible heuristic)
- **Optimality**: Yes (with admissible heuristic)
- **Time Complexity**: O(b^d)
- **Space Complexity**: O(b^d)
- **Best For**: Optimal pathfinding with domain knowledge

#### Heuristics:
- **Manhattan Distance**: Sum of distances of tiles from goal positions
- **Euclidean Distance**: Straight-line distance of tiles from goal positions

## Performance Metrics

All algorithms return detailed metrics:

- **Cost**: Number of moves to reach the goal
- **Depth**: Solution depth (same as cost for this problem)
- **Search Depth**: Maximum depth explored during search
- **Nodes Expanded**: Number of states explored
- **Time**: Execution time in appropriate units (μs, ms, s)
- **Path**: Complete solution path from start to goal

## Example Output

```
======================================================================
Algorithm: BFS
======================================================================
✅ Solution found!
Solution Cost (moves): 8
Solution Depth: 8
Search Depth: 8
Nodes Expanded: 188
Time: 355.48 μs
Path Length: 9 states

======================================================================
                    COMPARISON SUMMARY
======================================================================
Algorithm            Cost     Depth    Search Depth    Nodes        Time           
----------------------------------------------------------------------
BFS                  8        8        8               188          355.48 μs      
DFS                  50       50       50              8090         11.80 ms       
IDS                  8        8        8               443          498.77 μs      
A* (Manhattan)       8        8        8               11           79.63 μs       
A* (Euclidean)       8        8        8               11           81.78 μs       
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Author

Ahmed Ali Elashmawy
